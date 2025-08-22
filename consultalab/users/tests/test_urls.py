from django.urls import resolve
from django.urls import reverse

from consultalab.users.models import User


def test_detail(user: User):
    assert reverse("users:detail", kwargs={"pk": user.pk}) == f"/usuarios/{user.pk}/"
    assert resolve(f"/usuarios/{user.pk}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update") == "/usuarios/~editar/"
    assert resolve("/usuarios/~editar/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/usuarios/~redirecionar/"
    assert resolve("/usuarios/~redirecionar/").view_name == "users:redirect"
