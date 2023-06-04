from rest_framework import routers

from automation import views

router = routers.SimpleRouter()
router.register(r'automations', views.AutomationCampaignViewSet, basename="automations")
# Triggers
router.register(r'automation-event-triggers', views.TriggerEventViewset, basename="automation-event-triggers")
router.register(r'automation-page-triggers', views.TriggerPageViewset, basename="automation-page-triggers")
router.register(r'automation-list-triggers', views.TriggerListViewset, basename="automation-list-triggers")
router.register(r'automation-segment-triggers', views.TriggerSegmentViewset, basename="automation-segment-triggers")
router.register(r'automation-time-triggers', views.TriggerTimeViewset, basename="automation-time-triggers")
router.register(r'automation-email-triggers', views.TriggerEmailViewset, basename="automation-email-triggers")
# Steps
router.register(r'automation-steps', views.StepViewset, basename="automation-steps")
router.register(r'automation-email-steps', views.StepSendEmailViewset, basename="automation-email-steps")
router.register(r'automation-wait-steps', views.StepWaitViewset, basename="automation-wait-steps")

urlpatterns = router.urls
