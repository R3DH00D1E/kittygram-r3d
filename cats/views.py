from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User as DjangoUser
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .models import Achievement, Cat, User, CHOICES, OwnershipStatus
import os
from django.conf import settings

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
            return redirect('cabinet')
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
                email=email
            )
            # Log the user in
            login(request, user)
            return redirect('cabinet')
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


def _get_cabinet_context(user, error_message=''):
    user_cats = (
        Cat.objects.filter(owner=user)
        .select_related('owner', 'ownership_status')
        .prefetch_related('achievements')
        .annotate(achievement_count=Count('achievements'))
        .order_by('-id')
    )

    return {
        'cat_count': user_cats.count(),
        'cat_count_with_images': user_cats.exclude(image='').count(),
        'cat_count_with_status': user_cats.exclude(ownership_status__isnull=True).count(),
        'user_cats': user_cats,
        'choices': CHOICES,
        'ownership_statuses': OwnershipStatus.objects.order_by('name'),
        'error_message': error_message,
    }


@login_required(login_url='login')
def cabinet_view(request):
    """Personal cabinet for managing user's cats."""
    error_message = ''

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'create_cat':
            name = (request.POST.get('name') or '').strip()
            color = request.POST.get('color')
            birth_year = request.POST.get('birth_year')
            image = request.FILES.get('image')
            status_id = request.POST.get('ownership_status')

            if not name or not color or not birth_year:
                error_message = 'Заполните имя, цвет и год рождения.'
            else:
                ownership_status = None
                if status_id:
                    ownership_status = OwnershipStatus.objects.filter(id=status_id).first()

                Cat.objects.create(
                    name=name,
                    color=color,
                    birth_year=int(birth_year),
                    owner=request.user,
                    image=image,
                    ownership_status=ownership_status,
                )
                return redirect('cabinet')

        elif action == 'update_cat':
            cat = get_object_or_404(Cat, id=request.POST.get('cat_id'), owner=request.user)

            name = (request.POST.get('name') or '').strip()
            color = request.POST.get('color')
            birth_year = request.POST.get('birth_year')
            status_id = request.POST.get('ownership_status')
            new_image = request.FILES.get('image')

            if not name or not color or not birth_year:
                error_message = f'Проверьте данные для кота «{cat.name}».'
            else:
                cat.name = name
                cat.color = color
                cat.birth_year = int(birth_year)
                cat.ownership_status = None
                if status_id:
                    cat.ownership_status = OwnershipStatus.objects.filter(id=status_id).first()

                if request.POST.get('remove_image'):
                    cat.image = None
                if new_image:
                    cat.image = new_image

                cat.save()
                return redirect('cabinet')

        elif action == 'delete_cat':
            cat = get_object_or_404(Cat, id=request.POST.get('cat_id'), owner=request.user)
            cat.delete()
            return redirect('cabinet')

    context = _get_cabinet_context(request.user, error_message)
    return render(request, 'cats/cabinet.html', context)


@login_required(login_url='login')
def admin_dashboard(request):
    return redirect('cabinet')


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
    return redirect('cabinet')


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


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff or settings.DEBUG)
def debug_media_check(request):
    """Debug helper: check that a cat image exists on disk and show its URL/path.

    Usage: /debug/media-check/?cat_id=123
    Only accessible to staff users or when DEBUG=True.
    """
    cat_id = request.GET.get('cat_id')
    if not cat_id:
        return JsonResponse({'success': False, 'error': 'cat_id required'}, status=400)

    try:
        cat = Cat.objects.get(id=cat_id)
    except Cat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'cat not found'}, status=404)

    if not cat.image:
        return JsonResponse({'success': True, 'has_image': False, 'message': 'Cat has no image'})

    # image.url and image.path may raise ValueError if storage is remote; handle safely
    image_url = getattr(cat.image, 'url', None)
    image_path = getattr(cat.image, 'path', None)
    exists = False
    if image_path:
        exists = os.path.exists(image_path)

    return JsonResponse({
        'success': True,
        'has_image': True,
        'url': image_url,
        'path': image_path,
        'exists_on_disk': exists,
    })
