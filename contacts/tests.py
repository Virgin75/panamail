from io import BytesIO

import pytest
from django.urls import reverse

from .factories import ListFactory, CustomFieldFactory, ContactFactory, ContactInListFactory, \
    CustomFieldOfContactFactory, SegmentFactory, GroupOfConditionsFactory, ConditionFactory, ContactInSegmentFactory
from .models import Contact, ContactInList, CSVImportHistory, CustomFieldOfContact, CustomField, Segment, \
    Condition


@pytest.mark.django_db
def test_create_list(auth_client):
    url = reverse("contacts:lists-list")
    payload = {
        'name': 'new name',
        "description": "new description",
        "workspace": auth_client.workspace.id,
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'new name'
    assert res['description'] == 'new description'


@pytest.mark.django_db
def test_list_lists(auth_client, workspace2):
    lists = ListFactory.create_batch(
        size=3,
        workspace=auth_client.workspace,
        contacts__size=4,
    )
    ListFactory.create_batch(
        size=3,
        workspace=workspace2,
        contacts__size=4,
    )

    url = reverse("contacts:lists-list")
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == len(lists)  # must not be 6
    assert res['results'][0]['name'] == lists[0].name


@pytest.mark.django_db
def test_bulk_import_contacts_in_list(auth_client):
    list = ListFactory.create(
        workspace=auth_client.workspace,
        contacts__size=3,
    )
    custom_field_int = CustomFieldFactory.create(
        workspace=auth_client.workspace,
        type='int',
        name='age',
    )
    custom_field_str = CustomFieldFactory.create(
        workspace=auth_client.workspace,
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
        'workspace': auth_client.workspace.id,
        "file": file,
        "mapping": ["email", str(custom_field_int.id), str(custom_field_str.id)],
    }
    response = auth_client.api.post(url, payload)
    res = response.json()

    contacts_custom_fields = CustomFieldOfContact.objects.filter(contact__workspace=auth_client.workspace)
    assert len(contacts_custom_fields) == 4
    task = CSVImportHistory.objects.first()
    assert task.file_name == 'test.csv'
    assert task.nb_created == 2
    assert task.nb_errors == 0
    assert Contact.objects.filter(email="test1@gmail.com").exists()
    assert Contact.objects.filter(email="test2@gmail.com").exists()
    assert task.workspace == auth_client.workspace
    assert task.list == list
    assert task.mapping == ['email', str(custom_field_int.id), str(custom_field_str.id)]
    assert response.status_code == 200
    assert res["status"] == "Started importing contacts from csv file."


@pytest.mark.django_db
def test_list_contacts_in_list(auth_client):
    list = ListFactory.create(
        workspace=auth_client.workspace,
        contacts__size=3,
    )

    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['contact']['email'] in [contact.email for contact in Contact.objects.all()]


@pytest.mark.django_db
def test_list_unsub_contacts_in_list(auth_client):
    list = ListFactory.create(
        workspace=auth_client.workspace,
        contacts__size=3,
    )
    contact = Contact.objects.first()
    list.unsubscribed_contacts.add(contact)

    url = reverse(
        "contacts:lists-unsubscribed-contacts",
        kwargs={'pk': list.id}
    )
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 1
    assert res['results'][0]['email'] == contact.email


@pytest.mark.django_db
def test_list_double_optin_token_validation(auth_client):
    list = ListFactory.create(
        workspace=auth_client.workspace,
        optin_choice="double",
        contacts__size=1,
    )
    contact = Contact.objects.first()
    validation_token = ContactInList.objects.first().double_optin_token

    url = reverse(
        "contacts:lists-double-optin",
        kwargs={'pk': list.id, "validation_token": validation_token}
    )
    response = auth_client.api.get(url, {'email': contact.email})
    res = response.json()
    assert response.status_code == 200
    assert res == {"status": f"Subscription to the list {list.id} confirmed."}
    assert ContactInList.objects.first().double_optin_validate_date is not None


@pytest.mark.django_db
def test_list_all_contacts_of_list(auth_client):
    list = ListFactory.create(
        workspace=auth_client.workspace,
        contacts__size=3,
    )
    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    res_contacts = [contact['contact']['email'] for contact in res['results']]
    expected_contacts = [contact.email for contact in Contact.objects.all()]
    assert res_contacts == expected_contacts


@pytest.mark.django_db
def test_add_existing_contact_to_list(auth_client):
    list = ListFactory.create(workspace=auth_client.workspace, contacts__size=1)
    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    contact = ContactFactory(workspace=auth_client.workspace)
    payload = {
        'contact': contact.id,
        'workspace': auth_client.workspace.id,
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['contact']['email'] == contact.email
    assert res['list']['name'] == list.name
    assert list.contacts.count() == 2


@pytest.mark.django_db
def test_remove_contact_from_list(auth_client):
    list = ListFactory.create(workspace=auth_client.workspace, contacts__size=1)
    contact = Contact.objects.first()

    url = reverse(
        "contacts:lists-contacts-detail",
        kwargs={'parent_lookup_lists': list.id, 'pk': contact.id}
    )
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert ContactInList.objects.filter(contact=contact, list=list).count() == 0


@pytest.mark.django_db
def test_create_contact(auth_client):
    url = reverse("contacts:contacts-list")
    payload = {
        'email': 'test3@gmail.com',
        'workspace': auth_client.workspace.id
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['email'] == 'test3@gmail.com'
    assert res['manual_email_status'] == 'SUB'


@pytest.mark.django_db
def test_list_contacts(auth_client):
    ContactFactory.create_batch(3, workspace=auth_client.workspace)
    url = reverse("contacts:contacts-list")
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['email'] in [contact.email for contact in Contact.objects.all()]


@pytest.mark.django_db
def test_retrieve_contact(auth_client):
    contact = ContactFactory.create(workspace=auth_client.workspace)
    CustomFieldOfContactFactory.create(
        contact=contact,
        workspace=auth_client.workspace,
        custom_field=CustomFieldFactory.create(workspace=auth_client.workspace, type='int'),
        value_int=10
    )

    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['email'] == contact.email
    assert res["first_name"] == contact.first_name
    assert res["last_name"] == contact.last_name
    assert res["workspace"] == str(auth_client.workspace.id)
    assert res["custom_fields"][0]["value"] == 10


@pytest.mark.django_db
def test_update_contact(auth_client):
    contact = ContactFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    payload = {
        'first_name': 'test',
        'last_name': 'test',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['first_name'] == 'test'
    assert res['last_name'] == 'test'


@pytest.mark.django_db
def test_delete_contact(auth_client):
    contact = ContactFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:contacts-detail", kwargs={'pk': contact.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Contact.objects.filter(id=contact.id).count() == 0


@pytest.mark.django_db
def test_get_lists_of_contact(auth_client):
    contact = ContactFactory(workspace=auth_client.workspace)
    lists = ListFactory.create_batch(3, workspace=auth_client.workspace)
    [list.contacts.add(contact, through_defaults={"workspace": auth_client.workspace}) for list in lists]

    url = reverse("contacts:contacts-lists", kwargs={'pk': contact.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    for list in lists:
        assert list.name in [item['name'] for item in res['results']]


@pytest.mark.django_db
def test_get_segments_of_contact(auth_client):
    contact = ContactFactory(workspace=auth_client.workspace)
    segments = SegmentFactory.create_batch(3, workspace=auth_client.workspace)
    [segment.members.add(contact, through_defaults={"workspace": auth_client.workspace}) for segment in segments]

    url = reverse("contacts:contacts-segments", kwargs={'pk': contact.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    for segment in segments:
        assert segment.name in [item['name'] for item in res['results']]


@pytest.mark.django_db
def test_unsubscribe_contact_from_list(auth_client):
    contact = ContactFactory(workspace=auth_client.workspace)
    list = ListFactory.create(workspace=auth_client.workspace)
    ContactInListFactory.create(contact=contact, list=list, workspace=auth_client.workspace)
    url = reverse("contacts:contacts-unsub-from-list", kwargs={'pk': contact.id, 'list_pk': list.id})

    response = auth_client.api.post(url)
    res = response.json()
    assert response.status_code == 200
    assert res == {"status": "Contact unsubscribed from list."}
    assert list.unsubscribed_contacts.get(id=contact.id) == contact


"""
------------------------------------------------------------------------------------------------------------------------
----------------------------------------------CUSTOM FIELDS TESTS-------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------
"""


@pytest.mark.django_db
@pytest.mark.parametrize("field_type", ["str", "bool", "int", "date"])
def test_set_custom_field_value(auth_client, field_type):
    contact = ContactFactory(workspace=auth_client.workspace)
    custom_field = CustomFieldFactory.create(type=field_type, workspace=auth_client.workspace)
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
        'workspace': auth_client.workspace.id
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['custom_field']['name'] == custom_field.name
    assert res['value'][:-10] == value[field_type] if field_type == 'date' else res['value'] == value[field_type]


@pytest.mark.django_db
def test_create_custom_field(auth_client):
    url = reverse("contacts:custom-fields-list")
    payload = {
        'name': 'age',
        'workspace': auth_client.workspace.id,
        'type': 'int'
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'age'
    assert res['workspace'] == str(auth_client.workspace.id)
    assert res['type'] == 'int'


@pytest.mark.django_db
def test_list_custom_fields(auth_client):
    CustomFieldFactory.create_batch(3, workspace=auth_client.workspace)
    url = reverse("contacts:custom-fields-list")
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    assert res['results'][0]['name'] in [custom_field.name for custom_field in CustomField.objects.all()]


@pytest.mark.django_db
def test_retrieve_custom_field(auth_client):
    custom_field = CustomFieldFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == custom_field.name
    assert res["workspace"] == str(auth_client.workspace.id)
    assert res["type"] == custom_field.type


@pytest.mark.django_db
def test_update_custom_field(auth_client):
    custom_field = CustomFieldFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    payload = {
        'name': 'age',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == 'age'


@pytest.mark.django_db
def test_delete_custom_field(auth_client):
    custom_field = CustomFieldFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:custom-fields-detail", kwargs={'pk': custom_field.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert CustomField.objects.filter(id=custom_field.id).count() == 0


"""
------------------------------------------------------------------------------------------------------------------------
----------------------------------------------SEGMENTS TESTS------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------
"""


@pytest.mark.django_db
def test_list_segments(auth_client, workspace2):
    segments = SegmentFactory.create_batch(3, workspace=auth_client.workspace)
    SegmentFactory.create_batch(2, workspace=workspace2)

    url = reverse("contacts:segments-list")
    response = auth_client.api.get(url, {'workspace_id': auth_client.workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    res_segments = [segment['name'] for segment in res['results']]
    expected_segments = [segment.name for segment in segments]
    assert expected_segments == res_segments


@pytest.mark.django_db
def test_create_segment(auth_client):
    url = reverse("contacts:segments-list")
    payload = {
        'name': 'Recurrent customers',
        'description': 'Customers who have bought more than 3 times',
        'operator': 'AND',
        'workspace': auth_client.workspace.id,
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['name'] == 'Recurrent customers'
    assert res['description'] == 'Customers who have bought more than 3 times'
    assert res['workspace'] == str(auth_client.workspace.id)
    assert res['operator'] == 'AND'


@pytest.mark.django_db
def test_update_segment(auth_client, workspace2):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:segments-detail", kwargs={'pk': segment.id})
    payload = {
        'description': 'New description',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['description'] == 'New description'

    # Test updating a Segment form a Workspace you don't belong to
    segment2 = SegmentFactory.create(workspace=workspace2)
    url = reverse("contacts:segments-detail", kwargs={'pk': segment2.id})
    response = auth_client.api.patch(url, payload)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_segment(auth_client, workspace2):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:segments-detail", kwargs={'pk': segment.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Segment.objects.filter(id=segment.id).count() == 0

    # Test deleting a Segment form a Workspace you don't belong to
    segment2 = SegmentFactory.create(workspace=workspace2)
    url = reverse("contacts:segments-detail", kwargs={'pk': segment2.id})
    response = auth_client.api.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_segment(auth_client):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    groups = GroupOfConditionsFactory.create_batch(2, segment=segment, workspace=auth_client.workspace)
    for group in groups:
        ConditionFactory.create_batch(2, group=group, workspace=auth_client.workspace)

    url = reverse("contacts:segments-detail", kwargs={'pk': segment.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['name'] == segment.name
    assert res['operator'] == segment.operator
    assert len(res['conditions']) == 2  # 2 groups of conditions
    assert res['conditions'][0]['operator'] == groups[0].operator
    assert res['conditions'][1]['operator'] == groups[1].operator
    assert len(res['conditions'][0]['conditions']) == 2  # 2 conditions in the first group
    assert len(res['conditions'][1]['conditions']) == 2  # 2 conditions in the second group


@pytest.mark.django_db
def test_retrieve_segment_with_contacts(auth_client, workspace2):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    contacts = ContactFactory.create_batch(3, workspace=auth_client.workspace)
    for contact in contacts:
        ContactInSegmentFactory.create(segment=segment, contact=contact, workspace=auth_client.workspace)

    url = reverse("contacts:segments-contacts", kwargs={'pk': segment.id})
    response = auth_client.api.get(url)
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == 3
    res_contacts = [contact['id'] for contact in res['results']]
    expected_contacts = [str(contact.id) for contact in contacts]
    assert expected_contacts == res_contacts

    # Test retrieving a Segment members form a Workspace you don't belong to
    segment2 = SegmentFactory.create(workspace=workspace2)
    contacts = ContactFactory.create_batch(3, workspace=workspace2)
    for contact in contacts:
        ContactInSegmentFactory.create(segment=segment2, contact=contact, workspace=workspace2)
    url = reverse("contacts:segments-contacts", kwargs={'pk': segment2.id})
    response = auth_client.api.get(url)
    assert response.status_code == 403


"""
------------------------------------------------------------------------------------------------------------------------
------------------------------------------SEGMENT GROUP & CONDITION TESTS-----------------------------------------------
------------------------------------------------------------------------------------------------------------------------
"""


@pytest.mark.django_db
def test_create_segment_group(auth_client):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    url = reverse("contacts:segments-groups-list", kwargs={
        'parent_lookup_segments': segment.id
    })
    payload = {
        'operator': 'OR',
        'segment': segment.id,
        'workspace': auth_client.workspace.id,
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['operator'] == 'OR'
    assert res['segment']['id'] == str(segment.id)


@pytest.mark.django_db
def test_update_segment_group(auth_client):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    group = GroupOfConditionsFactory.create(segment=segment, workspace=auth_client.workspace, operator='OR')
    url = reverse("contacts:segments-groups-detail", kwargs={
        'parent_lookup_segments': segment.id,
        'pk': group.id
    })
    payload = {
        'operator': 'AND',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['operator'] == 'AND'


@pytest.mark.django_db
def test_delete_segment_group(auth_client, workspace2):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    group = GroupOfConditionsFactory.create(segment=segment, workspace=auth_client.workspace)
    url = reverse("contacts:segments-groups-detail", kwargs={
        'parent_lookup_segments': segment.id,
        'pk': group.id
    })
    response = auth_client.api.delete(url)
    assert response.status_code == 204

    # Test deleting a Segment Group form a Workspace you don't belong to
    segment2 = SegmentFactory.create(workspace=workspace2)
    group2 = GroupOfConditionsFactory.create(segment=segment2, workspace=workspace2)
    url = reverse("contacts:segments-groups-detail", kwargs={
        'parent_lookup_segments': segment2.id,
        'pk': group2.id
    })
    response = auth_client.api.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_segment_condition_basic_field(auth_client):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    group = GroupOfConditionsFactory.create(segment=segment, workspace=auth_client.workspace)
    url = reverse("contacts:segments-groups-conditions", kwargs={
        'parent_lookup_segments': segment.id,
        'pk': group.id,
    })
    payload = {
        'condition_type': 'BASIC FIELD',
        'basic_field': 'FIRST_NAME',
        'check_type': 'CONTAINS',
        'input_value': 'Brad',
        'workspace': auth_client.workspace.id,
    }
    response = auth_client.api.post(url, payload)
    res = response.json()
    assert response.status_code == 201
    assert res['condition_type'] == 'BASIC FIELD'
    assert res['basic_field'] == 'FIRST_NAME'
    assert res['check_type'] == 'CONTAINS'
    assert res['input_value'] == 'Brad'
    assert res['group'] == group.id


# TODO: Create tests for the other condition types


@pytest.mark.django_db
def test_update_segment_condition(auth_client):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    group = GroupOfConditionsFactory.create(segment=segment, workspace=auth_client.workspace)
    condition = ConditionFactory.create(group=group, workspace=auth_client.workspace)
    url = reverse("contacts:segments-groups-conditions", kwargs={
        'parent_lookup_segments': segment.id,
        'pk': group.id,
        'condition_pk': condition.id
    })
    payload = {
        'input_value': 'Johnny',
    }
    response = auth_client.api.patch(url, payload)
    res = response.json()
    assert response.status_code == 200
    assert res['input_value'] == 'Johnny'


@pytest.mark.django_db
def test_delete_segment_condition(auth_client, workspace2):
    segment = SegmentFactory.create(workspace=auth_client.workspace)
    group = GroupOfConditionsFactory.create(segment=segment, workspace=auth_client.workspace)
    condition = ConditionFactory.create(group=group, workspace=auth_client.workspace)
    url = reverse("contacts:segments-groups-conditions", kwargs={
        'parent_lookup_segments': segment.id,
        'pk': group.id,
        'condition_pk': condition.id
    })
    response = auth_client.api.delete(url)
    assert response.status_code == 204
    assert Condition.objects.count() == 0

    # Test deleting a Segment Condition form a Workspace you don't belong to
    segment2 = SegmentFactory.create(workspace=workspace2)
    group2 = GroupOfConditionsFactory.create(segment=segment2, workspace=workspace2)
    condition2 = ConditionFactory.create(group=group2, workspace=workspace2)
    url = reverse("contacts:segments-groups-conditions", kwargs={
        'parent_lookup_segments': segment2.id,
        'pk': group2.id,
        'condition_pk': condition2.id
    })
    response = auth_client.api.delete(url)
    assert response.status_code == 403
    assert Condition.objects.count() == 1
