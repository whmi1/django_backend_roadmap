from django.contrib import admin
from .models import Level, Category, Technology, Resource


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'timeframe', 'order')
    list_editable = ('order',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'level', 'category', 'difficulty',
                    'order_in_level', 'is_published')
    list_filter = ('level', 'category', 'difficulty', 'is_published')
    list_editable = ('order_in_level', 'is_published')
    search_fields = ('name', 'description')
    autocomplete_fields = ('level', 'category')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'resource_type', 'is_free')
    list_filter = ('resource_type', 'is_free')
    search_fields = ('title', 'technology__name')
    autocomplete_fields = ('technology',)
