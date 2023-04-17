from django.db import models

from commons.models import BaseWorkspace


class AutomationCampaign(BaseWorkspace):
    """
    An automation campaign is a set of actions executed automatically in
    response to a trigger event.

     >> A trigger event might be :
        - A contact has viewed a new page on your website
        - A contact has triggered a new custom event
        - A contact has done something with an email (open, click, etc.)
        - A contact has subscribed to a list
    >> An action can be:
        - Send an email
        - Update a contact attribute
        - Send a POST request to a webhook
     """

    STATUS = [
        ('DRAFT', "Automation campaign is in Draft."),
        ('ACTIVE', 'Automation campaign is active and emails are being sent.'),
        ('PAUSED', 'Automation campaign is stopped.'),
    ]

    name = models.CharField(max_length=89)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS[0][0])
    trigger = models.ForeignKey('Trigger', on_delete=models.CASCADE, null=True, blank=True)
