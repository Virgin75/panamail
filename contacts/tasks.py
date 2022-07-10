import csv
import io
import base64
import psycopg2
from .encryption_util import decrypt
from celery.utils.log import get_task_logger
from django.shortcuts import get_object_or_404
from pyparsing import line
from panamail import celery_app
from .models import Contact, ContactInSegment, CustomField, List, CustomFieldOfContact, CSVImportHistory, ContactInList, DatabaseToSync, DatabaseRule, Segment
from users.models import Workspace
from .utils import retrieve_segment_members
from .models import Contact, CustomField, CustomFieldOfContact


logger = get_task_logger(__name__)


@celery_app.task(name="sync_contacts_from_db")
def sync_contacts_from_db(sync_db_id, rule_id):
    db = DatabaseToSync.objects.get(id=sync_db_id)
    rule = DatabaseRule.objects.get(id=rule_id)

    logger.info(str(db.db_host) + ' ' + str(db.db_port) + ' ' + str(db.db_name) + ' ' + str(db.db_user) + ' ' + str(decrypt(db.db_password)))

    conn = psycopg2.connect(
            host=db.db_host,
            port=db.db_port,
            database=db.db_name,
            user=db.db_user,
            password=decrypt(db.db_password)
    )
    cursor = conn.cursor()
    cursor.execute(rule.query)
    conn.commit()

    results = cursor.fetchall()

    #Get or create contact
    for contact in results:
        pass

    logger.info(results)
    cursor.close()
    
    logger.info('Error while connecting to the db')
    return


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


@celery_app.task(name="compute_segment_members")
def compute_segment_members(segment_id):
    """Get all Segment members given a Segment id. Triggered when a segment is created or updated"""
    
    segment = Segment.objects.get(id=segment_id)
    if segment.conditions.all().count() == 0:
        return

    new_contacts = retrieve_segment_members(segment_id) #QuerySet

    # Check which Contacts do not match anymore with the new Segment conditions
    contacts_to_delete = ContactInSegment.objects.filter(
        segment=segment
    ).exclude(contact_id__in=new_contacts.values_list('id', flat=True))
    contacts_to_delete.delete()
  
    # Add new Contacts to the Segment
    for contact in new_contacts:
        cs, created = ContactInSegment.objects.get_or_create(
            contact=contact,
            segment=segment
        )

@celery_app.task(name="compute_contact_segments")
def compute_contact_segments(contact_id):
    """Update a Contact Segments membership. Triggered when any Contact info is updated (field change, new event, new page, new list membership...)"""
   
    contact = Contact.objects.get(id=contact_id)
    workspace = contact.workspace
    segments = workspace.segments.all()
    for segment in segments:
        is_a_match = retrieve_segment_members(segment.id, contact_id)
        if is_a_match:
            cs = ContactInSegment.objects.get_or_create(
                contact=contact,
                segment=segment
            )
        else:
            try:
                cs = ContactInSegment.objects.get(
                    contact=contact,
                    segment=segment
                )
                cs.delete()
            except ContactInSegment.DoesNotExist:
                #Contact was not member of the Segment. Continue
                pass
