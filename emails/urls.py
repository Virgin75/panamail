from django.urls import path
from rest_framework import routers
from .views import (
    EmailViewset,
    ListCreateEmail, 
    ListCreateSenderDomain, 
    ListCreateSenderEmail,
    RetrieveUpdateDestroyEmail,
    RetrieveUpdateDestroySenderDomain,
    RetrieveUpdateDestroySenderEmail,
)


router = routers.SimpleRouter()
router.register(r'emails', EmailViewset, basename="emails")
urlpatterns = router.urls

"""
urlpatterns = [
    path('emails', ListCreateEmail.as_view(), name="listcreateemail"),
    path('emails/<int:pk>', RetrieveUpdateDestroyEmail.as_view(), name="retrieveupdatedestroyemail"),
    path('sender-domains', ListCreateSenderDomain.as_view(), name="listcreatesenderdomain"),
    path('sender-domains/<int:pk>', RetrieveUpdateDestroySenderDomain.as_view(), name="retrieveupdatedestroyenderdomain"),
    path('sender-emails', ListCreateSenderEmail.as_view(), name="listcreatesenderemail"),
    path('sender-emails/<int:pk>', RetrieveUpdateDestroySenderEmail.as_view(), name="retrieveupdatedestroyenderemail"),

]"""