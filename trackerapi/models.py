import uuid

from django.db import models

from commons.models import BaseWorkspace
from contacts.models import Workspace, Contact
from users.models import CustomUser


class Page(BaseWorkspace):
    """
    Store Page views by Contact on client's website.

    Track Pages data are mostly used to generate dynamic Segments of Contacts.
    """

    url = models.CharField(max_length=200)  # Or screen name
    viewed_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='pages')

    def save(self, *args, **kwargs):
        """
        Override 'save()' to check if an existing AutomationCampaign trigger exists for this Page.

        If so, then add the Contact into the related Automation Campaign.
        """
        from automation.models import AutomationCampaign, AutomationCampaignContact

        automations = AutomationCampaign.objects.filter(
            page_trigger__name=self.url,
            page_trigger__workspace=self.workspace,
            status='ACTIVE'
        )
        if automations.exists():
            for automation in automations:
                process = AutomationCampaignContact.objects.create(
                    automation_campaign=automation,
                    contact=self.viewed_by_contact,
                    current_step=automation.steps.first(),
                    workspace=self.workspace,
                )
                process.async_execute_current_step()
        super().save(*args, **kwargs)


class Event(BaseWorkspace):
    """
    Store Events triggered by Contact on client's website.

    Track Pages data are mostly used to generate dynamic Segments of Contacts.
    """

    name = models.CharField(max_length=80)
    triggered_by_contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='events')
    attributes = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override 'save()' to check if an existing AutomationCampaign trigger exists for this Event.

        If so, then add the Contact into the related Automation Campaign.
        """
        from automation.models import AutomationCampaign, AutomationCampaignContact

        automations = AutomationCampaign.objects.filter(
            event_trigger__name=self.name,
            event_trigger__workspace=self.workspace,
            status='ACTIVE'
        )
        if automations.exists():
            for automation in automations:
                filters_attributes_checked = set()
                for k, v in automation.event_trigger.with_attributes.items():
                    if self.attributes.get(k) == v:
                        filters_attributes_checked.add(True)
                    else:
                        filters_attributes_checked.add(False)
                if len(filters_attributes_checked) == 1 and True in filters_attributes_checked:
                    process = AutomationCampaignContact.objects.create(
                        automation_campaign=automation,
                        contact=self.triggered_by_contact,
                        current_step=automation.steps.first(),
                        workspace=self.workspace,
                    )
                    process.async_execute_current_step()
        super().save(*args, **kwargs)


class TrackerAPIKey(BaseWorkspace):
    """
    Stores API keys related to a Workspace.

    Each Workspace can have many API keys. An API key is mandatory to send a
    Track Event or Track Page to the Tracker API.
    """

    class Meta:
        verbose_name_plural = "Tracker API keys"

    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='api_keys')
