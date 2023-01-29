import pytest
from django.urls import reverse

from .factories import ListFactory
from .models import Contact, ContactInList


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
def test_list_contacts_in_list(auth_client, workspace, workspace_member, user, list, contacts):
    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    response = auth_client.get(url, {'workspace_id': workspace.id})
    res = response.json()
    assert response.status_code == 200
    assert res['count'] == len(contacts)
    assert res['results'][0]['contact']['email'] in [contact.email for contact in contacts]


@pytest.mark.django_db
def test_add_contact_to_list(auth_client, workspace, workspace_member, user, list, contacts):
    url = reverse(
        "contacts:lists-contacts-list",
        kwargs={'parent_lookup_lists': list.id}
    )
    contact = Contact.objects.create(workspace=workspace, email="jjj@fff.fr")
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
def test_remove_contact_from_list(auth_client, workspace, workspace_member, user, list, contacts):
    url = reverse(
        "contacts:lists-contacts-detail",
        kwargs={'parent_lookup_lists': list.id, 'pk': contacts[0].id}
    )
    response = auth_client.delete(url)
    assert response.status_code == 204
    assert ContactInList.objects.filter(contact=contacts[0], list=list).count() == 0


"""
# Test create a contact
@pytest.mark.django_db
def test_create_contact(auth_client, workspace, workspace_member, user):
    response = auth_client.post('/contacts/contacts', {
        'email': 'pedro.almodovar@gmail.com',
        'workspace': workspace.id
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['email'] == 'pedro.almodovar@gmail.com'
    assert resp_json['manual_email_status'] == 'SUB'
    assert resp_json['workspace'] == str(workspace.id)

# Test list Contacts
@pytest.mark.django_db
def test_list_contacts(auth_client, workspace, contact, workspace_member, user):
    response = auth_client.get(f'/contacts/contacts?workspace_id={workspace.id}')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['count'] == 1
    assert resp_json['results'][0]['email'] == contact.email


# Test update a contact
@pytest.mark.django_db
def test_update_contact(auth_client, workspace, contact, workspace_member, user):
    response = auth_client.patch(f'/contacts/contacts/{contact.id}', {
        'manual_email_status': 'UNSUB'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['email'] == contact.email
    assert resp_json['manual_email_status'] == 'UNSUB'

# Test delete a contact
@pytest.mark.django_db
def test_delete_contact(auth_client, workspace, contact, workspace_member, user):
    response = auth_client.delete(f'/contacts/contacts/{contact.id}')
    assert response.status_code == 204


# Test create a custom field
@pytest.mark.django_db
def test_create_custom_field(auth_client, workspace, contact, workspace_member, user):
    response = auth_client.post(f'/contacts/custom-fields', {
        'type': 'int',
        'name': 'login_count',
        'workspace': str(workspace.id)
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['name'] == 'login_count'
    assert resp_json['workspace'] == str(workspace.id)

# Test list Custom fields
@pytest.mark.django_db
def test_list_custom_fields(auth_client, workspace, contact, custom_field, workspace_member, user):
    response = auth_client.get(f'/contacts/custom-fields?workspace_id={workspace.id}')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json[0]['id'] == custom_field.id
    assert resp_json[0]['workspace'] == str(workspace.id)

# Test update a custom field
@pytest.mark.django_db
def test_update_custom_field(auth_client, workspace, contact, custom_field, workspace_member, user):
    response = auth_client.patch(f'/contacts/custom-fields/{custom_field.id}', {
        'name': 'New-Name'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == 'New-Name'

# Test delete a custom field
@pytest.mark.django_db
def test_delete_custom_field(auth_client, workspace, contact, custom_field, workspace_member, user):
    response = auth_client.delete(f'/contacts/custom-fields/{custom_field.id}')
    assert response.status_code == 204

# Test set a Contact custom fields
@pytest.mark.django_db
def test_set_contact_custom_fields(auth_client, workspace, contact, custom_field, workspace_member, user):
    response = auth_client.post(f'/contacts/contacts/{contact.id}/set-custom-fields', {
        custom_field.id: 'My custom value',
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['status'] == 'All fields were updated successfully.'


# Test create a list
@pytest.mark.django_db
def test_create_list(auth_client, workspace, contact, workspace_member, user):
    response = auth_client.post(f'/contacts/lists', {
        'name': 'Newsletter Client',
        'workspace': str(workspace.id)
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['name'] == 'Newsletter Client'
    assert resp_json['workspace'] == str(workspace.id)

# Test list lists
@pytest.mark.django_db
def test_list_lists(auth_client, workspace, list, contact, custom_field, workspace_member, user):
    response = auth_client.get(f'/contacts/lists?workspace_id={workspace.id}')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['count'] == 1
    assert resp_json['results'][0]['id'] == str(list.id)


# Test update a List
@pytest.mark.django_db
def test_update_list(auth_client, workspace, list, contact, custom_field, workspace_member, user):
    response = auth_client.patch(f'/contacts/lists/{list.id}', {
        'name': 'New-List-Name'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['name'] == 'New-List-Name'

# Test delete a list
@pytest.mark.django_db
def test_delete_list(auth_client, workspace, contact, list, custom_field, workspace_member, user):
    response = auth_client.delete(f'/contacts/lists/{list.id}')
    assert response.status_code == 204

# Test list contacts in list
@pytest.mark.django_db
def test_list_contacts_in_list(auth_client, workspace, list, contact, contact_in_list, custom_field, workspace_member, user):
    response = auth_client.get(f'/contacts/contacts-in-list?list_id={list.id}')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['count'] == 1
    assert resp_json['results'][0]['contact']['email'] == contact.email

# Test add contact in list
@pytest.mark.django_db
def test_add_contact_in_list(auth_client, workspace, list, contact, workspace_member, user):
    response = auth_client.post(f'/contacts/add-contact-in-list', {
        'list': str(list.id),
        'contact': str(contact.id)
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['contact'] == str(contact.id)
    assert resp_json['list'] == str(list.id)


# Test delete a contact from list
@pytest.mark.django_db
def test_delete_contact_from_list(auth_client, workspace, contact, contact_in_list, list, custom_field, workspace_member, user):
    response = auth_client.delete(f'/contacts/delete-contact-in-list/{contact_in_list.id}')
    assert response.status_code == 204


# Test create a Segment
@pytest.mark.django_db
def test_create_segment(auth_client, workspace, list, contact, workspace_member, user):
    response = auth_client.post(f'/contacts/segments', {
        'name': 'Active users',
        'operator': 'AND',
        'workspace': str(workspace.id)
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['workspace'] == str(workspace.id)
    assert resp_json['name'] == 'Active users'

# Test list segments
@pytest.mark.django_db
def test_list_segments(auth_client, workspace, list, segment, contact, contact_in_list, custom_field, workspace_member, user):
    response = auth_client.get(f'/contacts/segments?workspace_id={workspace.id}')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json[0]['id'] == str(segment.id)


# Test update a Segment
@pytest.mark.django_db
def test_update_segment(auth_client, workspace, list, segment, contact, custom_field, workspace_member, user):
    response = auth_client.patch(f'/contacts/segments/{segment.id}', {
        'operator': 'OR'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['operator'] == 'OR'

# Test delete a Segment
@pytest.mark.django_db
def test_delete_segment(auth_client, workspace, contact, list, segment, custom_field, workspace_member, user):
    response = auth_client.delete(f'/contacts/segments/{segment.id}')
    assert response.status_code == 204


# Test create a Condition
@pytest.mark.django_db
def test_create_condition(auth_client, workspace, list, contact, segment, workspace_member, custom_field, user):
    response = auth_client.post(f'/contacts/segments/{segment.id}/conditions', {
        'condition_type': 'CUSTOM FIELD',
        'custom_field': custom_field.id,
        'check_type': 'IS NOT',
        'input_value': 'Alberto'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 201
    assert resp_json['segment'] == str(segment.id)
    assert resp_json['id'] is not None

# Test list Conditions of a Segment
@pytest.mark.django_db
def test_list_conditions(auth_client, workspace, list, contact, segment, condition, workspace_member, custom_field, user):
    response = auth_client.get(f'/contacts/segments/{segment.id}/conditions')
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json[0]['segment'] == str(segment.id)
    assert resp_json[0]['id'] == condition.id


# Test update a Condition
@pytest.mark.django_db
def test_update_segment(auth_client, workspace, list, segment, condition, custom_field, contact, workspace_member, user):
    response = auth_client.patch(f'/contacts/segments-conditions/{condition.id}', {
        'check_type': 'CONTAINS'
    })
    resp_json = json.loads(response.content)
    assert response.status_code == 200
    assert resp_json['check_type'] == 'CONTAINS'

# Test delete a Condition
@pytest.mark.django_db
def test_delete_condition(auth_client, workspace, contact, list, segment, condition, custom_field, workspace_member, user):
    response = auth_client.delete(f'/contacts/segments-conditions/{condition.id}')
    assert response.status_code == 204"""
