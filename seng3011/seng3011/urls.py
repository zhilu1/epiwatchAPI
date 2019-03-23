from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from epiwatch.schema_view import my_get_swagger_view
from epiwatch.views import *
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view


schema_view = my_get_swagger_view()

# We use a single global DRF Router that routes views from all apps in project
router = DefaultRouter()

# app views and viewsets
router.register(r'article', ArticleViewSet, r"article")

urlpatterns = [
    # default django admin interface (currently unused)
    url(r'^admin/', include(admin.site.urls)),

    # root view of our REST api, generated by Django REST Framework's router
    url(r'^api/', include(router.urls, namespace='api')),

    # index page should be served by django to set cookies, headers etc.
    url('^$', schema_view),
]

# let django built-in server serve static and media content
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)