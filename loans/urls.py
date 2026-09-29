from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_dashboard, name='dashboard'),
    path('apply/', views.loan_apply, name='apply'),

    # ⭐ NEW: Detail + Return
    path('<int:pk>/', views.loan_detail, name='loan_detail'),
    path('<int:pk>/return/', views.loan_return, name='loan_return'),
]