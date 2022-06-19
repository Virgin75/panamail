import csv
import io
import base64
from celery.utils.log import get_task_logger
from django.shortcuts import get_object_or_404
from panamail import celery_app
from .models import Contact, CustomField, CustomFieldOfContact
from users.models import Workspace

from .models import Contact, CustomField, CustomFieldOfContact


logger = get_task_logger(__name__)

@celery_app.task(name="do_csv_import")
def do_csv_import(contacts, column_mapping, workspace_id, update_existing):
    """Create all contacts from the csv file imported"""
    decrypted = base64.b64decode(contacts).decode('utf-8')
    with io.StringIO(decrypted) as f:
        reader = csv.DictReader(f)

        created_contacts = 0
        updated_contacts = 0
        nb_errors = 0

        #Get or Create contact
        for contact in reader:
            contact_l = list(contact.values())
            contact_obj, created = Contact.objects.get_or_create(
                email=contact_l[column_mapping.index('email')],
                workspace=get_object_or_404(Workspace, id=workspace_id)
            )
            #Add custom fields to contact
            for i, field in enumerate(contact_l):
                if field == contact_l[column_mapping.index('email')]:
                    continue
                
                obj, created_obj = CustomFieldOfContact.objects.get_or_create(
                    contact=contact_obj,
                    custom_field=CustomField.objects.get(id=column_mapping[i])
                )
                if update_existing == "True":
                    obj.value = field
                    obj.save()
                if update_existing == "False":
                    if created:
                        obj.value = field
                        obj.save()
                

    
    logger.info(f"All contacts were created with success.")
    return