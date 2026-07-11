
from django.urls import path, include
from admin_panel.api.v1 import UserView, StatsView, UserActivityLogExcelView

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("user", UserView, basename="user")


urlpatterns = [
path("", include(router.urls)),
path("stats/", StatsView.as_view(), name="stats"),
path("log/excel/", StatsView.as_view(), name="log-excel")

]
