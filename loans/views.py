from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Loan, LoanRepayment
from .forms import LoanForm
from django.contrib import messages

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
