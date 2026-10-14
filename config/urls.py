"""
NovaStore URL Configuration
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("catalog/", include("catalog.urls")),
    path("accounts/", include("accounts.urls")),
]

from django.views import defaults as default_views

# Preview routes for custom error pages
urlpatterns += [
    path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
    path("500/", default_views.server_error),
]

from django.views.static import serve
from django.urls import re_path

# Serve media files in all environments (including production when not using external object storage)
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
