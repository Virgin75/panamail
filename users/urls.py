from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
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
    path('signin', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signin-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-profile', RetrieveUpdateDestroyView.as_view(), name="retrieveupdateview"),
    path('companies', CreateCompanyView.as_view(), name="createcompany"),
    path('my-company', RetrieveUpdateDestroyCompanyView.as_view(), name="retrieveupdatedestroycompany"),
    path('workspaces', ListCreateWorkspaceView.as_view(), name="createlistworkspaces"),
    path('workspaces/<int:pk>', RetrieveUpdateDestroyWorkspaceView.as_view(), name="retrieveupdatedestroyworkspace"),
    #invite user to workspace
    #edit rights & delete user from workspace
    path('workspaces-members/', ListCreateMemberOfWorkspaceView.as_view(), name="addlistmemberofworkspace"),
    path('workspaces-members/<int:pk>', RetrieveUpdateDestroyMemberOfWorkspaceView.as_view(), name="retrieveupdatedestroymemberofworkspace"),
    path('smtp', ListSMTPProviderView.as_view(), name="listsmtpproviders"),

]