from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views import defaults as default_views

from carping.docs import schema_view

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    # path('accounts/', include('dj_rest_auth.urls')),
    # path('accounts/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls'), name="socialaccount_signup"),
    path('accounts/', include('accounts.urls')),
    path('camps/', include('camps.urls')),
    path('posts/', include('posts.urls')),
    path('comments/', include('comments.urls')),
    path('mypage/', include('mypage.urls')),
    path('search/', include('search.urls')),
]

# Swagger
urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui',),
    path("redoc/", schema_view.with_ui("redoc",
         cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns += [
        path("400/", default_views.bad_request,
             kwargs={"exception": Exception("Bad Request!")},),
        path("403/", default_views.permission_denied,
             kwargs={"exception": Exception("Permission Denied")},),
        path("404/", default_views.page_not_found,
             kwargs={"exception": Exception("Page not Found")},),
        path("500/", default_views.server_error),
    ]
