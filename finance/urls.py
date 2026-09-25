from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_dashboard, name='dashboard'),
    path('income/add/', views.record_income, name='record_income'),
    path('withdrawals/add/', views.add_withdrawal, name='add_withdrawal'),
    path('withdrawals/<int:pk>/approve/', views.approve_withdrawal, name='approve_withdrawal'),
    path('loans/<int:pk>/approve/', views.approve_loan, name='approve_loan'),
]
