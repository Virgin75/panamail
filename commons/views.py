import pickle

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, filters, exceptions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from commons.models import History, ExportHistory
from commons.paginations import x10ResultsPerPage
from commons.serializers import ExportHistorySerializer, HistorySerializer
from commons.tasks import generate_async_export
from users.models import Workspace

params = [
    OpenApiParameter(
        name='workspace_id',
        location=OpenApiParameter.QUERY,
        description='Used to filter based on a Workspace belonging.',
        required=True,
        type=str
    ),
]


@method_decorator(name="list", decorator=extend_schema(parameters=params))
class WorkspaceViewset(viewsets.ModelViewSet):
    """
    Viewset inherited by most of other views related to a Workspace.

    - Return a queryset of objects (depending on 'base_model_class') matching only the Workspace of request user.
    - Make sure Pagination is 10 results per page.
    - Implements default filter backends for ordering, search and filter.
    - Auto update edit_history table of related objects.
    """

    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend,)
    pagination_class = x10ResultsPerPage
    base_model_class = None
    parent_obj_type = None
    parent_obj_url_lookup = None
    diff_obj_in_post_request = None
    select_related_fields = ("workspace",)
    prefetch_related_fields = []

    def get_select_related_fields(self):
        """
        Allow to dynamically define the select_related fields to use in the View.
        (!) Mandatory to define at least 1 'select_related' field because 'workspace' FK is in all models.
        """
        assert self.select_related_fields is not None, (
                "'%s' should either include a `select_related_fields` attribute, "
                "or override the `get_select_related_fields()` method."
                % self.__class__.__name__
        )
        select_related_fields = self.select_related_fields
        return select_related_fields

    def get_prefetch_related_fields(self):
        """Allow to dynamically define the select_related fields to use in the View."""
        prefetch_related_fields = self.prefetch_related_fields
        return prefetch_related_fields

    def get_queryset(self, **kwargs):

        if self.action in ('list',):
            workspace_obj = Workspace.objects.get(id=self.request.GET.get('workspace_id'))
        else:
            # Retrieve, Update or Destroy actions
            custom_filters = {}
            specific_obj = self.diff_obj_in_post_request
            if specific_obj:
                custom_filters[f"{specific_obj}_id"] = self.kwargs.get("pk")
            else:
                custom_filters["id"] = self.kwargs.get("pk")
            base_obj = self.base_model_class.objects.get(**custom_filters)
            workspace_obj = Workspace.objects.get(id=base_obj.workspace_id)

        if not workspace_obj.members.filter(id=self.request.user.id).exists():
            raise exceptions.PermissionDenied()

        qs_filters = {
            "workspace": workspace_obj
        }
        if self.parent_obj_type and self.parent_obj_url_lookup:
            qs_filters[self.parent_obj_type] = self.kwargs.get(self.parent_obj_url_lookup)

        select_related_fields = self.get_select_related_fields()
        prefetch_related_fields = self.get_prefetch_related_fields()

        qs = (
            self.base_model_class.objects.filter(**qs_filters)
            .select_related(*select_related_fields)
            .prefetch_related(*prefetch_related_fields)
        )
        return qs

    def perform_update(self, serializer):
        serializer.validated_data.pop('workspace', None)
        self.get_object().edit_history.add(History.objects.create(edited_by=self.request.user))
        serializer.save()

    def perform_create(self, serializer):
        filter = {
            "created_by": self.request.user
        }
        if self.parent_obj_type and self.parent_obj_url_lookup:
            filter[self.parent_obj_type] = self.kwargs.get(self.parent_obj_url_lookup)
        workspace_obj = Workspace.objects.get(id=serializer.validated_data.get("workspace").id)
        if workspace_obj.members.filter(id=self.request.user.id).exists():
            serializer.save(**filter)
        else:
            raise exceptions.PermissionDenied()

    def get_object(self):
        if self.diff_obj_in_post_request:
            queryset = self.filter_queryset(self.get_queryset())
            obj = get_object_or_404(queryset, **{f"{self.diff_obj_in_post_request}_id": self.kwargs.get("pk")})
            self.check_object_permissions(self.request, obj)
            return obj
        else:
            return super().get_object()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ('list',):
            workspace_id = self.request.GET.get('workspace_id')
            context["workspace"] = workspace_id

        elif self.action in ('retrieve', 'update', 'partial_update', 'destroy',):
            workspace_id = self.get_object().workspace.id
            context["workspace"] = workspace_id

        elif self.action in ("create", "bulk_import", "set_custom_field_value"):
            workspace_id = self.request.data.get("workspace")
            context["workspace"] = workspace_id

        return context

    @action(detail=True, methods=['get'])
    def edit_history(self, request, *args, **kwargs):
        """
        Return a list of edits for a given object (paginated)
        """
        obj = self.get_object()
        page = self.paginate_queryset(obj.edit_history.all())
        serializer = HistorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ExportMixin(viewsets.GenericViewSet):
    export_serializer_class = None

    @action(detail=False, methods=['post'])
    def export(self, request, *args, **kwargs):
        """
        Mixin adding an .../export/ view to any objects.

        Export data from a given serializer (async Task).
        You must implement an "export_serializer_class" attribute in your viewset.
        """
        if not self.export_serializer_class:
            raise NotImplementedError("ExportMixin requires an 'export_serializer_class' attribute.")

        if not request.data.get("workspace", None):
            raise exceptions.ValidationError("Missing 'workspace' field.")

        queryset = self.filter_queryset(self.get_queryset())
        export_task = ExportHistory.objects.create(
            workspace=request.data.get("workspace"),
            query=pickle.dumps(queryset.query),
            export_serializer=pickle.dumps(self.export_serializer_class),
        )
        generate_async_export.delay(export_task.id)

        return Response({"status": "Your export is being generated."}, status=status.HTTP_202_ACCEPTED)


class ExportViewSet(WorkspaceViewset):
    """
    Viewset used to retrieve a list of export history and their related status.

      - GET: /api/commons/export-history/?workspace_id=XXX
    """
    base_model_class = ExportHistory
    serializer_class = ExportHistorySerializer
    search_fields = ("status",)
    ordering_fields = ("created_at",)
