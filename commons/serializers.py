from rest_framework import serializers

from commons.models import History
from users.serializers import MinimalUserSerializer


class HistorySerializer(serializers.ModelSerializer):
    edited_by = MinimalUserSerializer(read_only=True)

    class Meta:
        model = History
        fields = '__all__'
        read_only_fields = ['edited_at', 'edited_by']


class WksFieldsSerializer(serializers.Serializer):
    created_by = MinimalUserSerializer(read_only=True)
    edit_history = HistorySerializer(many=True, read_only=True)


class RestrictedPKRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.read_serializer = kwargs.pop('read_serializer', None)
        self.model = kwargs.pop('model', None)
        if self.read_serializer is not None and not issubclass(self.read_serializer, serializers.Serializer):
            raise TypeError('"read_serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.read_serializer else True

    def to_representation(self, instance):
        if self.read_serializer:
            return self.read_serializer(instance, context=self.context).data
        return super().to_representation(instance)

    def get_queryset(self):
        model = self.model
        workspace_id = self.context['workspace']
        queryset = model.objects.filter(workspace_id=workspace_id)
        return queryset
