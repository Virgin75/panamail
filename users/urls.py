from django.urls import path
from .views import (
    SignUpView, 
    RetrieveUpdateDestroyView,
    CreateCompanyView,
    RetrieveUpdateDestroyCompanyView,
    ListCreateWorkspaceView,
    RetrieveUpdateDestroyWorkspaceView,
    ListCreateMemberOfWorkspaceView,
    RetrieveUpdateDestroyMemberOfWorkspaceView,
    ListSMTPProviderView
    )

urlpatterns = [
    path('signup', SignUpView.as_view(), name="signupview"),
    path('my-profile', RetrieveUpdateDestroyView.as_view(), name="retrieveupdateview"),
    path('companies', CreateCompanyView.as_view(), name="createcompany"),
    path('my-company', RetrieveUpdateDestroyCompanyView.as_view(), name="retrieveupdatedestroycompany"),
    path('workspaces', ListCreateWorkspaceView.as_view(), name="createlistworkspaces"),
    path('workspaces/<int:pk>', RetrieveUpdateDestroyWorkspaceView.as_view(), name="retrieveupdatedestroyworkspace"),
    path('workspaces-members/', ListCreateMemberOfWorkspaceView.as_view(), name="addlistmemberofworkspace"),
    path('workspaces-members/<int:pk>', RetrieveUpdateDestroyMemberOfWorkspaceView.as_view(), name="retrieveupdatedestroymemberofworkspace"),
    path('smtp', ListSMTPProviderView.as_view(), name="listsmtpproviders"),

]