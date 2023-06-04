from rest_framework import serializers

from automation.models import (
    AutomationCampaign,
    TriggerEvent,
    TriggerPage,
    TriggerList,
    TriggerSegment,
    StepWait,
    StepSendEmail, Step, TriggerEmail, TriggerTime,
)
from commons.serializers import WksFieldsSerializer, RestrictedPKRelatedField
from contacts.models import List, Segment
from contacts.serializers import MinimalListSerializer, MinimalSegmentSerializer
from emails.models import Email
from emails.serializers import EmailSerializer, MinimalEmailSerializer


class PolymorphicTriggerTypeField(serializers.Field):
    """
    Custom serializer field to return the right trigger content regarding the defined trigger_type.
    (!) Beware: Use only this Serializer field on 'AutomationCampaign' model read-only serializer.
    """

    def to_representation(self, value):
        match value.trigger_type:
            case 'EVENT':
                return TriggerEventSerializer(value.trigger).data
            case 'PAGE':
                return TriggerPageSerializer(value.trigger).data
            case 'EMAIL':
                return TriggerEmailSerializer(value.trigger).data
            case 'LIST':
                return TriggerListSerializer(value.trigger).data
            case 'SEGMENT':
                return TriggerSegmentSerializer(value.trigger).data
            case 'TIME':
                return TriggerTimeSerializer(value.trigger).data


class PolymorphicStepTypeField(serializers.Field):
    """
    Custom serializer field to return the right Step content regarding the defined step_type.
    (!) Beware: Use only this Serializer field on 'Step' model read-only serializer.
    """

    def to_representation(self, value):
        match value.step_type:
            case 'SEND_EMAIL':
                return StepSendEmailSerializer(value.content).data
            case 'WAIT':
                return StepWaitSerializer(value.content).data


class StepSendEmailSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a StepSendEmail."""

    step = RestrictedPKRelatedField(model=Step)
    email = RestrictedPKRelatedField(model=Email, read_serializer=EmailSerializer)

    class Meta:
        model = StepSendEmail
        fields = ('id', 'email', 'workspace', 'step')


class StepWaitSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a StepWait."""

    step = RestrictedPKRelatedField(model=Step)

    class Meta:
        model = StepWait
        fields = ('id', 'delay', 'delay_unit', 'workspace', 'step')


class TriggerEventSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerEvent."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)

    class Meta:
        model = TriggerEvent
        fields = ('id', 'name', 'with_attributes', 'workspace', 'automation_campaign')


class TriggerPageSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerPage."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)

    class Meta:
        model = TriggerPage
        fields = ('id', 'name', 'workspace', 'automation_campaign')


class TriggerListSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerList."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)
    list = RestrictedPKRelatedField(model=List, read_serializer=MinimalListSerializer)

    class Meta:
        model = TriggerList
        fields = ('id', 'list', 'workspace', 'automation_campaign')


class TriggerSegmentSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerSegment."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)
    segment = RestrictedPKRelatedField(model=Segment, read_serializer=MinimalSegmentSerializer)

    class Meta:
        model = TriggerSegment
        fields = ('id', 'segment', 'workspace', 'automation_campaign')


class TriggerEmailSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerEmail."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)
    email = RestrictedPKRelatedField(model=Email, read_serializer=MinimalEmailSerializer)

    class Meta:
        model = TriggerEmail
        fields = ('id', 'email', 'action', 'workspace', 'automation_campaign')


class TriggerTimeSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """Serialize for Read and Write on a TriggerTime."""

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)

    class Meta:
        model = TriggerTime
        fields = ('id', 'unit', 'value', 'workspace', 'automation_campaign')


class MinimalAutomationCampaignSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """
    Serializer used for 'list' and 'create' and 'update' action in AutomationCampaignViewSet.
    It returns only basic information about the automation campaign, not all the Steps.
    """

    class Meta:
        model = AutomationCampaign
        fields = ('id', 'name', 'description', 'status', 'trigger_type', 'is_repeated', 'total_contacts_now',
                  'total_contacts_past', 'created_at', 'created_by', 'workspace')
        read_only_fields = ('created_at', 'created_by', 'total_contacts_now', 'total_contacts_past')


class StepSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """
    Serializer used for read or write operations on a 'Step' model.
    It returns all information about the Step.
    """

    automation_campaign = RestrictedPKRelatedField(model=AutomationCampaign)
    content = PolymorphicStepTypeField(source='*', read_only=True)

    class Meta:
        model = Step
        fields = ('id', 'automation_campaign', 'order', 'step_type', 'content', 'created_at', 'created_by', 'workspace')
        read_only_fields = ('created_at', 'created_by', 'total_contacts_now', 'total_contacts_past', 'content')


class RetrieveAutomationCampaignSerializer(serializers.ModelSerializer, WksFieldsSerializer):
    """
    Serializer used for 'retrieve' action in AutomationCampaignViewSet.
    It returns all information about the automation campaign, including all Steps and trigger details.
    """

    steps = StepSerializer(many=True, read_only=True)
    trigger = PolymorphicTriggerTypeField(source='*')

    class Meta:
        model = AutomationCampaign
        fields = ('id', 'name', 'description', 'status', 'trigger_type', 'is_repeated', 'total_contacts_now',
                  'steps', 'trigger', 'total_contacts_past', 'created_at', 'created_by', 'workspace')
        read_only_fields = ('created_at', 'created_by', 'total_contacts_now', 'total_contacts_past')
