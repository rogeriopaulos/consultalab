import json

from allauth.account.forms import AddEmailForm
from allauth.account.forms import ChangePasswordForm
from allauth.account.views import EmailView as AllauthEmailView
from allauth.account.views import PasswordChangeView as AllauthPasswordChangeView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.views.generic import View

from consultalab.users.forms import UserCreationForm
from consultalab.users.forms import UserUpdateForm

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_object(self, queryset=None):
        if self.request.user.id != self.kwargs["pk"]:
            raise PermissionDenied
        return self.request.user


user_detail_view = UserDetailView.as_view()


class UserDetailModalView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"
    template_name = "audit/partials/user_detail.html"

    def get_success_url(self) -> str:
        return reverse("users:detail", kwargs={"id": self.object.id})


user_detail_modal_view = UserDetailModalView.as_view()


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(
            request,
            "audit/partials/user_form.html",
            {"form": form},
        )

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Criar trigger com mensagem de sucesso usando JSON
            trigger_data = json.dumps(
                {
                    "closeModal": True,
                    "refreshUsers": True,
                    "showMessageCreatedUser": {
                        "message": f'Usuário "{user.name}" foi criado com sucesso!',
                        "type": "success",
                    },
                },
            )

            response = HttpResponse("")
            response["HX-Trigger"] = trigger_data
            return response

        return render(
            request,
            "audit/partials/user_form.html",
            {"form": form},
        )


user_create_view = UserCreateView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["name"]

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)

        # Se for uma requisição HTMX, retornar apenas o conteúdo atualizado
        if self.request.headers.get("HX-Request"):
            # Criar trigger com mensagem de sucesso usando JSON
            msg = f'Nome alterado para "{self.object.name}" com sucesso!'
            trigger_data = json.dumps(
                {
                    "showMessageCreatedUser": {
                        "message": msg,
                        "type": "success",
                    },
                },
            )

            response = render(
                self.request,
                "users/detail/partials/name_display.html",
                {"user": self.object},
            )
            response["HX-Trigger"] = trigger_data
            return response

        return response

    def form_invalid(self, form):
        # Se for uma requisição HTMX, retornar o formulário com erros
        if self.request.headers.get("HX-Request"):
            return render(
                self.request,
                "users/detail/partials/name_edit.html",
                {"user": self.get_object(), "form": form},
            )

        return super().form_invalid(form)


user_update_view = UserUpdateView.as_view()


class UserNameEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user

        # Se for um cancelamento, retornar a view normal do nome
        if request.GET.get("cancel"):
            return render(
                request,
                "users/detail/partials/name_display.html",
                {"user": user},
            )

        return render(
            request,
            "users/detail/partials/name_edit.html",
            {"user": user},
        )


user_name_edit_view = UserNameEditView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class UserAdminSectionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.access_admin_section"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.get("id"))
        if not user:
            return HttpResponse(status=404)
        form = UserUpdateForm(instance=user)
        return render(
            request,
            "audit/partials/user_form.html",
            {"form": form, "update_form": True},
        )

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.get("id"))
        if not user:
            return HttpResponse(status=404)
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            trigger_data = json.dumps(
                {
                    "closeModal": True,
                    "refreshUsers": True,
                    "showMessageCreatedUser": {
                        "message": f'Usuário "{user.name}" foi atualizado com sucesso!',
                        "type": "success",
                    },
                },
            )

            response = HttpResponse("")
            response["HX-Trigger"] = trigger_data
            return response
        return render(
            request,
            "audit/partials/user_form.html",
            {"form": form, "update_form": True},
        )


user_admin_section_update_view = UserAdminSectionUpdateView.as_view()


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return HttpResponse(status=404)

        # Se for uma requisição HTMX para o seletor #name-display,
        # retornar apenas a parte do nome
        if (
            request.headers.get("HX-Request")
            and request.headers.get("HX-Target") == "name-container"
        ):
            return render(
                request,
                "users/detail/partials/name_display.html",
                {"user": user},
            )

        return render(
            request,
            "users/detail/tabs/profile.html",
            {"user": user},
        )


user_profile_view = UserProfileView.as_view()


class UserEmailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "users/detail/tabs/email.html",
            {"email_form": AddEmailForm(user=request.user)},
        )


user_email_view = UserEmailView.as_view()


class UserSecurityView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Verificar force_password_change tanto no parâmetro GET quanto no usuário
        force_password_change = (
            request.GET.get("force_password_change") == "true"
            or request.user.force_password_change
        )

        return render(
            request,
            "users/detail/tabs/security.html",
            {
                "password_change_form": ChangePasswordForm(user=request.user),
                "force_password_change": force_password_change,
            },
        )


user_security_view = UserSecurityView.as_view()


class CustomEmailView(AllauthEmailView):
    """View customizada para gerenciar e-mails que retorna o conteúdo
    da aba de e-mail"""

    def get_success_url(self):
        # Se for uma requisição HTMX, não redirecionamos
        if self.request.headers.get("HX-Request"):
            return None
        return super().get_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        # Se for uma requisição HTMX, renderizar a aba de e-mail atualizada
        if self.request.headers.get("HX-Request"):
            # Determinar a mensagem de sucesso baseada na ação
            action_add = self.request.POST.get("action_add")
            if action_add:
                message = "E-mail adicionado com sucesso!"
            else:
                action_primary = self.request.POST.get("action_primary")
                action_send = self.request.POST.get("action_send")
                action_remove = self.request.POST.get("action_remove")

                if action_primary:
                    message = "E-mail primário definido com sucesso!"
                elif action_send:
                    message = "E-mail de verificação reenviado com sucesso!"
                elif action_remove:
                    message = "E-mail removido com sucesso!"
                else:
                    message = "Operação realizada com sucesso!"

            # Criar trigger com mensagem de sucesso
            trigger_data = json.dumps(
                {
                    "showMessageCreatedUser": {
                        "message": message,
                        "type": "success",
                    },
                },
            )

            # Renderizar a aba de e-mail atualizada
            response = render(
                self.request,
                "users/detail/tabs/email.html",
                {"email_form": AddEmailForm(user=self.request.user)},
            )
            response["HX-Trigger"] = trigger_data
            return response

        return response

    def form_invalid(self, form):
        # Se for uma requisição HTMX, renderizar a aba com erros
        if self.request.headers.get("HX-Request"):
            return render(
                self.request,
                "users/detail/tabs/email.html",
                {"email_form": form},
            )
        return super().form_invalid(form)


custom_email_view = CustomEmailView.as_view()


class CustomPasswordChangeView(AllauthPasswordChangeView):
    """View customizada para mudança de senha que retorna o
    conteúdo da aba de segurança"""

    def get_success_url(self):
        # Se for uma requisição HTMX, não redirecionamos
        if self.request.headers.get("HX-Request"):
            return None
        return super().get_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        # Se for uma requisição HTMX, renderizar a aba de segurança atualizada
        if self.request.headers.get("HX-Request"):
            # Remover o force_password_change do usuário se existir
            if hasattr(self.request.user, "force_password_change"):
                self.request.user.force_password_change = False
                self.request.user.save()

            # Criar trigger com mensagem de sucesso
            trigger_data = json.dumps(
                {
                    "showMessageCreatedUser": {
                        "message": "Senha alterada com sucesso!",
                        "type": "success",
                    },
                },
            )

            # Renderizar a aba de segurança atualizada
            response = render(
                self.request,
                "users/detail/tabs/security.html",
                {
                    "password_change_form": ChangePasswordForm(user=self.request.user),
                    "force_password_change": False,  # Reset após mudança de senha
                },
            )
            response["HX-Trigger"] = trigger_data
            return response

        return response

    def form_invalid(self, form):
        # Se for uma requisição HTMX, renderizar a aba com erros
        if self.request.headers.get("HX-Request"):
            force_password_change = self.request.GET.get(
                "force_password_change",
            ) == "true" or getattr(self.request.user, "force_password_change", False)
            return render(
                self.request,
                "users/detail/tabs/security.html",
                {
                    "password_change_form": form,
                    "force_password_change": force_password_change,
                },
            )
        return super().form_invalid(form)


custom_password_change_view = CustomPasswordChangeView.as_view()
