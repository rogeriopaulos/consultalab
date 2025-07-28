from auditlog.models import LogEntry
from axes.models import AccessLog
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View

from consultalab.users.filters import UserFilter

User = get_user_model()


class AdminSectionView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "audit/admin_section.html"
    permission_required = "users.access_admin_section"


class UsersView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by("-date_joined")
        user_filter = UserFilter(request.GET, queryset=users)
        return render(
            request,
            "audit/partials/users_list.html",
            {"users": user_filter.qs, "form": user_filter.form},
        )


class LogEntriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        log_entries = LogEntry.objects.all().order_by("-timestamp")
        return render(
            request,
            "audit/partials/log_entries_list.html",
            {"log_entries": log_entries},
        )


class AccessLogsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        access_logs = AccessLog.objects.all().order_by("-attempt_time")
        return render(
            request,
            "audit/partials/access_logs_list.html",
            {"access_logs": access_logs},
        )
