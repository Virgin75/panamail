from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

from users import views

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet, basename="users")

wks_router = ExtendedSimpleRouter()
(
    wks_router.register(r'workspaces', views.WorkspaceViewSet, basename="workspaces")
    .register(
        r'members',
        views.NestedWorkspaceMembersViewset,
        basename="workspaces-members",
        parents_query_lookups=['workspaces']
    )
)

urlpatterns = router.urls + wks_router.urls
