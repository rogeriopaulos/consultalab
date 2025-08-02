from django.http import HttpResponseRedirect
from django.urls import reverse


class ForceChangePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se o usuário precisa trocar senha
        if (
            request.user.is_authenticated
            and not request.user.is_superuser
            and request.user.force_password_change
        ):
            # Permitir apenas URLs essenciais
            allowed_paths = [
                "/usuarios/",
                "/contas/",
                "/static/",
                "/media/",
                "/admin/",  # Permitir admin caso seja necessário
                "/__debug__/",  # Django Debug Toolbar
            ]

            # Verificar se a URL atual é permitida
            path_allowed = any(
                request.path_info.startswith(path) for path in allowed_paths
            )

            # Se não é uma requisição HTMX e não está em uma URL permitida, redirecionar
            if not request.headers.get("HX-Request") and not path_allowed:
                url = reverse("users:detail", kwargs={"pk": request.user.id})
                url = url + "?force_password_change=true"
                return HttpResponseRedirect(url)

        return self.get_response(request)
