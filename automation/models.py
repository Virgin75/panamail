from datetime import timedelta, datetime

from django.db import models
from django_rq.queues import get_queue, get_scheduler

from automation.tasks import process_automation_step
from commons.models import BaseWorkspace


class AutomationCampaign(BaseWorkspace):
    """
    An automation campaign is a set of "actions" (Steps) executed automatically in
    response to a trigger.
    When a Contact triggers the campaign, he enters it and goes through all the Steps
    in a specific order (unless he exits the campaign before the end).

     >> A trigger event might be :
        - A contact has viewed a new page on your website ✅
        - A contact has triggered a new custom event ✅
        - A contact has done something with an email (open, click, etc.) ✅
        - A contact has subscribed to a list ✅
        - A contact has joined a segment ✅
        - A time-based trigger (every day, every week, etc.)
        Trigger content is gotten from the custom @property 'trigger'.

    >> Contacts currently in the automation campaign journey are stored in the M2M field 'current_contacts'.
     """

    STATUS = [
        ('DRAFT', "Automation campaign is in Draft."),
        ('ACTIVE', 'Automation campaign is active and emails are being sent.'),
        ('PAUSED', 'Automation campaign is stopped.'),
    ]
    TRIGGER_TYPE = [
        ('EVENT', 'Event trigger'),
        ('PAGE', 'Page trigger'),
        ('EMAIL', 'Email trigger'),
        ('LIST', 'List trigger'),
        ('SEGMENT', 'Segment trigger'),
        ('TIME', 'Time trigger'),
    ]

    name = models.CharField(max_length=89)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS[0][0])
    trigger_type = models.CharField(max_length=15, choices=TRIGGER_TYPE, null=True, blank=True)
    is_repeated = models.BooleanField(default=True)  # Whether a Contact can enter the campaign many times
    steps = models.ManyToManyField('Step', blank=True)
    # Contacts currently moving through the campaign journey (not finished yet)
    current_contacts = models.ManyToManyField('contacts.Contact', blank=True, through='AutomationCampaignContact')
    # Contacts that have already exited the campaign journey
    done_contacts = models.ManyToManyField('contacts.Contact', blank=True, related_name='done_automation_campaigns')

    @property
    def trigger(self):
        """Return the right trigger content regarding the defined trigger_type."""
        match self.trigger_type:
            case 'EVENT':
                return self.event_trigger
            case 'PAGE':
                return self.page_trigger
            case 'EMAIL':
                return self.email_trigger
            case 'LIST':
                return self.list_trigger
            case 'SEGMENT':
                return self.segment_trigger
            case 'TIME':
                return self.time_trigger
        return None

    @property
    def total_contacts_now(self):
        """Return the total number of Contacts currently in the campaign journey."""
        return self.current_contacts.count()

    @property
    def total_contacts_past(self):
        """Return the total number of Contacts who have exited the campaign journey."""
        return self.done_contacts.count()

    def save(self, *args, **kwargs):
        """Prevent Activating an Automation Campaign without a Trigger or Step."""
        if self.status == "ACTIVE" and not self.trigger:
            raise ValueError("An Automation Campaign must have a Trigger to be activated.")
        if self.status == "ACTIVE" and not self.steps.exists():
            raise ValueError("An Automation Campaign must have at least 1 Step to be activated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Make sure time-based CRON jobs are also deleted."""
        if self.trigger_type == 'TIME':
            scheduler = get_scheduler(queue=get_queue("cron"))
            scheduler.cancel(self.trigger.rq_cron_job_id)
        super().delete(*args, **kwargs)


class TriggerEvent(BaseWorkspace):
    """
    Store information about an 'Event' trigger used in an Automation Campaign.

    An event trigger is defined by an event name such as i.e: 'Signed up' or 'Purchased'.
    Additionally, it can be filtered by event attributes sent with the event such as
    {"signup_date": "2023-01-30"} for example.

    As soon as a Contact triggers this event, he enters the related Automation Campaign.
    """

    name = models.CharField(max_length=50)
    with_attributes = models.JSONField(null=True, blank=True)
    automation_campaign = models.OneToOneField('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='event_trigger')


class TriggerPage(BaseWorkspace):
    """
    Store information about a 'Page' trigger used in an Automation Campaign.

    A page trigger is defined by a page name such as i.e: 'Pricing' or 'Home'.
    As soon as a Contact triggers this event, he enters the related Automation Campaign.
    """

    name = models.CharField(max_length=50)
    automation_campaign = models.OneToOneField('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='page_trigger')


class TriggerList(BaseWorkspace):
    """
    Store information about a 'List' trigger used in an Automation Campaign.

    A list trigger is defined by a List unique 'id' (pk).
    When a Contact is added to the choosen list, then he enters the related Automation Campaign.
    """

    list = models.ForeignKey('contacts.List', on_delete=models.CASCADE, null=True, blank=True)
    automation_campaign = models.OneToOneField('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='list_trigger')


class TriggerSegment(BaseWorkspace):
    """
    Store information about a 'Segment' trigger used in an Automation Campaign.

    A segment trigger is defined by a Segment unique 'id' (pk).
    When a Contact enters the choosen segment, then he enters the related Automation Campaign.
    """

    segment = models.ForeignKey('contacts.Segment', on_delete=models.CASCADE, null=True, blank=True)
    automation_campaign = models.OneToOneField('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='segment_trigger')


class TriggerEmail(BaseWorkspace):
    """
    Store information about an 'Email' trigger used in an Automation Campaign.

    An email trigger is defined by an Email ForeignKey and a type of action ("open", "click"...).
    When a Contact has done the specific action on the choosen Email, then he enters the
    related Automation Campaign.
    """
    from campaigns.models import CampaignActivity

    email = models.ForeignKey('emails.Email', on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=50, null=True, blank=True, choices=CampaignActivity.ACTIVITY_TYPES)
    automation_campaign = models.OneToOneField('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True,
                                               related_name='email_trigger')


class TriggerTime(BaseWorkspace):
    """
    Store information about a 'Time' trigger used in an Automation Campaign.

    A time trigger is defined by a time unit AND a time value. i.e: 2 days or 1 week...

    For example, if you choose 2 days, it means every 2 days all the Contacts will
    enter the Automation Campaign.
    """

    TIME_UNITS = [
        ('DAY', 'Day'),
        ('WEEK', 'Week'),
        ('MONTH', 'Month'),
        ('MONTH', 'Year'),
    ]

    unit = models.CharField(max_length=50, null=True, blank=True, choices=TIME_UNITS)
    value = models.IntegerField(null=True, blank=True, default=1)
    rq_cron_job_id = models.CharField(max_length=50, null=True, blank=True)
    automation_campaign = models.OneToOneField(
        'AutomationCampaign',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_trigger'
    )

    def save(self, *args, **kwargs):
        """Prevent creating a Time Trigger without a unit and value."""
        from automation.tasks import add_all_contacts_to_automation_campaign
        scheduler = get_scheduler(queue=get_queue("cron"))

        if self._state.adding is True:
            # Object creation
            job = scheduler.schedule(
                scheduled_time=datetime.utcnow(),
                func=add_all_contacts_to_automation_campaign,
                args=[self.automation_campaign_id],
                interval=60,
                repeat=None
            )
            self.rq_cron_job_id = job.id

        else:
            # Object update
            scheduler.cancel(self.rq_cron_job_id)
            new_job = scheduler.schedule(
                scheduled_time=datetime.utcnow(),
                func=add_all_contacts_to_automation_campaign,
                args=[self.automation_campaign_id],
                interval=60,
                repeat=None
            )
            self.rq_cron_job_id = new_job.id
        super().save(*args, **kwargs)


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

    class Meta:
        ordering = ["order"]

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

    @property
    def next_step(self):
        if self.has_next_step:
            return self.automation_campaign.steps.get(order=self.order + 1)
        return None


class StepSendEmail(BaseWorkspace):
    """Store information about the email to send in an Automation Campaign 'Send Email' Step."""

    step = models.OneToOneField('Step', on_delete=models.CASCADE, null=True, blank=True, related_name='send_email_step')
    email = models.ForeignKey('emails.Email', on_delete=models.CASCADE, null=True, blank=True)


class StepWait(BaseWorkspace):
    """Store information about the delay to wait in an Automation Campaign 'Wait' Step."""

    step = models.OneToOneField('Step', on_delete=models.CASCADE, null=True, blank=True, related_name='wait_step')
    delay = models.IntegerField(default=1)
    delay_unit = models.CharField(
        max_length=15,
        choices=(('days', 'Day'), ('hours', 'Hour'), ('weeks', 'Week'), ('minutes', 'Minute')),
        default='days'
    )


class AutomationCampaignContact(BaseWorkspace):
    """
    Store information about how a Contact is moving through the AutomationCampaign journey.

    Only Contacts currently in the Automation Campaign are stored in this table.
     >> This table data can also be accesses from 'AutomationCampaign.contacts.through.all()'

    ----------------
    1. The AutomationCampaignContact objects is created in the 'save()' method of other models
    such as 'Page' or 'Event'... (If there is an existing Trigger upon creation of Event for example).

    2. After object creation, the 'async_execute_current_step()' method is called to process the Step.

    3. At the end of the async step processing function (as long as there is a next step), we call
    the 'async_execute_current_step()' method again to keep going.
    """

    automation_campaign = models.ForeignKey('AutomationCampaign', on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True)
    current_step = models.ForeignKey('Step', on_delete=models.CASCADE, null=True, blank=True)

    def async_execute_current_step(self):
        """Execute the current step for the Contact in the Automation Campaign (with async task)."""
        if self.current_step.step_type == 'WAIT':
            delay = self.current_step.content.delay
            delay_unit = self.current_step.content.delay_unit
            queue = get_queue('default')
            queue.enqueue_in(timedelta(**{delay: delay_unit}), process_automation_step, self.id)
        else:
            # Process Step immediately (async)
            process_automation_step.delay(self.id)
