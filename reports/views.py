from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from members.models import Member
from finance.models import FinancialTransaction

@login_required
def report_dashboard(request):
    return render(request, 'reports/dashboard.html')

@login_required
def member_report(request):
    members = Member.objects.all().order_by('last_name', 'first_name')
    return render(request, 'reports/member_report.html', {'members': members})

from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Sum, Case, When, DecimalField

@login_required
def financial_report(request):
    transactions = FinancialTransaction.objects.all().order_by('-transaction_date')
    total_income = transactions.filter(transaction_type__startswith='income_').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type__startswith='expense_').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    # Categorize by Month
    monthly_data = transactions.annotate(month=TruncMonth('transaction_date')).values('month').annotate(
        income=Sum(Case(When(transaction_type__startswith='income_', then='amount'), default=0, output_field=DecimalField())),
        expense=Sum(Case(When(transaction_type__startswith='expense_', then='amount'), default=0, output_field=DecimalField()))
    ).order_by('-month')

    # Categorize by Year
    annual_data = transactions.annotate(year=TruncYear('transaction_date')).values('year').annotate(
        income=Sum(Case(When(transaction_type__startswith='income_', then='amount'), default=0, output_field=DecimalField())),
        expense=Sum(Case(When(transaction_type__startswith='expense_', then='amount'), default=0, output_field=DecimalField()))
    ).order_by('-year')

    return render(request, 'reports/financial_report.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'monthly_data': monthly_data,
        'annual_data': annual_data,
    })
