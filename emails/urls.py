from django.urls import path
from .views import (
    ListCreateEmail, 
    ListCreateSenderDomain, 
    ListCreateSenderEmail,
    RetrieveUpdateDestroyEmail,
)

urlpatterns = [
    path('emails', ListCreateEmail.as_view(), name="listcreateemail"),
    path('emails/<int:pk>', RetrieveUpdateDestroyEmail.as_view(), name="retrieveupdatedestroyemail"),
    path('sender-domains', ListCreateSenderDomain.as_view(), name="listcreatesenderdomain"),
    path('sender-emails', ListCreateSenderEmail.as_view(), name="listcreatesenderemail"),

]