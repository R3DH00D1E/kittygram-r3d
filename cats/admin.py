from django.contrib import admin
from .models import Cat

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'birth_year', 'owner', 'ownership_status')
    search_fields = ('name',)
    list_filter = ('color', 'birth_year', 'ownership_status')

from django.contrib.auth import get_user_model
from .models import Achievement, OwnershipStatus

User = get_user_model()

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(OwnershipStatus)
class OwnershipStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

try:
    admin.site.register(User)
except admin.sites.AlreadyRegistered:
    pass
