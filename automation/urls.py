from rest_framework import routers

from automation import views

router = routers.SimpleRouter()
router.register(r'automations', views.AutomationCampaignViewSet, basename="automations")
urlpatterns = router.urls
