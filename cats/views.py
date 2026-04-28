from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User as DjangoUser
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .models import Achievement, Cat, User, CHOICES, OwnershipStatus

from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class IsOwnerOrAdmin:
    """Helper permission: owner or admin allowed for unsafe actions."""
    @staticmethod
    def has_object_permission(request, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_staff or user.is_superuser or obj.owner_id == user.id


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not IsOwnerOrAdmin.has_object_permission(request, instance):
            return Response({'detail': 'Недостаточно прав.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not IsOwnerOrAdmin.has_object_permission(request, instance):
            return Response({'detail': 'Недостаточно прав.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not IsOwnerOrAdmin.has_object_permission(request, instance):
            return Response({'detail': 'Недостаточно прав.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


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


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_http_methods(["DELETE"])
def api_delete_cat(request, cat_id):
    """AJAX API: delete a cat."""
    try:
        cat = Cat.objects.get(id=cat_id)
        cat_name = cat.name
        cat.delete()
        return JsonResponse({'success': True, 'message': f'Кот "{cat_name}" удалён'})
    except Cat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Кот не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_http_methods(["POST", "OPTIONS"])
def api_update_cat_status(request, cat_id):
    """AJAX API: update cat ownership status."""
    if request.method == 'OPTIONS':
        return JsonResponse({'success': True})
    
    try:
        cat = Cat.objects.get(id=cat_id)
        status_id = request.POST.get('status_id')
        
        if status_id:
            ownership_status = OwnershipStatus.objects.get(id=status_id)
            cat.ownership_status = ownership_status
            cat.save()
            return JsonResponse({'success': True, 'message': f'Статус обновлён на "{ownership_status.name}"'})
        else:
            return JsonResponse({'success': False, 'error': 'Статус не указан'}, status=400)
    except Cat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Кот не найден'}, status=404)
    except OwnershipStatus.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Статус не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@require_http_methods(["GET"])
def api_list_ownership_statuses(request):
    """AJAX API: list all ownership statuses."""
    try:
        statuses = OwnershipStatus.objects.values('id', 'name')
        return JsonResponse({'success': True, 'statuses': list(statuses)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login')
def create_cat_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color')
        birth_year = request.POST.get('birth_year')
        image = request.FILES.get('image')

        Cat.objects.create(
            name=name,
            color=color,
            birth_year=int(birth_year),
            owner=request.user,
            image=image
        )
        return redirect('home')

    choices = CHOICES
    return render(request, 'cats/create_cat.html', {'choices': choices})


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
