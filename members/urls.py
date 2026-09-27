from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # ───── Existing member views ─────
    path('', views.member_list, name='member_list'),
    path('add/', views.member_create, name='member_create'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('<int:pk>/edit/', views.member_update, name='member_update'),

    # ───── Public registration (no login required) ─────
    path('register/', views.register, name='register'),
    path('register/success/', views.register_success, name='register_success'),

    # ───── Admin review of registration requests ─────
    path('registrations/', views.registration_requests, name='registration_requests'),
    path('registrations/<int:pk>/', views.registration_detail, name='registration_detail'),
    path('registrations/<int:pk>/approve/', views.registration_approve, name='registration_approve'),
    path('registrations/<int:pk>/reject/', views.registration_reject, name='registration_reject'),
]