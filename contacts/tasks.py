import csv
import io

import psycopg2
from celery.utils.log import get_task_logger
from django_rq import job

from panamail import celery_app
from .encryption_util import decrypt
from .models import Contact, CustomField, CustomFieldOfContact
from .models import ContactInSegment, CSVImportHistory, DatabaseToSync, DatabaseRule, Segment
from .utils import retrieve_segment_members

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


@job
def do_csv_import(import_task_id):
    """Async task that import Contacts into a specific List."""
    created_contacts = 0
    updated_contacts = 0
    nb_errors = 0
    lines_with_error = []

    # Retrieve fields from task
    task = CSVImportHistory.objects.get(id=import_task_id)
    csv_file = task.file
    csv_binary_file = io.BytesIO(bytes(memoryview(csv_file)))
    must_mass_unsubscribe = task.mass_unsubscribe
    must_update_existing = task.update_existing
    mapping = task.mapping

    with io.TextIOWrapper(csv_binary_file, encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        custom_fields = []
        for i, column in enumerate(reader.fieldnames):
            if column not in ['email', 'first_name', 'last_name']:
                custom_fields.append({
                    'name': column,
                    'id': mapping[i],
                    'type': CustomField.objects.get(id=mapping[i]).type,
                    'row_index': i
                })

        for row in reader:
            try:
                # Get or create Contact
                contact, created = Contact.objects.get_or_create(
                    workspace=task.workspace,
                    email=row['email']
                )

                # If must mass unsub contact
                if must_mass_unsubscribe:
                    contact.transac_email_status = 'UNSUB'
                    contact.manual_email_status = 'UNSUB'
                    contact.save()

                # Update/set reserved attributes
                if "first_name" in row and (must_update_existing or created):
                    contact.first_name = row['first_name']
                if "last_name" in row and (must_update_existing or created):
                    contact.last_name = row['last_name']
                contact.save()

                # Update/set custom fields
                for field in custom_fields:
                    value = CustomFieldOfContact.objects.filter(contact=contact, custom_field_id=field['id'])
                    if value.exists() and must_update_existing:
                        match field["type"]:
                            case "int":
                                value[0].value_int = row[field['name']]
                            case "str":
                                value[0].value_str = row[field['name']]
                            case "bool":
                                value[0].value_bool = row[field['name']]
                            case "date":
                                value[0].value_date = row[field['name']]
                        value[0].save()

                    if not value.exists():
                        match field["type"]:
                            case "int":
                                CustomFieldOfContact.objects.create(
                                    contact=contact,
                                    custom_field_id=field['id'],
                                    value_int=row[field['name']],
                                    workspace=task.workspace
                                )
                            case "str":
                                CustomFieldOfContact.objects.create(
                                    contact=contact,
                                    custom_field_id=field['id'],
                                    value_str=row[field['name']],
                                    workspace=task.workspace
                                )
                            case "bool":
                                CustomFieldOfContact.objects.create(
                                    contact=contact,
                                    custom_field_id=field['id'],
                                    value_bool=row[field['name']],
                                    workspace=task.workspace
                                )
                            case "date":
                                CustomFieldOfContact.objects.create(
                                    contact=contact,
                                    custom_field_id=field['id'],
                                    value_date=row[field['name']],
                                    workspace=task.workspace
                                )

                if created:
                    created_contacts += 1
                else:
                    updated_contacts += 1

            except Exception as e:
                nb_errors += 1
                lines_with_error.append(row["email"])

            finally:
                task.file = None
                task.save()

    task.nb_created = created_contacts
    task.nb_updated = updated_contacts
    task.nb_errors = nb_errors
    task.error_message = ', '.join(lines_with_error)
    task.save()

    logger.info(f"{created_contacts} contacts were created and {updated_contacts} were updated.")
    return


@job
def compute_segment_members(segment_id):
    # Get all Segment members given a Segment id. Triggered when a segment is created or updated
    
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


@job
def compute_contact_segments(contact_id):
    # Update a Contact Segments membership. Triggered when any Contact info is updated (field change, new event, new page, new list membership...)

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
