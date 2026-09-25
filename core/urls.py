from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.system_settings, name='settings'),
    path('homepage/', views.manage_homepage, name='manage_homepage'),
    path('homepage/announcements/new/', views.announcement_create, name='announcement_create'),
    path('homepage/announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('homepage/announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
]
