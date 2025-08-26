import logging

from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class ForceTwoFactorMiddleware:
    """
    Middleware que força todos os usuários autenticados a configurar 2FA.
    Usuários sem 2FA são redirecionados para o fluxo de configuração MFA.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se o usuário está autenticado
        if request.user.is_authenticated:
            logger.debug(
                "User %s authenticated, checking MFA status",
                request.user.email,
            )

            # Verificar se o usuário tem 2FA configurado
            if not self._user_has_mfa(request.user):
                logger.debug("User %s does not have MFA configured", request.user.email)

                # URLs que devem permanecer acessíveis sem 2FA
                allowed_paths = [
                    "/contas/2fa/",  # URLs do allauth MFA (correto!)
                    "/contas/logout/",  # Logout
                    "/contas/password/reset/",  # Reset de senha
                    "/static/",  # Arquivos estáticos
                    "/media/",  # Arquivos de mídia
                    "/admin/",  # Admin (pode ser necessário para recuperação)
                    "/__debug__/",  # Django Debug Toolbar
                    "/400/",  # Páginas de erro
                    "/403/",
                    "/404/",
                    "/500/",
                ]

                # Verificar se a URL atual é permitida
                path_allowed = any(
                    request.path_info.startswith(path) for path in allowed_paths
                )

                logger.debug("Path %s allowed: %s", request.path_info, path_allowed)

                # Se não é uma URL permitida, redirecionar para configuração MFA
                if not path_allowed:
                    # Preservar a URL de destino usando next
                    next_url = request.get_full_path()
                    mfa_setup_url = "/contas/2fa/totp/activate/"
                    separator = "&" if "?" in mfa_setup_url else "?"
                    redirect_url = f"{mfa_setup_url}{separator}next={next_url}"
                    logger.debug("Redirecting to: %s", redirect_url)
                    return redirect(redirect_url)
            else:
                logger.debug("User %s has MFA configured", request.user.email)

        return self.get_response(request)

    def _user_has_mfa(self, user):
        """
        Verifica se o usuário tem 2FA configurado.
        Usa os modelos do allauth.mfa para verificar dispositivos ativos.
        """
        try:
            # Verificar se o allauth.mfa está instalado
            if not apps.is_installed("allauth.mfa"):
                logger.debug("allauth.mfa not installed, skipping MFA check")
                return True  # Se MFA não está configurado, pular verificação

            # Importar dinamicamente para evitar erros de importação
            from allauth.mfa.models import Authenticator

            # Verificar se o usuário tem pelo menos um autenticador TOTP ativo
            # (códigos de recuperação são opcionais e criados automaticamente)
            has_mfa = Authenticator.objects.filter(
                user=user,
                type="totp",
            ).exists()

            logger.debug("User %s MFA status: %s", user.email, has_mfa)
        except ImportError:
            # Em caso de erro, assumir que não tem MFA configurado para ser seguro
            logger.exception("Error checking MFA status for user %s", user.email)
            return False
        else:
            return has_mfa


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
