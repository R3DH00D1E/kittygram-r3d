from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets

from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


def home_page(request):
    featured_cats = (
        Cat.objects.select_related('owner')
        .prefetch_related('achievements')
        .annotate(achievement_count=Count('achievements'))
        .order_by('-id')[:6]
    )
    latest_achievements = Achievement.objects.annotate(
        cat_count=Count('cat')
    ).order_by('-id')[:8]

    context = {
        'cat_count': Cat.objects.count(),
        'user_count': User.objects.count(),
        'achievement_count': Achievement.objects.count(),
        'featured_cats': featured_cats,
        'latest_achievements': latest_achievements,
    }
    return render(request, 'cats/home.html', context)
