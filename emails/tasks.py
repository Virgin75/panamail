import boto3
from botocore.config import Config
from celery.utils.log import get_task_logger
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_rq import job

from emails.models import SenderDomain

logger = get_task_logger(__name__)


@job
def check_domain_status(domain_name):
    logger.info(f'Domain is: {domain_name}')

    my_config = Config(
            region_name = settings.AWS_REGION_NAME
    )
    aws_client = boto3.client(
        'sesv2',
        config=my_config,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    response = aws_client.get_email_identity(
            EmailIdentity=domain_name
        )
    logger.info(response['DkimAttributes']['Status'])
    if response['DkimAttributes']['Status'] == 'SUCCESS':
        sd = get_object_or_404(SenderDomain, domain_name=domain_name)
        sd.status = 'VERIFIED'
        sd.save()
    return
