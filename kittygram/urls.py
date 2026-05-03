from rest_framework import routers
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve
from cats.views import (
    AchievementViewSet, CatViewSet, UserViewSet,
    home_page, login_view, register_view, cabinet_view, admin_dashboard, logout_view,
    api_delete_cat, api_update_cat_status, api_list_ownership_statuses
)
from cats.views import create_cat_view, debug_media_check
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('cats', CatViewSet)
router.register('users', UserViewSet)
router.register('achievements', AchievementViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('cabinet/', cabinet_view, name='cabinet'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('cats/create/', create_cat_view, name='create_cat'),
    path('debug/media-check/', debug_media_check, name='debug_media_check'),
    path('api/cat/<int:cat_id>/delete/', api_delete_cat, name='api_delete_cat'),
    path('api/cat/<int:cat_id>/status/', api_update_cat_status, name='api_update_cat_status'),
    path('api/ownership-statuses/', api_list_ownership_statuses, name='api_list_ownership_statuses'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

media_url_path = settings.MEDIA_URL.lstrip('/')
urlpatterns += [
    path(media_url_path + '<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)