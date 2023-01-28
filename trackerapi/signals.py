"""from django.db.models.signals import post_save
from django.db.models import signals
from django.dispatch import receiver
from .models import Event, Page
from contacts.tasks import compute_segment_members, compute_contact_segments


'''
Signal to update a Contact memberships in Segments
Triggered on :
    > New Page viewed
'''
@receiver(signals.post_save, sender=Page, dispatch_uid='update_contact_segments_from_page')
def update_contacts_segment(sender, instance, **kwargs):
    compute_contact_segments.delay(instance.viewed_by_contact.id)

'''
Signal to update a Contact memberships in Segments
Triggered on :
    > New Event received
'''
@receiver(signals.post_save, sender=Event, dispatch_uid='update_contact_segments_from_segment')
def update_contacts_segment(sender, instance, **kwargs):
    compute_contact_segments.delay(instance.triggered_by_contact.id)"""
