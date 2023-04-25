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
from django.urls import path
from django.urls import path
from urls.views import create_url, get_url, get_url_stats, custom_404_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("url", create_url),
    path("url/<str:short_id>", get_url),
    path("url/<str:short_id>/statistics", get_url_stats),
    path("404/", custom_404_view, name="custom_404"),
]
