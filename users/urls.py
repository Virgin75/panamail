from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    SignUpView, 
    SignInView,
    RetrieveUpdateDestroyView,
    CreateCompanyView,
    RetrieveUpdateDestroyCompanyView,
    ListCreateWorkspaceView,
    RetrieveUpdateDestroyWorkspaceView,
    ListCreateMemberOfWorkspaceView,
    RetrieveUpdateDestroyMemberOfWorkspaceView,
    CreateInvitationView,
    ListCompanyMembers,
    DeleteMemberOfCompany,
    )

urlpatterns = [
    path('signup', SignUpView.as_view(), name="signupview"),
    path('signin', SignInView.as_view(), name='token_obtain_pair'),
    path('signin-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-profile', RetrieveUpdateDestroyView.as_view(), name="retrieveupdateview"),
    path('companies', CreateCompanyView.as_view(), name="createcompany"),
    path('company-members/', ListCompanyMembers.as_view(), name="listcompanymembers"),
    path('delete-company-member/<uuid:pk>', DeleteMemberOfCompany.as_view(), name="destroycompanymember"),
    path('my-company', RetrieveUpdateDestroyCompanyView.as_view(), name="retrieveupdatedestroycompany"),
    path('workspaces', ListCreateWorkspaceView.as_view(), name="createlistworkspaces"),
    path('workspaces/<uuid:pk>', RetrieveUpdateDestroyWorkspaceView.as_view(), name="retrieveupdatedestroyworkspace"),
    path('invitations/', CreateInvitationView.as_view(), name="createinvitation"),
    path('workspaces-members/', ListCreateMemberOfWorkspaceView.as_view(), name="addmemberofworkspace"),
    path('workspaces-members/<int:pk>', RetrieveUpdateDestroyMemberOfWorkspaceView.as_view(), name="retrieveupdatedestroymemberofworkspace"),

]