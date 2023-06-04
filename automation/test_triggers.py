import pytest

from automation.factories import TriggerEventFactory, AutomationCampaignFactoryWithSteps
from automation.models import AutomationCampaignContact
from contacts.factories import ContactFactory
from trackerapi.models import Event

@pytest.mark.django_db
def test_trigger_event(auth_client):
    contact = ContactFactory(workspace=auth_client.workspace)
    automation = AutomationCampaignFactoryWithSteps(trigger_type="EVENT", workspace=auth_client.workspace)
    trigger = TriggerEventFactory(
        name="Signed Up",
        with_attributes={"username": "virgin"},
        automation_campaign=automation,
        workspace=auth_client.workspace
    )
    automation.status = "ACTIVE"
    automation.save()

    # Send event that should trigger the automation
    event = Event.objects.create(
        name="Signed Up",
        triggered_by_contact=contact,
        attributes={"username": "virgin"},
        workspace=auth_client.workspace
    )

    a = AutomationCampaignContact.objects.all()
    assert automation.done_contacts.count() == 1
