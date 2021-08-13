from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Carping API",
        default_version="v1",
        description="Carping Swagger API 문서",
        contact=openapi.Contact(email="ywchoi0625@gmail.com"),
        license=openapi.License(name="Copyright Yewon Choi, Chanjong Park"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
