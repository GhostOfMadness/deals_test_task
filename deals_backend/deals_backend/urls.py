from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.contrib import admin
from django.urls import include, path


schema_view = get_schema_view(
    openapi.Info(
        title='Deals API',
        default_version='v1',
        description='Документация по API проекта Deals',
        contact=openapi.Contact(email='foo@bar.com'),
        license=openapi.License(name='BSD Licence'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/', include('api.urls', namespace='api')),
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='redoc',
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='swagger',
    ),
]
