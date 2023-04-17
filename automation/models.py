from django.db import models

from commons.models import BaseWorkspace


class AutomationCampaign(BaseWorkspace):
    """
    An automation campaign is a set of "actions" (Steps) executed automatically in
    response to a trigger.
    When a Contact triggers the campaign, he enters it and goes through all the Steps
    in a specific order (unless he exits the campaign before the end).

     >> A trigger event might be :
        - A contact has viewed a new page on your website
        - A contact has triggered a new custom event
        - A contact has done something with an email (open, click, etc.)
        - A contact has subscribed to a list
        - A contact has joined a segment
        - A time-based trigger (every day, every week, etc.)

    The trigger field is a JSONField. The expected structure is as follow:
        - {"type": "event", "name": "Signed up", "with_attributes": {"plan": "Free"}}
        - {"type": "page", "name": "Pricing"}
        - {"type": "list", "id": 6489}
        - {"type": "segment", "id": 2481}
        - {"type": "email", "id": 2481, "action": "open"} # other actions: ("click","reply","bounce","unsub","spam")
        - {"type": "time", "unit": "day", "value": 2} # other units: ("hour","week","month","year")
     """

    STATUS = [
        ('DRAFT', "Automation campaign is in Draft."),
        ('ACTIVE', 'Automation campaign is active and emails are being sent.'),
        ('PAUSED', 'Automation campaign is stopped.'),
    ]

    name = models.CharField(max_length=89)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS[0][0])
    is_repeated = models.BooleanField(default=True)  # Whether a Contact can enter the campaign many times
    trigger = models.JSONField(null=True, blank=True)
    steps = models.ManyToManyField('Step', blank=True)


class Step(BaseWorkspace):
    """
    A Step is something that should be executed in a specific order
    within an automation campaign.

    A Step is one of the 3 following categories:
        - An action to take (send an email, update a contact attribute, etc.)
        - A condition to check (if a contact has done something, etc.)
        - A delay (wait for 2 days, etc.)

    Everytime a Step processing is done for a Contact, the step with the next
    order will be automatically processed.
    """

    STEP_TYPES = [
        ('ACTION', 'Action to take'),
        ('CONDITION', 'Condition to check'),
        ('DELAY', 'Delay'),
    ]

    automation_campaign = models.ForeignKey('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=0)
    step_type = models.CharField(max_length=15, choices=STEP_TYPES, default=STEP_TYPES[0][0])


class AutomationCampaignContact(BaseWorkspace):
    """
    Store statistics about Automation Campaigns.
    """
    pass
