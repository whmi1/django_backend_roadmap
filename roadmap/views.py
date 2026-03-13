from django.shortcuts import render, get_object_or_404
from .models import Level, Category, Technology


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

    context = {
        'level': level,
        'technologies': technologies,
        'title': f'{level.name} - Backend Roadmap'
    }

    return render(request, 'roadmap/level_detail.html', context)
