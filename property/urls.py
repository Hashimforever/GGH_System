from django.urls import path
from . import views

app_name = 'property'

urlpatterns = [
    path('', views.property_dashboard, name='dashboard'),

    # Property
    path('items/', views.property_list, name='property_list'),
    path('items/add/', views.property_create, name='property_create'),
    path('items/<int:pk>/', views.property_detail, name='property_detail'),
    path('items/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('items/<int:pk>/delete/', views.property_delete, name='property_delete'),

    # Loaners
    path('loaners/', views.loaner_list, name='loaner_list'),
    path('loaners/add/', views.loaner_create, name='loaner_create'),
    path('loaners/<int:pk>/', views.loaner_detail, name='loaner_detail'),
    path('loaners/<int:pk>/edit/', views.loaner_edit, name='loaner_edit'),

    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/', views.loan_detail, name='loan_detail'),
    path('loans/<int:pk>/return/', views.loan_return, name='loan_return'),
    path('loans/overdue/', views.overdue_loans, name='overdue_loans'),
]