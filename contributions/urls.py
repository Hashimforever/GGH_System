from django.urls import path
from . import views

app_name = 'contributions'

urlpatterns = [
    path('', views.contribution_dashboard, name='dashboard'),
    path('generate/', views.generate_expected, name='generate'),
    path('record/', views.bulk_record_matrix, name='record'),
    path('member/<int:member_id>/', views.member_profile_payments, name='member_profile'),
    path('toggle/', views.toggle_payment_status, name='toggle_payment'),
]
