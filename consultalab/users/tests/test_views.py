from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from consultalab.users.forms import UserAdminChangeForm
from consultalab.users.models import User
from consultalab.users.views import UserRedirectView
from consultalab.users.views import UserUpdateView
from consultalab.users.views import user_detail_view

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/usuarios/{user.pk}/"

    def test_get_object(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request
        view.object = user  # Set the object as it would be set by UpdateView

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        response = view.form_valid(form)

        # Para requisições não-HTMX, o método apenas retorna a resposta normal
        # sem adicionar mensagens ao sistema de mensagens do Django
        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == []

        # Verificar que a resposta foi retornada corretamente
        assert response is not None

    def test_form_valid_htmx_request(self, user: User, rf: RequestFactory):
        """Testa o comportamento do form_valid para requisições HTMX"""
        view = UserUpdateView()
        request = rf.post("/fake-url/")

        # Simular uma requisição HTMX
        request.META["HTTP_HX_REQUEST"] = "true"

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request
        view.object = user  # Set the object as it would be set by UpdateView

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        response = view.form_valid(form)

        # Para requisições HTMX, o método retorna um template renderizado
        # com um trigger HX-Trigger no header
        assert response is not None
        assert "HX-Trigger" in response

        # Verificar que não usa o sistema de mensagens do Django para HTMX
        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == []


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/usuarios/{user.pk}/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = user  # Usar o mesmo usuário para requisição e detalhes
        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == HTTPStatus.OK

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, pk=user.pk)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"
