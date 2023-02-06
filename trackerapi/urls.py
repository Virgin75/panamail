from rest_framework import routers

from trackerapi import views

router = routers.SimpleRouter()
router.register(r'api-keys', views.ApiKeyViewSet, basename="api-keys")
router.register(r'track-events', views.TrackEventsViewSet, basename="track-events")
router.register(r'track-pages', views.TrackPagesViewSet, basename="track-pages")
router.register(r'track-contacts', views.TrackContactViewSet, basename="track-contacts")

urlpatterns = router.urls
