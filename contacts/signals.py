from django.db.models.signals import post_save
from django.db.models import signals
from django.dispatch import receiver
from .models import Segment, Condition
from .tasks import compute_segment_members


@receiver(signals.post_save, sender=Condition, dispatch_uid='segment_update_from_condition')
def get_members_of_segment(sender, instance, **kwargs):
    compute_segment_members.delay(instance.segment.id)

