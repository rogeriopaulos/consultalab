from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth.models import Permission
from django.forms import CharField
from django.forms import EmailField
from django.forms import ModelChoiceField
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Department
from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User
        field_classes = {"email": EmailField}


# type: ignore[name-defined]  # django-stubs is missing the class,
# thats why the error is thrown: typeddjango/django-stubs#2555
class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    # type: ignore[name-defined]
    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class UserCreationForm(forms.UserCreationForm):
    name = CharField(
        max_length=255,
        required=True,
        label="Nome Completo",
        strip=True,
    )
    department = ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        label="Órgão/Unidade",
        required=True,
        empty_label="Selecione um órgão/unidade",
    )

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "department",
            "password1",
            "password2",
            "force_password_change",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas as permissões específicas do usuário
        allowed_permissions = [
            "users.access_admin_section",
            "users.can_request_pix",
            "users.can_request_ccs",
        ]
        self.fields["user_permissions"].queryset = Permission.objects.filter(
            content_type__app_label="users",
            codename__in=[perm.split(".")[1] for perm in allowed_permissions],
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            msg = _("Este e-mail já está cadastrado.")
            raise forms.ValidationError(msg)
        return email


class UserUpdateForm(ModelForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "name",
            "email",
            "department",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas as permissões específicas do usuário
        allowed_permissions = [
            "users.access_admin_section",
            "users.can_request_pix",
            "users.can_request_ccs",
        ]
        self.fields["user_permissions"].queryset = Permission.objects.filter(
            content_type__app_label="users",
            codename__in=[perm.split(".")[1] for perm in allowed_permissions],
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            msg = _("Este e-mail já está cadastrado.")
            raise forms.ValidationError(msg)
        return email
