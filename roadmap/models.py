from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Level(models.Model):
    """
    Модель для уровней обучения (Новорождённый, Умненький и т.д.)
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Название уровня",
        help_text="Например: Новорождённый бекендер"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-идентификатор",
        help_text="Уникальное имя для URL, на основе названия. Должно содержать только латиницу, цифры, дефисы и подчеркивания."
    )
    timeframe = models.CharField(
        max_length=50,
        verbose_name="Срок освоения",
        help_text="Например: 1–3 месяца",
        blank=True, null=True
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Чем меньше число, тем выше уровень в списке"
    )
    description = models.TextField(
        verbose_name="Описание уровня",
        help_text="Краткое описание того, что будет изучено на этом этапе",
        blank=True
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Уровень"
        verbose_name_plural = "Уровни"

    def __str__(self):
        return f"{self.name} ({self.timeframe})"

    def get_absolute_url(self):
        """Возвращает ссылку на страницу уровня"""
        return reverse('level_detail', args=[self.slug])


class Category(models.Model):
    """
    Модель для категорий/разделов (Git, SQL, Фреймворки и т.д.)
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Название категории"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-идентификатор"
    )
    description = models.TextField(
        verbose_name="Описание категории",
        blank=True
    )
    icon = models.ImageField(
        upload_to='categories/icons/',
        verbose_name="Иконка",
        help_text="SVG или PNG иконка для категории",
        blank=True, null=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])


class Technology(models.Model):
    """
    Модель для конкретной технологии/темы (Docker, JWT, и т.д.)
    """
    DIFFICULTY_CHOICES = [
        ('beginner', '🟢 Начальный'),
        ('intermediate', '🟡 Средний'),
        ('advanced', '🔴 Продвинутый'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Название технологии"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL-идентификатор"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Что это такое и зачем это учить. 1-2 предложения."
    )

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='technologies',
        verbose_name="Уровень обучения"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='technologies',
        verbose_name="Категория",
        blank=True, null=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        verbose_name="Уровень сложности"
    )
    order_in_level = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок в рамках уровня",
        help_text="Чем меньше число, тем выше в списке"
    )

    official_docs_url = models.URLField(
        verbose_name="Ссылка на официальную документацию",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано"
    )

    class Meta:
        ordering = ['level__order', 'order_in_level', 'name']
        verbose_name = "Технология"
        verbose_name_plural = "Технологии"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('technology_detail', args=[self.slug])


class Resource(models.Model):
    """
    Модель для учебных материалов (статьи, видео, курсы)
    """
    RESOURCE_TYPES = [
        ('video', '📺 Видео'),
        ('article', '📝 Статья'),
        ('course', '🎓 Курс'),
        ('book', '📚 Книга'),
        ('tool', '🔧 Инструмент'),
    ]

    technology = models.ForeignKey(
        Technology,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name="Технология"
    )

    title = models.CharField(
        max_length=300,
        verbose_name="Название ресурса"
    )
    url = models.URLField(
        verbose_name="Ссылка"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        default='article',
        verbose_name="Тип ресурса"
    )
    description = models.TextField(
        verbose_name="Краткое описание",
        blank=True
    )
    is_free = models.BooleanField(
        default=True,
        verbose_name="Бесплатный"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )

    class Meta:
        ordering = ['technology', 'order', 'title']
        verbose_name = "Учебный ресурс"
        verbose_name_plural = "Учебные ресурсы"

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class UserProgress(models.Model):
    """
    Модель для отслеживания прогресса пользователя по технологиям
    """
    STATUS_CHOICES = [
        ('not_started', '⚪ Не начато'),
        ('in_progress', '🟡 В процессе'),
        ('completed', '✅ Выполнено'),
    ]
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Пользователь"
    )
    technology = models.ForeignKey(
        Technology,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Технология"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name="Статус"
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата завершения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Прогресс пользователя"
        verbose_name_plural = "Прогресс пользователей"
        unique_together = ['user', 'technology']

    def __str__(self):
        status_icon = {
            'not_started': '⚪',
            'in_progress': '🟡',
            'completed': '✅'
        }.get(self.status, '⚪')
        return f"{self.user.username} - {self.technology.name} - {status_icon}"


class Profile(models.Model):
    """
    Модель для дополнительной информации о пользователе
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватарка",
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name="О себе",
        blank=True,
        max_length=500
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"
