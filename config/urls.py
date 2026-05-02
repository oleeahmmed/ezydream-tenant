"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.generic import RedirectView

from apps.core import admin_search_views

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/erp-search/items", admin_search_views.erp_search_items, name="admin_erp_search_items"),
    path(
        "admin/erp-search/warehouses",
        admin_search_views.erp_search_warehouses,
        name="admin_erp_search_warehouses",
    ),
    path(
        "admin/erp-search/gl-accounts",
        admin_search_views.erp_search_gl_accounts,
        name="admin_erp_search_gl_accounts",
    ),
    path("admin/", admin.site.urls),
]
