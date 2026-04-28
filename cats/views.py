from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User as DjangoUser
from django.views.decorators.http import require_http_methods
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


def login_view(request):
    """Login page for users"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Check if user is admin
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            context = {'error': 'Неверное имя пользователя или пароль'}
            return render(request, 'cats/login.html', context)
    
    # Check debug parameter
    debug_mode = request.GET.get('debug')
    if debug_mode == '1':
        request.session['debug_mode'] = True
    elif debug_mode == '0':
        request.session['debug_mode'] = False
    
    return render(request, 'cats/login.html')


def register_view(request):
    """Registration page for new users"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Validate passwords match
        if password1 != password2:
            context = {'error': 'Пароли не совпадают'}
            return render(request, 'cats/register.html', context)
        
        # Check if user already exists
        if DjangoUser.objects.filter(username=username).exists():
            context = {'error': 'Пользователь с таким именем уже существует'}
            return render(request, 'cats/register.html', context)
        
        # Create user
        try:
            user = DjangoUser.objects.create_user(
                username=username,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            
            # Log the user in
            login(request, user)
            return redirect('home')
        except Exception as e:
            context = {'error': f'Ошибка при регистрации: {str(e)}'}
            return render(request, 'cats/register.html', context)
    
    # Check debug parameter
    debug_mode = request.GET.get('debug')
    if debug_mode == '1':
        request.session['debug_mode'] = True
    elif debug_mode == '0':
        request.session['debug_mode'] = False
    
    return render(request, 'cats/register.html')


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard(request):
    """Admin dashboard page"""
    if request.method == 'POST':
        if 'logout' in request.POST:
            logout(request)
            return redirect('home')
    
    featured_cats = (
        Cat.objects.select_related('owner')
        .prefetch_related('achievements')
        .annotate(achievement_count=Count('achievements'))
        .order_by('-id')[:6]
    )
    
    context = {
        'cat_count': Cat.objects.count(),
        'user_count': User.objects.count(),
        'achievement_count': Achievement.objects.count(),
        'featured_cats': featured_cats,
    }
    return render(request, 'cats/admin_dashboard.html', context)


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('home')


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

    # Check debug parameter for debug menu
    debug_mode = request.GET.get('debug')
    if debug_mode == '1':
        request.session['debug_mode'] = True
    elif debug_mode == '0':
        request.session['debug_mode'] = False
    
    context = {
        'cat_count': Cat.objects.count(),
        'user_count': User.objects.count(),
        'achievement_count': Achievement.objects.count(),
        'featured_cats': featured_cats,
        'latest_achievements': latest_achievements,
        'debug_mode': request.session.get('debug_mode', False),
        'user': request.user,
    }
    return render(request, 'cats/home.html', context)
