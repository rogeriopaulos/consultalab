from django.urls import path

from .views import user_admin_section_update_view
from .views import user_create_view
from .views import user_detail_modal_view
from .views import user_detail_view
from .views import user_email_view
from .views import user_profile_view
from .views import user_redirect_view
from .views import user_security_view
from .views import user_update_view

app_name = "users"
urlpatterns = [
    path("~redirecionar/", view=user_redirect_view, name="redirect"),
    path("~editar/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("<int:id>/modal/", view=user_detail_modal_view, name="detail_modal"),
    path("cadastrar/", view=user_create_view, name="create"),
    path(
        "admin-usuario/<int:id>/editar/",
        view=user_admin_section_update_view,
        name="user_admin_section_update_view",
    ),
]

partials = [
    path("perfil/", view=user_profile_view, name="profile"),
    path("email/", view=user_email_view, name="email_tab"),
    path("seguranca/", view=user_security_view, name="security_tab"),
]

urlpatterns += partials
