from django.urls import path
from .views import SignUpView, RetrieveUpdateView

urlpatterns = [
    path('signup', SignUpView.as_view(), name="signupview"),
    path('my-profile', RetrieveUpdateView.as_view(), name="retrieveupdateview"),
]