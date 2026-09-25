from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Withdrawal, FinancialTransaction
from loans.models import Loan
from .forms import WithdrawalForm, IncomeForm
from django.contrib import messages
from django.utils import timezone

@login_required
def finance_dashboard(request):
    transactions = FinancialTransaction.objects.all().order_by('-transaction_date')[:50]
    withdrawals = Withdrawal.objects.filter(status='pending')
    pending_loans = Loan.objects.filter(status='pending')

    # Metrics Calculations
    all_tx = FinancialTransaction.objects.all()
    total_income = all_tx.filter(transaction_type__startswith='income_').aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdrawal = all_tx.filter(transaction_type__startswith='expense_').aggregate(Sum('amount'))['amount__sum'] or 0
    total_balance = total_income - total_withdrawal
    
    returned_loans = all_tx.filter(transaction_type='income_loan_repayment').aggregate(Sum('amount'))['amount__sum'] or 0
    active_loans = Loan.objects.filter(status__in=['active', 'overdue'])
    unreturned_loans = active_loans.aggregate(Sum('amount'))['amount__sum'] or 0
    # True unreturned would be principal minus repayments, but this is a close approximation for outstanding original principal.
    # Let's subtract returned loans from the active principal if they apply, or just show Total Disbursed vs Total Returned.
    # Actually, let's keep it simple: Total Disbursed Loans - Total Returned Loans = Unreturned Loans Balance
    total_disbursed = all_tx.filter(transaction_type='expense_loan_disbursement').aggregate(Sum('amount'))['amount__sum'] or 0
    unreturned_loans = total_disbursed - returned_loans

    return render(request, 'finance/dashboard.html', {
        'transactions': transactions,
        'withdrawals': withdrawals,
        'pending_loans': pending_loans,
        'total_balance': total_balance,
        'total_income': total_income,
        'total_withdrawal': total_withdrawal,
        'returned_loans': returned_loans,
        'unreturned_loans': unreturned_loans,
    })

@login_required
def approve_withdrawal(request, pk):
    withdrawal = get_object_or_404(Withdrawal, pk=pk, status='pending')
    if request.method == 'POST':
        withdrawal.status = 'approved'
        withdrawal.approved_by = request.user
        withdrawal.save()
        messages.success(request, f"Withdrawal for '{withdrawal.purpose}' approved. Balance updated.")
    return redirect('finance:dashboard')

@login_required
def approve_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk, status='pending')
    if request.method == 'POST':
        loan.status = 'active'
        loan.approval_date = timezone.now().date()
        loan.disbursement_date = timezone.now().date()
        loan.save()
        messages.success(request, f"Loan for {loan.member} approved and marked as withdrawal.")
    return redirect('finance:dashboard')

@login_required
def add_withdrawal(request):
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.recorded_by = request.user
            withdrawal.save()
            messages.success(request, 'Withdrawal request submitted.')
            return redirect('finance:dashboard')
    else:
        form = WithdrawalForm()
    return render(request, 'finance/withdrawal_form.html', {'form': form})

@login_required
def record_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.transaction_type = 'income_other'
            income.save()
            messages.success(request, 'Other income recorded successfully.')
            return redirect('finance:dashboard')
    else:
        form = IncomeForm()
    return render(request, 'finance/income_form.html', {'form': form})
