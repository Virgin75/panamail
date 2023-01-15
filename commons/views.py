from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, exceptions
from rest_framework.permissions import IsAuthenticated

from commons.paginations import x10ResultsPerPage
from commons.models import History
from users.models import Workspace


class WorkspaceViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend, )
    pagination_class = x10ResultsPerPage
    base_model_class = None
    select_related_fields = None
    prefetch_related_fields = ("edit_history",)

    def get_queryset(self):
        if self.action in ('list',):
            workspace_obj = Workspace.objects.get(id=self.request.GET.get('workspace_id'))
        else:
            base_obj = self.base_model_class.objects.get(id=self.kwargs.get("pk"))
            workspace_obj = Workspace.objects.get(id=base_obj.workspace_id)

        if not workspace_obj.members.filter(id=self.request.user.id).exists():
            raise exceptions.PermissionDenied()

        return (
            self.base_model_class.objects.filter(
                workspace=workspace_obj
            )
            .select_related(*self.select_related_fields)
            .prefetch_related(*self.prefetch_related_fields)
        )

    def perform_update(self, serializer):
        serializer.validated_data.pop('workspace', None)
        self.get_object().edit_history.add(History.objects.create(edited_by=self.request.user))
        serializer.save()

    def perform_create(self, serializer):
        workspace_obj = Workspace.objects.get(id=serializer.validated_data.get("workspace").id)
        if workspace_obj.members.filter(id=self.request.user.id).exists():
            serializer.save()
        else:
            raise exceptions.PermissionDenied()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ('list',):
            workspace_id = self.request.GET.get('workspace_id')
        elif self.action in ('retrieve', 'update', 'partial_update', 'destroy',):
            workspace_id = self.get_object().workspace.id
        elif self.action == "create":
            workspace_id = self.request.data.get("workspace")

        context["workspace"] = workspace_id
        return context
