from django_rq import job


@job(queue='events')
def send_double_optin_validation_email(list_id, validate_token, contact_id):
    pass
