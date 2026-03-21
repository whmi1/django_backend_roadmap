import json


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Level, Category, Technology, UserProgress


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
