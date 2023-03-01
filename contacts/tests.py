from io import BytesIO

import pytest
from django.urls import reverse

from .factories import ListFactory, CustomFieldFactory, ContactFactory, ContactInListFactory, \
    CustomFieldOfContactFactory, SegmentFactory
from .models import Contact, ContactInList, CSVImportHistory, CustomFieldOfContact, CustomField


@pytest.mark.django_db
def test_create_list(auth_client, workspace):
    url = reverse("contacts:lists-list")
    payload = {
        'name': 'new name',
        "description": "new description",
        "workspace": workspace.id,
    }
    response = auth_client.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'new name'
    assert res['description'] == 'new description'


@pytest.mark.django_db
def test_list_lists(auth_client, workspace, workspace2):
    lists = ListFactory.create_batch(
        size=3,
        workspace=workspace,
        contacts__size=4,
    )
    ListFactory.create_batch(
        size=3,
        workspace=workspace2,
        contacts__size=4,
    )

    url = reverse("contacts:lists-list")
    response = auth_client.get(url, {'workspace_id': workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == len(lists)  # must not be 6
    assert res['results'][0]['name'] == lists[0].name


@pytest.mark.django_db
def test_bulk_import_contacts_in_list(auth_client, workspace):
    list = ListFactory.create(
        workspace=workspace,
        contacts__size=3,
    )
    custom_field_int = CustomFieldFactory.create(
        workspace=workspace,
        type='int',
        name='age',
    )
    custom_field_str = CustomFieldFactory.create(
        workspace=workspace,
        type='str',
        name='type',
    )
    file = BytesIO(b'email,age,type\ntest1@gmail.com,20,student\ntest2@gmail.com,30,teacher')
    file.name = 'test.csv'

    url = reverse("contacts:contacts-bulk-import")
    payload = {
        "update_existing": False,
        "mass_unsubscribe": False,
        "list": list.id,
        'workspace': workspace.id,
        "file": file,
        "mapping": ["email", str(custom_field_int.id), str(custom_field_str.id)],
    }
    response = auth_client.post(url, payload)
    res = response.json()

    contacts_custom_fields = CustomFieldOfContact.objects.filter(contact__workspace=workspace)
    assert len(contacts_custom_fields) == 4
    task = CSVImportHistory.objects.first()
    assert task.file_name == 'test.csv'
    assert task.nb_created == 2
    assert task.nb_errors == 0
    assert Contact.objects.filter(email="test1@gmail.com").exists()
    assert Contact.objects.filter(email="test2@gmail.com").exists()
    assert task.workspace == workspace
    assert task.list == list
    assert task.mapping == ['email', str(custom_field_int.id), str(custom_field_str.id)]
    assert response.status_code == 200
    assert res["status"] == "Started importing contacts from csv file."


@pytest.mark.django_db
def test_list_contacts_in_list(auth_client, workspace):
    list = ListFactory.create(
        workspace=workspace,
        contacts__size=3,
    )

    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    response = auth_client.get(url, {'workspace_id': workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['contact']['email'] in [contact.email for contact in Contact.objects.all()]


@pytest.mark.django_db
def test_add_contact_to_list(auth_client, workspace):
    list = ListFactory.create(workspace=workspace, contacts__size=1)
    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    contact = ContactFactory(workspace=workspace)
    payload = {
        'contact': contact.id,
        'workspace': workspace.id,
    }
    response = auth_client.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['contact']['email'] == contact.email
    assert res['list']['name'] == list.name


@pytest.mark.django_db
def test_remove_contact_from_list(auth_client, workspace):
    list = ListFactory.create(workspace=workspace, contacts__size=1)
    contact = Contact.objects.first()

    url = reverse(
        "contacts:lists-contacts-detail",
        kwargs={'parent_lookup_lists': list.id, 'pk': contact.id}
    )
    response = auth_client.delete(url)
    assert response.status_code == 204
    assert ContactInList.objects.filter(contact=contact, list=list).count() == 0


@pytest.mark.django_db
def test_create_contact(auth_client, workspace):
    url = reverse("contacts:contacts-list")
    payload = {
        'email': 'test3@gmail.com',
        'workspace': workspace.id
    }
    response = auth_client.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['email'] == 'test3@gmail.com'
    assert res['manual_email_status'] == 'SUB'


@pytest.mark.django_db
def test_list_contacts(auth_client, workspace):
    ContactFactory.create_batch(3, workspace=workspace)
    url = reverse("contacts:contacts-list")
    response = auth_client.get(url, {'workspace_id': workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['email'] in [contact.email for contact in Contact.objects.all()]


@pytest.mark.django_db
def test_retrieve_contact(auth_client, workspace):
    contact = ContactFactory.create(workspace=workspace)
    CustomFieldOfContactFactory.create(
        contact=contact,
        workspace=workspace,
        custom_field=CustomFieldFactory.create(workspace=workspace, type='int'),
        value_int=10
    )

    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    response = auth_client.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['email'] == contact.email
    assert res["first_name"] == contact.first_name
    assert res["last_name"] == contact.last_name
    assert res["workspace"] == str(workspace.id)
    assert res["custom_fields"][0]["value"] == 10


@pytest.mark.django_db
def test_update_contact(auth_client, workspace):
    contact = ContactFactory.create(workspace=workspace)
    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    payload = {
        'first_name': 'test',
        'last_name': 'test',
    }
    response = auth_client.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['first_name'] == 'test'
    assert res['last_name'] == 'test'


@pytest.mark.django_db
def test_delete_contact(auth_client, workspace):
    contact = ContactFactory.create(workspace=workspace)
    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    response = auth_client.delete(url)
    assert response.status_code == 204
    assert Contact.objects.filter(id=contact.id).count() == 0


@pytest.mark.django_db
def test_get_lists_of_contact(auth_client, workspace):
    contact = ContactFactory(workspace=workspace)
    lists = ListFactory.create_batch(3, workspace=workspace)
    [list.contacts.add(contact, through_defaults={"workspace": workspace}) for list in lists]

    url = reverse("contacts:contacts-lists", kwargs={'pk': contact.id})
    response = auth_client.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    for list in lists:
        assert list.name in [item['name'] for item in res['results']]


@pytest.mark.django_db
def test_get_segments_of_contact(auth_client, workspace):
    contact = ContactFactory(workspace=workspace)
    segments = SegmentFactory.create_batch(3, workspace=workspace)
    [segment.members.add(contact, through_defaults={"workspace": workspace}) for segment in segments]

    url = reverse("contacts:contacts-segments", kwargs={'pk': contact.id})
    response = auth_client.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    for segment in segments:
        assert segment.name in [item['name'] for item in res['results']]


@pytest.mark.django_db
def test_unsubscribe_contact_from_list(auth_client, workspace):
    contact = ContactFactory(workspace=workspace)
    list = ListFactory.create(workspace=workspace)
    ContactInListFactory.create(contact=contact, list=list, workspace=workspace)
    url = reverse("contacts:contacts-unsub-from-list", kwargs={'pk': contact.id, 'list_pk': list.id})

    response = auth_client.post(url)
    res = response.json()
    assert response.status_code == 200
    assert res == {"status": "Contact unsubscribed from list."}
    assert list.unsubscribed_contacts.get(id=contact.id) == contact


@pytest.mark.django_db
@pytest.mark.parametrize("field_type", ["str", "bool", "int", "date"])
def test_set_custom_field_value(auth_client, workspace, field_type):
    contact = ContactFactory(workspace=workspace)
    custom_field = CustomFieldFactory.create(type=field_type, workspace=workspace)
    url = reverse("contacts:contacts-set-custom-field-value", kwargs={'pk': contact.id})
    value = {
        "str": "test",
        "bool": True,
        "int": 1,
        "date": "2020-01-01"
    }
    payload = {
        'custom_field': custom_field.id,
        f'value_{field_type}': value[field_type],
        'workspace': workspace.id
    }
    response = auth_client.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['custom_field']['name'] == custom_field.name
    assert res['value'][:-10] == value[field_type] if field_type == 'date' else res['value'] == value[field_type]


@pytest.mark.django_db
def test_create_custom_field(auth_client, workspace):
    url = reverse("contacts:custom-fields-list")
    payload = {
        'name': 'age',
        'workspace': workspace.id,
        'type': 'int'
    }
    response = auth_client.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'age'
    assert res['workspace'] == str(workspace.id)
    assert res['type'] == 'int'


@pytest.mark.django_db
def test_list_custom_fields(auth_client, workspace):
    CustomFieldFactory.create_batch(3, workspace=workspace)
    url = reverse("contacts:custom-fields-list")
    response = auth_client.get(url, {'workspace_id': workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['name'] in [custom_field.name for custom_field in CustomField.objects.all()]


@pytest.mark.django_db
def test_retrieve_custom_field(auth_client, workspace):
    custom_field = CustomFieldFactory.create(workspace=workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    response = auth_client.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == custom_field.name
    assert res["workspace"] == str(workspace.id)
    assert res["type"] == custom_field.type


@pytest.mark.django_db
def test_update_custom_field(auth_client, workspace):
    custom_field = CustomFieldFactory.create(workspace=workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    payload = {
        'name': 'age',
    }
    response = auth_client.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == 'age'


@pytest.mark.django_db
def test_delete_custom_field(auth_client, workspace):
    custom_field = CustomFieldFactory.create(workspace=workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    response = auth_client.delete(url)
    assert response.status_code == 204
    assert CustomField.objects.filter(id=custom_field.id).count() == 0
