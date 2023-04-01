from rest_framework import routers

from campaigns import views

router = routers.SimpleRouter()
router.register(r'campaigns', views.CampaignViewSet, basename="campaigns")
urlpatterns = router.urls
