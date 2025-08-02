import json

from allauth.account.forms import AddEmailForm
from allauth.account.forms import ChangePasswordForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


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
