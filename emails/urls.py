from rest_framework import routers

from emails import views

router = routers.SimpleRouter()
router.register(r'emails', views.EmailViewset, basename="emails")
router.register(r'sender-domains', views.SenderDomainViewset, basename="sender-domains")
router.register(r'sender-emails', views.SenderEmailViewset, basename="sender-emails")
urlpatterns = router.urls
