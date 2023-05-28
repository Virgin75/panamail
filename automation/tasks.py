import logging

from django_rq import job

from automation.models import AutomationCampaignContact

logger = logging.getLogger(__name__)


@job
def process_automation_step(id):
    """
    Async task processing a single automation step.

    Parameters:
     - id (str/UUID): The id of the AutomationCampaignContact object.
    """
    task = AutomationCampaignContact.objects.get(id=id)

    if task.automation_campaign.status != "ACTIVE":
        logger.info(f"Automation campaign (id: {task.automation_campaign.id}) is not active. Returning...")
        return

    contact = task.contact
    current_step = task.current_step.content
    current_step_type = task.current_step.type

    match current_step_type:
        case "SEND_EMAIL":
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
