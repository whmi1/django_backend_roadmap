from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),  # Main page
    path('level/<slug:level_slug>/', views.level_detail, name='level_detail'),
    path('toggle-progress/', views.toggle_progress, name='toggle_progress'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name='search'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
]
