from .views.area import AreaView
from .views.documents import DocumentView, UpdateDocumentView
from .views.search import UserSearchView
from .views.excel import FieldsCsvExportView, FieldsExcelExportView
from .views.logs import UserActivityLogListView, LastBoardOfTrusteeLogAPIView

from .views.extra import (
    BoardOfTrusteeListView,
    BoardOfTrusteeGroupedListView,
    CertificateTypeListView,
    NeighborhoodListView,
    SubAreaListView,
)
