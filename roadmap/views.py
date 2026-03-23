import json


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Level, Category, Technology, UserProgress, Profile
from django.contrib.auth.models import User
from django import forms


def index(request):
    levels = Level.objects.order_by('order')

    context = {
        'levels': levels,
        'title': 'Roadmap для Backend-разработчика'
    }

    return render(request, 'roadmap/index.html', context)


def level_detail(request, level_slug):
    level = get_object_or_404(Level, slug=level_slug)
    
    technologies = level.technologies.filter(
        is_published=True
    ).order_by('category__name', 'order_in_level')
    
    user_progress = {}
    if request.user.is_authenticated:
        progresses = UserProgress.objects.filter(
            user=request.user,
            technology__in=technologies
        ).values_list('technology_id', 'completed')
        user_progress = dict(progresses)
        print(f"DEBUG: user_progress = {user_progress}") 
    
    context = {
        'level': level,
        'technologies': technologies,
        'user_progress': user_progress,
        'title': f'{level.name} - Backend Roadmap'
    }
    
    return render(request, 'roadmap/level_detail.html', context)


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def level_detail(request, level_slug):
    level = get_object_or_404(Level, slug=level_slug)

    technologies = level.technologies.filter(
        is_published=True
    ).order_by('category__name', 'order_in_level')

    user_progress = {}
    if request.user.is_authenticated:
        progresses = UserProgress.objects.filter(
            user=request.user,
            technology__in=technologies
        ).values_list('technology_id', 'completed')
        user_progress = dict(progresses)

    context = {
        'level': level,
        'technologies': technologies,
        'user_progress': user_progress,
        'title': f'{level.name} - Backend Roadmap'
    }

    return render(request, 'roadmap/level_detail.html', context)


@require_POST
@login_required
def toggle_progress(request):
    """Обновление прогресса пользователя по технологии"""
    try:
        data = json.loads(request.body)
        technology_id = data.get('technology_id')
        completed = data.get('completed', False)

        technology = get_object_or_404(Technology, id=technology_id)

        # Получаем или создаем запись прогресса
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            technology=technology,
            defaults={'completed': completed}
        )

        # Если запись уже существовала, обновляем
        if not created:
            progress.completed = completed
            if completed:
                from django.utils import timezone
                progress.completed_at = timezone.now()
            else:
                progress.completed_at = None
            progress.save()

        category = technology.category
        if category:
            technologies_in_category = Technology.objects.filter(
                level=technology.level,
                category=category,
                is_published=True
            )
            total = technologies_in_category.count()
            completed_count = UserProgress.objects.filter(
                user=request.user,
                technology__in=technologies_in_category,
                completed=True
            ).count()
            percent = int((completed_count / total * 100)) if total > 0 else 0
        else:
            total = 0
            completed_count = 0
            percent = 0

        return JsonResponse({
            'success': True,
            'message': 'Прогресс обновлен',
            'stats': {
                'category_id': category.id if category else None,
                'total': total,
                'completed': completed_count,
                'percent': percent
            }
        })

    except Technology.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Технология не найдена'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
    

class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


class ProfileUpdateForm(forms.ModelForm):
    """Форма обновления профиля"""
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 4})


@login_required
def profile_view(request):
    """Страница профиля с прогрессом и настройками"""
    user = request.user
    
    profile, created = Profile.objects.get_or_create(user=user)
    
    levels = Level.objects.all().order_by('order')
    levels_progress = []
    total_technologies = 0
    total_completed = 0
    
    for level in levels:
        technologies = Technology.objects.filter(level=level, is_published=True)
        tech_count = technologies.count()
        
        completed_count = UserProgress.objects.filter(
            user=user,
            technology__in=technologies,
            completed=True
        ).count()
        
        percent = int((completed_count / tech_count * 100)) if tech_count > 0 else 0
        
        total_technologies += tech_count
        total_completed += completed_count
        
        levels_progress.append({
            'level': level,
            'total': tech_count,
            'completed': completed_count,
            'percent': percent
        })
    
    total_percent = int((total_completed / total_technologies * 100)) if total_technologies > 0 else 0
    
    context = {
        'user': user,
        'profile': profile,
        'levels_progress': levels_progress,
        'total_technologies': total_technologies,
        'total_completed': total_completed,
        'total_percent': total_percent,
        'title': 'Мой профиль'
    }
    
    return render(request, 'roadmap/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Редактирование профиля'
    }
    
    return render(request, 'roadmap/profile_edit.html', context)


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Смена пароля'
    }
    
    return render(request, 'roadmap/change_password.html', context)


def search(request):
    """Поиск технологий по названию и описанию"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        results = Technology.objects.filter(
            is_published=True
        ).filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query)
        ).select_related('level', 'category')
    
    context = {
        'query': query,
        'results': results,
        'results_count': results.count(),
        'title': f'Результаты поиска: {query}' if query else 'Поиск'
    }
    
    return render(request, 'roadmap/search_results.html', context)
