from auditlog.models import LogEntry
from axes.models import AccessLog
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.dateparse import parse_date
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
        # Obter parâmetros de filtro
        actor_search = request.GET.get("actor", "").strip()
        date_from = request.GET.get("date_from", "").strip()
        date_to = request.GET.get("date_to", "").strip()

        # Começar com todos os logs
        log_entries_list = LogEntry.objects.all()

        # Filtrar por usuário (actor)
        if actor_search:
            log_entries_list = log_entries_list.filter(
                Q(actor__name__icontains=actor_search)
                | Q(actor__email__icontains=actor_search),
            )

        # Filtrar por período de data
        if date_from:
            try:
                parsed_date_from = parse_date(date_from)
                if parsed_date_from:
                    log_entries_list = log_entries_list.filter(
                        timestamp__date__gte=parsed_date_from,
                    )
            except ValueError:
                pass

        if date_to:
            try:
                parsed_date_to = parse_date(date_to)
                if parsed_date_to:
                    log_entries_list = log_entries_list.filter(
                        timestamp__date__lte=parsed_date_to,
                    )
            except ValueError:
                pass

        log_entries_list = log_entries_list.order_by("-timestamp")

        paginator = Paginator(log_entries_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page")
        log_entries = paginator.get_page(page_number)

        # Se há filtros aplicados e é uma requisição HTMX, retorna apenas a tabela
        if (actor_search or date_from or date_to) and request.headers.get("HX-Request"):
            return render(
                request,
                "audit/partials/includes/log_entries_table_with_pagination.html",
                {
                    "log_entries": log_entries,
                    "actor_search": actor_search,
                    "date_from": date_from,
                    "date_to": date_to,
                },
            )

        return render(
            request,
            "audit/partials/log_entries_list.html",
            {
                "log_entries": log_entries,
                "actor_search": actor_search,
                "date_from": date_from,
                "date_to": date_to,
            },
        )


class LogEntriesSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def post(self, request, *args, **kwargs):
        # Obter parâmetros de filtro
        actor_search = request.POST.get("actor", "").strip()
        date_from = request.POST.get("date_from", "").strip()
        date_to = request.POST.get("date_to", "").strip()

        # Começar com todos os logs
        log_entries_list = LogEntry.objects.all()

        # Filtrar por usuário (actor)
        if actor_search:
            log_entries_list = log_entries_list.filter(
                Q(actor__name__icontains=actor_search)
                | Q(actor__email__icontains=actor_search),
            )

        # Filtrar por período de data
        if date_from:
            try:
                from django.utils.dateparse import parse_date

                parsed_date_from = parse_date(date_from)
                if parsed_date_from:
                    log_entries_list = log_entries_list.filter(
                        timestamp__date__gte=parsed_date_from,
                    )
            except ValueError:
                pass

        if date_to:
            try:
                from django.utils.dateparse import parse_date

                parsed_date_to = parse_date(date_to)
                if parsed_date_to:
                    log_entries_list = log_entries_list.filter(
                        timestamp__date__lte=parsed_date_to,
                    )
            except ValueError:
                pass

        log_entries_list = log_entries_list.order_by("-timestamp")

        paginator = Paginator(log_entries_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page", 1)
        log_entries = paginator.get_page(page_number)

        return render(
            request,
            "audit/partials/includes/log_entries_table_with_pagination.html",
            {
                "log_entries": log_entries,
                "actor_search": actor_search,
                "date_from": date_from,
                "date_to": date_to,
            },
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


class AccessLogsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        # Obter parâmetros de filtro
        username_search = request.GET.get("username", "").strip()
        date_from = request.GET.get("date_from", "").strip()
        date_to = request.GET.get("date_to", "").strip()

        # Começar com todos os logs de acesso
        access_logs_list = AccessLog.objects.all()

        # Filtrar por usuário (username)
        if username_search:
            access_logs_list = access_logs_list.filter(
                username__icontains=username_search,
            )

        # Filtrar por período de data
        if date_from:
            try:
                parsed_date_from = parse_date(date_from)
                if parsed_date_from:
                    access_logs_list = access_logs_list.filter(
                        attempt_time__date__gte=parsed_date_from,
                    )
            except ValueError:
                pass

        if date_to:
            try:
                parsed_date_to = parse_date(date_to)
                if parsed_date_to:
                    access_logs_list = access_logs_list.filter(
                        attempt_time__date__lte=parsed_date_to,
                    )
            except ValueError:
                pass

        access_logs_list = access_logs_list.order_by("-attempt_time")

        paginator = Paginator(access_logs_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page")
        access_logs = paginator.get_page(page_number)

        # Se há filtros aplicados e é uma requisição HTMX, retorna apenas a tabela
        if (username_search or date_from or date_to) and request.headers.get(
            "HX-Request",
        ):
            return render(
                request,
                "audit/partials/includes/access_logs_table_with_pagination.html",
                {
                    "access_logs": access_logs,
                    "username_search": username_search,
                    "date_from": date_from,
                    "date_to": date_to,
                },
            )

        return render(
            request,
            "audit/partials/access_logs_list.html",
            {
                "access_logs": access_logs,
                "username_search": username_search,
                "date_from": date_from,
                "date_to": date_to,
            },
        )


class AccessLogsSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def post(self, request, *args, **kwargs):
        # Obter parâmetros de filtro
        username_search = request.POST.get("username", "").strip()
        date_from = request.POST.get("date_from", "").strip()
        date_to = request.POST.get("date_to", "").strip()

        # Começar com todos os logs de acesso
        access_logs_list = AccessLog.objects.all()

        # Filtrar por usuário (username)
        if username_search:
            access_logs_list = access_logs_list.filter(
                username__icontains=username_search,
            )

        # Filtrar por período de data
        if date_from:
            try:
                from django.utils.dateparse import parse_date

                parsed_date_from = parse_date(date_from)
                if parsed_date_from:
                    access_logs_list = access_logs_list.filter(
                        attempt_time__date__gte=parsed_date_from,
                    )
            except ValueError:
                pass

        if date_to:
            try:
                from django.utils.dateparse import parse_date

                parsed_date_to = parse_date(date_to)
                if parsed_date_to:
                    access_logs_list = access_logs_list.filter(
                        attempt_time__date__lte=parsed_date_to,
                    )
            except ValueError:
                pass

        access_logs_list = access_logs_list.order_by("-attempt_time")

        paginator = Paginator(access_logs_list, 10)  # 10 entradas por página
        page_number = request.GET.get("page", 1)
        access_logs = paginator.get_page(page_number)

        return render(
            request,
            "audit/partials/includes/access_logs_table_with_pagination.html",
            {
                "access_logs": access_logs,
                "username_search": username_search,
                "date_from": date_from,
                "date_to": date_to,
            },
        )
