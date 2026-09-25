from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('members/', views.member_report, name='member_report'),
    path('financial/', views.financial_report, name='financial_report'),
]
