from django.urls import path
from .views import ListCreateEmail, ListCreateSenderDomain, ListCreateSenderEmail

urlpatterns = [
    path('emails', ListCreateEmail.as_view(), name="listcreateemail"),
    path('sender-domains', ListCreateSenderDomain.as_view(), name="listcreatesenderdomain"),
    path('sender-emails', ListCreateSenderEmail.as_view(), name="listcreatesenderemail"),

]