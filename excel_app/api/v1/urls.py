
from django.urls import path, include
from excel_app.api.v1 import (
    AreaView,
    BoardOfTrusteeGroupedListView,
    BoardOfTrusteeListView,
    CertificateTypeListView,
    DocumentView,
    FieldsCsvExportView,
    FieldsExcelExportView,
    NeighborhoodListView,
    SubAreaListView,
    UpdateDocumentView,
    UserActivityLogListView,
    UserSearchView,
    LastBoardOfTrusteeLogAPIView
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("document", UpdateDocumentView, basename="document")

urlpatterns = [
    path("area/list/", AreaView.as_view(), name="area-list"),
    path("sub-area/list/", SubAreaListView.as_view(), name="sub-area-list"),
    path("neighborhood/list/", NeighborhoodListView.as_view(), name="neighborhood-list"),
    path("board-of-trustee/list/", BoardOfTrusteeListView.as_view(), name="board-of-trustee-list"),
    path("board-of-trustee/grouped/", BoardOfTrusteeGroupedListView.as_view(), name="board-of-trustee-grouped-list"),
    path("certificate-type/list/", CertificateTypeListView.as_view(), name="certificate-type-list"),
    path("document/list/", DocumentView.as_view(), name="document-list"),
    path("logs/list/", UserActivityLogListView.as_view(), name="logs-list"),
    path("user/search/", UserSearchView.as_view(), name="user-search"),

    path("fields/export-csv/", FieldsCsvExportView.as_view(), name="fields-export-csv"),
    path("fields/export-excel/", FieldsExcelExportView.as_view(), name="fields-export-excel"),
     path(
        "fields/<int:document_id>/logs/board-of-trustees/last/",
        LastBoardOfTrusteeLogAPIView.as_view(),
        name="last_board_log"
    ),
    path("", include(router.urls)),
]
