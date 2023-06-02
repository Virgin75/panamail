import logging

from django_rq import job

from contacts.models import Contact

logger = logging.getLogger(__name__)


@job
def process_automation_step(id):
    """
    Async task processing a single automation step.

    Parameters:
     - id (str/UUID): The id of the AutomationCampaignContact object.
    """
    from automation.models import AutomationCampaignContact
    task = AutomationCampaignContact.objects.get(id=id)

    if task.automation_campaign.status != "ACTIVE":
        logger.info(f"Automation campaign (id: {task.automation_campaign.id}) is not active. Returning...")
        return

    contact = task.contact
    current_step = task.current_step.content
    current_step_type = task.current_step.type

    match current_step_type:
        case "SEND_EMAIL":
            # TODO: call a function to send email here and keep this task short and clean
            pass
        case "WAIT":
            pass

    if task.current_step.has_next_step:
        task.current_step = task.current_step.next_step
        task.save()
        task.async_execute_current_step()
        logger.info(f"Step has a next Step (id: {task.current_step.next_step.id})")
    else:
        task.automation_campaign.done_contacts.add(contact)
        task.delete()
        logger.info(f"No next Step. Exiting Contact from Automation Campaign (id: {task.automation_campaign.id})")


@job
def add_all_contacts_to_automation_campaign(id):
    """Async task adding all contacts to an automation campaign (used in 'TIME' trigger campaign)."""
    from automation.models import AutomationCampaign, AutomationCampaignContact

    automation = AutomationCampaign.objects.get(id=id)

    if automation.status != "ACTIVE":
        logger.info(f"Automation campaign (id: {automation.id}) is not active. Returning...")
        return

    for contact in Contact.objects.filter(workspace=automation.workspace):
        process = AutomationCampaignContact.objects.create(
            automation_campaign=automation,
            contact=contact,
            current_step=automation.steps.first(),
            workspace=automation.workspace,
        )
        process.async_execute_current_step()
        logger.info(f"Added contact (id: {contact.id}) to campaign (id: {automation.id})")
