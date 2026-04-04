from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),  # Main page
    path('level/<slug:level_slug>/', views.level_detail, name='level_detail'),
    path('update-progress/', views.update_progress, name='update_progress'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
