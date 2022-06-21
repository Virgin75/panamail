import csv
import io
import base64
from celery.utils.log import get_task_logger
from django.shortcuts import get_object_or_404
from pyparsing import line
from panamail import celery_app
from .models import Contact, CustomField, List, CustomFieldOfContact, CSVImportHistory, ContactInList
from users.models import Workspace

from .models import Contact, CustomField, CustomFieldOfContact


logger = get_task_logger(__name__)

@celery_app.task(name="do_csv_import")
def do_csv_import(contacts, column_mapping, workspace_id, update_existing, list_id, unsub):
    """Create all contacts from the csv file imported"""
    created_contacts = 0
    updated_contacts = 0
    nb_errors = 0
    lines_with_error = []

    decrypted = base64.b64decode(contacts).decode('utf-8')

    with io.StringIO(decrypted) as f:
        reader = csv.DictReader(f)

        #Get or Create contact
        for line, contact in enumerate(reader):
            contact_l = list(contact.values())
            try:
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
                
                #Add contact to selected list
                if len(list_id) > 1:
                    membership = ContactInList(
                        contact=contact_obj,
                        list=List.objects.get(id=list_id)
                    )
                    membership.save()
                
                #Set unsub status
                if unsub == 'True':
                    contact_obj.manual_email_status = False
                    contact_obj.save()

                #Update upload metrics
                if created:
                    created_contacts += 1
                else:
                    updated_contacts += 1

            except:
                nb_errors +=1
                lines_with_error.append(str(line + 2))
                

    activity = CSVImportHistory(
        nb_created = created_contacts,
        nb_updated = updated_contacts,
        nb_errors = nb_errors,
        error_message = ', '.join(lines_with_error),
        workspace = Workspace.objects.get(id=workspace_id)
    )
    activity.save()

    logger.info(f"{created_contacts} contacts were created and {updated_contacts} were updated.")
    return