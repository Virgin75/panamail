from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

from contacts import views

router = routers.SimpleRouter()
router.register(r'contacts', views.ContactViewSet, basename="contacts")
router.register(r'custom-fields', views.CustomFieldViewSet, basename="custom-fields")
list_router = ExtendedSimpleRouter()
(
    list_router.register(r'lists', views.ListViewSet, basename="lists")
    .register(
        r'contacts',
        views.NestedContactInListViewSet,
        basename="lists-contacts",
        parents_query_lookups=['lists']
    )
)
segment_router = ExtendedSimpleRouter()
(
    segment_router.register(r'segments', views.SegmentViewset, basename="segments")
    .register(
        r'groups',
        views.NestedGroupConditionsViewSet,
        basename="segments-groups",
        parents_query_lookups=['segments']
    )
)

urlpatterns = router.urls + list_router.urls + segment_router.urls
