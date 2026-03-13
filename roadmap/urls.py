from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),  # Main page
    path('level/<slug:level_slug>/', views.level_detail, name='level_detail')
]
