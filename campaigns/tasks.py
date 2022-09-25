from panamail import celery_app
from celery.utils.log import get_task_logger
from .models import Campaign
from jinja2 import Template
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = get_task_logger(__name__)

#TODO: DO NOT SEND TO UNSUBS
#TODO: Define ConfigSet to track Emails actions
# Pass as tags in email : contact_id, campaign_id, email_id, workspace_id

def send_email_ses(**kwargs):
    client = boto3.client('ses',region_name=settings.AWS_REGION_NAME)
    #Send the email.
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    kwargs['recipient'],
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': kwargs['body'],
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': kwargs['body'],
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': kwargs['subject'],
                },
            },
            Source=f"{kwargs['sender_name']} <{kwargs['sender_email']}>",
            Tags=[
                {
                    'Name': 'workspace_id',
                    'Value': str(kwargs['workspace_id'])
                },
                {
                    'Name': 'contact_id',
                    'Value': str(kwargs['contact_id'])
                },
                {
                    'Name': 'campaign_id',
                    'Value': str(kwargs['campaign_id'])
                },
            ],
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def prep_email_sending(recipient, campaign):
    sender_email = campaign.sender.email_address
    sender_name = campaign.sender.name
    reply_to = campaign.sender.reply_to
    subject = campaign.subject
    content = campaign.email_model.raw_html

    recipient_cf = recipient.custom_fields.select_related('custom_field').all()
    recipient_fields = {}
    for cf in recipient_cf:
        recipient_fields[cf.custom_field.name] = cf.get_value()
    recipient_fields['email'] = recipient.email
    recipient_fields['created_at'] = recipient.created_at

    #Replace the varibales in the email content
    message = Template(content)
    content = message.render(contact=recipient_fields)

    #Send the email
    smtp = campaign.workspace.company.smtp
    if smtp == 'SES':
        send_email_ses(
            recipient=recipient.email, 
            subject=subject, 
            body=content, 
            sender_name=sender_name, 
            sender_email=sender_email,
            workspace_id=campaign.workspace.id,
            contact_id=recipient.id,
            campaign_id=campaign.id
        )
    print(content)


@celery_app.task(name="send_campaign")
def send_campaign(campaign_id):
    """Send a campaign immediately"""
    campaign = Campaign.objects.get(id=campaign_id)

    # Iterate over all recipients, prep email and send it!
    if campaign.to_type == 'LIST':
        list = campaign.to_list
        recipients = list.contacts.all()
        for recipient in recipients:
            prep_email_sending(recipient, campaign)

    if campaign.to_type == 'SEGMENT':
        segment = campaign.to_segment
        recipients = segment.members.all()
        for recipient in recipients:
            prep_email_sending(recipient, campaign)
            

    campaign.status = 'SENT'
    campaign.save()
    logger.info(f"CAMPAIGN ID: {campaign_id}")
    return