from rest_framework import routers
from django.contrib import admin
from django.urls import include, path
from cats.views import (
    AchievementViewSet, CatViewSet, UserViewSet,
    home_page, login_view, register_view, admin_dashboard, logout_view
)
from cats.views import create_cat_view
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
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('cats/create/', create_cat_view, name='create_cat'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)