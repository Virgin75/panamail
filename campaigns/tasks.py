from panamail import celery_app
from celery.utils.log import get_task_logger
from .models import Campaign
from jinja2 import Template

logger = get_task_logger(__name__)

@celery_app.task(name="send_campaign")
def send_campaign(campaign_id):
    """Send a campaign immediately"""
    campaign = Campaign.objects.get(id=campaign_id)
    sender = campaign.sender.email_address
    reply_to = campaign.sender.reply_to
    subject = campaign.subject
    content = campaign.email_model.raw_html

    # Iterate over all recipients
    if campaign.to_type == 'LIST':
        list = campaign.to_list
        recipients = list.contacts.all()
        for recipient in recipients:
            email = recipient.email
            message = Template(content)
            print(message.render(email=email))

    if campaign.to_type == 'SEGMENT':
        segment = campaign.to_segment
        recipients = segment.members.all()
        for recipient in recipients:
            contact_custom_fields = recipient.custom_fields.select_related('custom_field').all()
            message = Template(content)
            print(message.render(email=email))

    campaign.status = 'SENT'
    campaign.save()
    logger.info(f"CAMPAIGN ID: {campaign_id}")
    return