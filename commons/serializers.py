from rest_framework import serializers


class RestrictedPKRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        model = self.context['view'].base_model_class
        workspace_id = self.context['workspace']
        queryset = model.objects.filter(workspace_id=workspace_id)
        return queryset
