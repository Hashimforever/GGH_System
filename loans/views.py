from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Loan, LoanRepayment
from .forms import LoanForm
from finance.models import FinancialTransaction


@login_required
def loan_dashboard(request):
    loans = Loan.objects.all().order_by('-application_date')
    return render(request, 'loans/dashboard.html', {'loans': loans})


@login_required
def loan_apply(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan application submitted.')
            return redirect('loans:dashboard')
    else:
        form = LoanForm()
    return render(request, 'loans/loan_form.html', {'form': form})


@login_required
def loan_detail(request, pk):
    """Show details of a single loan with repayment history."""
    loan = get_object_or_404(Loan, pk=pk)
    repayments = loan.repayments.all().order_by('-repayment_date')
    return render(request, 'loans/loan_detail.html', {
        'loan': loan,
        'repayments': repayments,
    })


@login_required
def loan_return(request, pk):
    """
    Mark a loan as fully returned (no interest).
    Creates a LoanRepayment + income_loan_repayment FinancialTransaction.
    """
    loan = get_object_or_404(Loan, pk=pk)

    if loan.status == 'repaid':
        messages.warning(request, f"Loan #{loan.id} is already repaid.")
        return redirect('loans:dashboard')

    if loan.status not in ['active', 'overdue']:
        messages.warning(
            request,
            f"Loan #{loan.id} cannot be returned (status: {loan.get_status_display()})."
        )
        return redirect('loans:dashboard')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', '').strip()
        reference_number = request.POST.get('reference_number', '').strip()
        repayment_date_str = request.POST.get('repayment_date', '').strip()

        repayment_date = timezone.now().date()
        if repayment_date_str:
            try:
                from datetime import datetime
                repayment_date = datetime.strptime(repayment_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # 1. Create the LoanRepayment record
        repayment = LoanRepayment.objects.create(
            loan=loan,
            amount=loan.amount,
            repayment_date=repayment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            recorded_by=request.user,
        )

        # 2. Create the finance income transaction (money returns to fund)
        FinancialTransaction.objects.create(
            transaction_type='income_loan_repayment',
            amount=loan.amount,
            description=f"Loan returned by {loan.member} (Loan #{loan.id})",
            loan_repayment=repayment,
            member=loan.member,
        )

        # 3. Mark loan as repaid
        loan.status = 'repaid'
        loan.save()

        messages.success(
            request,
            f"✅ Loan #{loan.id} returned. "
            f"💰 {loan.amount} added back to Total Balance. "
            f"📉 Unreturned Loans reduced by {loan.amount}."
        )
        return redirect('loans:dashboard')

    # GET — show the return form
    return render(request, 'loans/loan_return.html', {'loan': loan})