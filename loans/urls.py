from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_dashboard, name='dashboard'),
    path('apply/', views.loan_apply, name='apply'),
]
