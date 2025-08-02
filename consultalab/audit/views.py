from auditlog.models import LogEntry
from axes.models import AccessLog
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View

User = get_user_model()


class AdminSectionView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "audit/admin_section.html"
    permission_required = "users.access_admin_section"


class UsersView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        search_term = request.GET.get("search", "")

        if search_term:
            users_list = User.objects.filter(
                Q(name__icontains=search_term) | Q(email__icontains=search_term),
            ).order_by("-date_joined")
        else:
            users_list = User.objects.all().order_by("-date_joined")

        paginator = Paginator(users_list, 10)  # 10 usuários por página
        page_number = request.GET.get("page")
        users = paginator.get_page(page_number)

        # Se há um termo de busca, retorna apenas a tabela com paginação
        if search_term and request.headers.get("HX-Request"):
            return render(
                request,
                "audit/partials/includes/users_table_with_pagination.html",
                {"users": users, "search_term": search_term},
            )

        # Caso contrário, retorna a página completa
        return render(
            request,
            "audit/partials/users_list.html",
            {"users": users, "search_term": search_term},
        )


class UsersSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def post(self, request, *args, **kwargs):
        search_term = request.POST.get("search", "").strip()

        if search_term:
            users_list = User.objects.filter(
                Q(name__icontains=search_term) | Q(email__icontains=search_term),
            ).order_by("-date_joined")
        else:
            users_list = User.objects.all().order_by("-date_joined")

        paginator = Paginator(users_list, 10)  # 10 usuários por página
        page_number = request.GET.get("page", 1)
        users = paginator.get_page(page_number)

        return render(
            request,
            "audit/partials/includes/users_table_with_pagination.html",
            {"users": users, "search_term": search_term},
        )


class LogEntriesView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        log_entries_list = LogEntry.objects.all().order_by("-timestamp")

        paginator = Paginator(log_entries_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page")
        log_entries = paginator.get_page(page_number)

        return render(
            request,
            "audit/partials/log_entries_list.html",
            {"log_entries": log_entries},
        )


class AccessLogsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        access_logs_list = AccessLog.objects.all().order_by("-attempt_time")

        paginator = Paginator(access_logs_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page")
        access_logs = paginator.get_page(page_number)

        return render(
            request,
            "audit/partials/access_logs_list.html",
            {"access_logs": access_logs},
        )


class LogEntryDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        log_entry_id = kwargs.get("log_id")
        log_entry = LogEntry.objects.filter(id=log_entry_id).first()

        if not log_entry:
            return render(request, "audit/partials/log_entry_not_found.html")

        return render(
            request,
            "audit/partials/log_entry_detail.html",
            {"log_entry": log_entry},
        )
