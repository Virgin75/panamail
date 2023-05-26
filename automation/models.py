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
    # Contacts currently moving through the campaign journey (not finished yet)
    current_contacts = models.ManyToManyField('contacts.Contact', blank=True, through='AutomationCampaignContact')
    # Contacts that have already exited the campaign journey
    done_contacts = models.ManyToManyField('contacts.Contact', blank=True, related_name='done_automation_campaigns')


class Step(BaseWorkspace):
    """
    A Step is something that should be executed in a specific order within an automation campaign.

    Everytime a Step processing is done for a Contact, the step with the next
    'order' number will be automatically processed.

     A Step content is defined in the custom @property 'content'
       >> This 'content' field links to a specific model depending on the Step type.
       It might be : 'StepSendEmail', 'StepWait', etc.
    """

    STEP_TYPES = [
        ('SEND_EMAIL', 'Send an email when the Contact enters this Step.'),
        ('WAIT', 'Wait for a specific time before processing the next Step.'),
    ]

    automation_campaign = models.ForeignKey('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True)
    # parent = models.ForeignKey('Step', on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=0)
    step_type = models.CharField(max_length=50, choices=STEP_TYPES, default=STEP_TYPES[0][0])

    @property
    def content(self):
        match self.step_type:
            case 'SEND_EMAIL':
                return self.send_email_step
            case 'WAIT':
                return self.wait_step

    @property
    def has_next_step(self):
        return self.order < self.automation_campaign.steps.count()


class StepSendEmail(BaseWorkspace):
    """Store information about the email to send in an Automation Campaign 'Send Email' Step."""

    step = models.OneToOneField('Step', on_delete=models.CASCADE, null=True, blank=True, related_name='send_email_step')
    email = models.ForeignKey('emails.Email', on_delete=models.CASCADE, null=True, blank=True)


class StepWait(BaseWorkspace):
    """Store information about the delay to wait in an Automation Campaign 'Wait' Step."""

    step = models.OneToOneField('Step', on_delete=models.CASCADE, null=True, blank=True, related_name='wait_step')
    delay = models.IntegerField(default=1)
    delay_unit = models.CharField(max_length=15, choices=(('DAY', 'Day'), ('HOUR', 'Hour'), ('WEEK', 'Week')),
                                  default='DAY')


class AutomationCampaignContact(BaseWorkspace):
    """
    Store information about how a Contact is moving through the AutomationCampaign journey.
    """

    automation_campaign = models.ForeignKey('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True)
    current_step = models.ForeignKey('Step', on_delete=models.CASCADE, null=True, blank=True)
