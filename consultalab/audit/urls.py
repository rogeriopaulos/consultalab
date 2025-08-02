from django.urls import path

from consultalab.audit.views import AccessLogsSearchView
from consultalab.audit.views import AccessLogsView
from consultalab.audit.views import AdminSectionView
from consultalab.audit.views import LogEntriesSearchView
from consultalab.audit.views import LogEntriesView
from consultalab.audit.views import LogEntryDetailView
from consultalab.audit.views import UsersSearchView
from consultalab.audit.views import UsersView

app_name = "audit"
urlpatterns = [
    path("", AdminSectionView.as_view(), name="admin_section"),
]
htmx_urlpatterns = [
    path("tab1/usuarios/", UsersView.as_view(), name="users"),
    path("tab1/usuarios/busca/", UsersSearchView.as_view(), name="users_search"),
    path("tab2/logs/", LogEntriesView.as_view(), name="log_entries"),
    path("tab2/logs/busca/", LogEntriesSearchView.as_view(), name="log_entries_search"),
    path(
        "tab2/logs/<int:log_id>/detalhes/",
        LogEntryDetailView.as_view(),
        name="log_entry_detail",
    ),
    path("tab3/acessos/", AccessLogsView.as_view(), name="access_logs"),
    path(
        "tab3/acessos/busca/",
        AccessLogsSearchView.as_view(),
        name="access_logs_search",
    ),
]
urlpatterns += htmx_urlpatterns
