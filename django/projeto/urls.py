from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("api/", include("api.urls")),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path(
        "alterar-senha/",
        auth_views.PasswordChangeView.as_view(
            template_name="alterar-senha.html", success_url="/alterar-senha/confirma/"
        ),
        name="alterarsenha",
    ),
    path(
        "alterar-senha/confirma/",
        auth_views.PasswordChangeDoneView.as_view(template_name="confirma-senha.html"),
        name="confirmasenha",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html", next_page="/"),
        name="login",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html", next_page="/"),
        name="login",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
