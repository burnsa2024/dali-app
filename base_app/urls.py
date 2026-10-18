"""
URL configuration for dali_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from .views import static_view, register, search_submitted, search
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', static_view, {'template': 'home.html'}, name='home_page'),
    path('search/', search, name='search_page'),
    path("register/", register, name="register_page"),
    path("tools/", static_view, {'template': 'tools.html'}, name='tools_page'),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search/submitted/", search_submitted, name="search_submitted_page"),

]
