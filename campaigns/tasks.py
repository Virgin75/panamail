from panamail import celery_app
from celery.utils.log import get_task_logger
from .models import Campaign
from jinja2 import Template
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = get_task_logger(__name__)

def send_email_ses(**kwargs):
    client = boto3.client('ses',region_name=settings.AWS_REGION_NAME)
    #Send the email.
    print(f"{kwargs['sender_name']} <{kwargs['sender_email']}>")
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
            Source=f"{kwargs['sender_name']} <{kwargs['sender_email']}>"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


@celery_app.task(name="send_campaign")
def send_campaign(campaign_id):
    """Send a campaign immediately"""
    campaign = Campaign.objects.get(id=campaign_id)
    sender_email = campaign.sender.email_address
    sender_name = campaign.sender.name
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
            recipient_cf = recipient.custom_fields.select_related('custom_field').all()
            recipeint_fields = {}
            for cf in recipient_cf:
                recipeint_fields[cf.custom_field.name] = cf.get_value()
            recipeint_fields['email'] = recipient.email
            recipeint_fields['created_at'] = recipient.created_at

            message = Template(content)
            content = message.render(contact=recipeint_fields)

            #Send the email
            send_email_ses(recipient=recipient.email, subject=subject, body=content, sender_name=sender_name, sender_email=sender_email)
            print(recipeint_fields)
            print(content)
            

    campaign.status = 'SENT'
    campaign.save()
    logger.info(f"CAMPAIGN ID: {campaign_id}")
    return