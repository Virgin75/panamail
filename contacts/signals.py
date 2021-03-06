from django.db.models.signals import post_save
from django.db.models import signals
from django.dispatch import receiver
from .models import Condition, Contact, ContactInList
from .tasks import compute_segment_members, compute_contact_segments


@receiver(signals.post_save, sender=Condition, dispatch_uid='segment_update_from_condition')
def get_members_of_segment(sender, instance, **kwargs):
    compute_segment_members.delay(instance.segment.id)

'''
Signal to update a Contact memberships in Segments
Triggered on :
    > Contact update/create (including Custom Fields)
'''
@receiver(signals.post_save, sender=Contact, dispatch_uid='update_contact_segments')
def update_contacts_segment(sender, instance, **kwargs):
    compute_contact_segments.delay(instance.id)

'''
Signal to update a Contact memberships in Segments
Triggered on :
    > ContactInList update/create
'''
@receiver(signals.post_save, sender=ContactInList, dispatch_uid='update_contact_segments_from_list')
def update_contacts_segment(sender, instance, **kwargs):
    compute_contact_segments.delay(instance.contact.id)
