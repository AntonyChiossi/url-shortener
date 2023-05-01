"""
URL configuration for shortener project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

from urls.views import (
    UrlView,
    get_url,
    get_url_stats,
    custom_404_view,
    register,
    login,
    refresh_token,
    angular,
)

urlpatterns = [
    # path(
    #     "app",
    #     serve,
    #     kwargs={
    #         "path": "index.html",
    #         "document_root": "frontend/shortener/dist/shortener/",
    #     },
    # ),
    # static("", document_root="frontend/shortener/dist/shortener/"),
    # auth
    path("api/register", register),
    path("api/login", login),
    path("api/refresh", refresh_token),
    # Urls
    path("api/url", UrlView.as_view()),
    re_path(r"^(?P<short_id>[a-zA-Z0-9]{12})[\/]*$", get_url),
    re_path(r"^(?P<short_id>[a-zA-Z0-9]{12})[\/]*\+[\/]*$", get_url_stats),
    # others
    path("404/", custom_404_view, name="custom_404"),
    path("<path:route>", RedirectView.as_view(url="/404/")),
]
