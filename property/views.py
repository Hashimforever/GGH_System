from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Property, Loaner, PropertyLoan, Category
from .forms import (PropertyForm, LoanerForm, PropertyLoanForm,
                    CategoryForm, ReturnLoanForm, LoanerWithLoanForm)


# ═══════════════════════════════════════════════════════════════
#   HELPER — Finance integration
# ═══════════════════════════════════════════════════════════════

def _create_property_withdrawal(prop, user):
    """Create a Withdrawal + FinancialTransaction for a property purchase."""
    from finance.models import Withdrawal, FinancialTransaction

    if not prop.total_cost or prop.total_cost <= 0:
        return None

    withdrawal = Withdrawal.objects.create(
        category='Property Purchase',
        amount=prop.total_cost,
        purpose=f"Purchase: {prop.name} ({prop.code})",
        description=(
            f"Auto-generated from Property Records.\n"
            f"Quantity: {prop.quantity_total} × Unit Price: {prop.unit_price}"
        ),
        transaction_date=prop.purchase_date or timezone.now().date(),
        status='approved',
        recorded_by=user,
        approved_by=user,
    )
    FinancialTransaction.objects.create(
        transaction_type='expense_withdrawal',
        amount=prop.total_cost,
        description=f"Property Purchase: {prop.name} ({prop.code})",
        withdrawal=withdrawal,
    )
    return withdrawal


def _refund_property_finance(prop, user):
    """
    Refund finance entries for this property by creating an offsetting income
    transaction. Looks up withdrawals by property code keyword.
    """
    from finance.models import Withdrawal, FinancialTransaction

    keyword = f"({prop.code})"
    withdrawals = Withdrawal.objects.filter(
        purpose__icontains=keyword,
        category='Property Purchase',
    )

    refunded = 0
    for w in withdrawals:
        FinancialTransaction.objects.create(
            transaction_type='income_other',
            amount=w.amount,
            description=f"Refund: Property adjustment for {prop.name} ({prop.code})",
            withdrawal=None,
        )
        w.description = (w.description or '') + \
            f"\n[REVERSED by {user.username} on {timezone.now().date()}]"
        w.save()
        refunded += w.amount

    return refunded


# ---------- DASHBOARD ----------
@login_required
def property_dashboard(request):
    today = timezone.now().date()
    total_items = Property.objects.count()
    total_available = Property.objects.filter(status='available').count()
    active_loans = PropertyLoan.objects.filter(status__in=['active', 'overdue']).count()
    overdue_loans = PropertyLoan.objects.filter(status='overdue').count()
    recent_loans = PropertyLoan.objects.select_related('property_item', 'loaner')[:8]
    low_stock = Property.objects.filter(quantity_available__lte=1)

    context = {
        'total_items': total_items,
        'total_available': total_available,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'recent_loans': recent_loans,
        'low_stock': low_stock,
    }
    return render(request, 'property/dashboard.html', context)


# ---------- PROPERTY CRUD ----------
@login_required
def property_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    category_id = request.GET.get('category', '')

    items = Property.objects.all()
    if q:
        items = items.filter(Q(name__icontains=q) | Q(code__icontains=q))
    if status:
        items = items.filter(status=status)
    if category_id:
        items = items.filter(category_id=category_id)

    context = {
        'items': items,
        'categories': Category.objects.all(),
        'q': q,
        'status': status,
        'category_id': category_id,
        'status_choices': Property.STATUS_CHOICES,
    }
    return render(request, 'property/property_list.html', context)


@login_required
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save()

            # ⭐ If deduct_from_finance is checked → create a Withdrawal + Transaction
            if prop.deduct_from_finance and prop.total_cost and prop.total_cost > 0:
                _create_property_withdrawal(prop, request.user)
                messages.success(
                    request,
                    f"Property '{prop.name}' added. "
                    f"💰 {prop.total_cost} deducted from Finance balance."
                )
            else:
                messages.success(request, "Property added successfully.")
            return redirect('property:property_list')
    else:
        form = PropertyForm()
    return render(request, 'property/property_form.html', {'form': form, 'title': 'Add Property'})


@login_required
def property_edit(request, pk):
    item = get_object_or_404(Property, pk=pk)

    # Capture old values BEFORE the form is saved
    old_cost = item.total_cost or 0
    old_deduct = item.deduct_from_finance

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            prop = form.save()
            new_cost = prop.total_cost or 0
            new_deduct = prop.deduct_from_finance

            # Case 1: Not deducting before → NOW deducting → create withdrawal
            if (not old_deduct) and new_deduct and new_cost > 0:
                _create_property_withdrawal(prop, request.user)
                messages.success(
                    request,
                    f"Property updated. 💰 {new_cost} deducted from Finance balance."
                )

            # Case 2: Deducting before → NOW not deducting → refund
            elif old_deduct and (not new_deduct):
                refunded = _refund_property_finance(prop, request.user)
                messages.success(
                    request,
                    f"Property updated. 💰 {refunded} refunded to Finance balance."
                )

            # Case 3: Deducting both → amount changed → refund old + create new
            elif old_deduct and new_deduct and old_cost != new_cost:
                _refund_property_finance(prop, request.user)
                if new_cost > 0:
                    _create_property_withdrawal(prop, request.user)
                messages.success(
                    request,
                    f"Property updated. Finance adjusted: {old_cost} → {new_cost}."
                )

            else:
                messages.success(request, "Property updated successfully.")

            return redirect('property:property_list')
    else:
        form = PropertyForm(instance=item)
    return render(request, 'property/property_form.html', {'form': form, 'title': 'Edit Property'})


@login_required
def property_detail(request, pk):
    item = get_object_or_404(Property, pk=pk)
    loans = item.loans.select_related('loaner').all()
    return render(request, 'property/property_detail.html', {'item': item, 'loans': loans})


@login_required
def property_delete(request, pk):
    item = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        # ⭐ If this property deducted from finance → refund on delete
        if item.deduct_from_finance and item.total_cost and item.total_cost > 0:
            refunded = _refund_property_finance(item, request.user)
            messages.success(
                request,
                f"Property '{item.name}' deleted. 💰 {refunded} refunded to Finance balance."
            )
        else:
            messages.success(request, "Property deleted.")
        item.delete()
        return redirect('property:property_list')
    return render(request, 'property/property_confirm_delete.html', {'item': item})


# ---------- LOANER CRUD ----------
@login_required
def loaner_list(request):
    q = request.GET.get('q', '')
    loaners = Loaner.objects.all()
    if q:
        loaners = loaners.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
    return render(request, 'property/loaner_list.html', {'loaners': loaners, 'q': q})


@login_required
def loaner_create(request):
    """
    Create a Loaner, optionally recording a material loan in the SAME submission.
    """
    if request.method == 'POST':
        form = LoanerWithLoanForm(request.POST)
        if form.is_valid():
            form.current_user = request.user
            loaner = form.save()

            if form.cleaned_data.get('property_item'):
                messages.success(
                    request,
                    f"Loaner '{loaner.full_name}' added and material loan recorded."
                )
            else:
                messages.success(request, f"Loaner '{loaner.full_name}' added successfully.")
            return redirect('property:loaner_list')
    else:
        form = LoanerWithLoanForm()
    return render(request, 'property/loaner_form.html', {'form': form, 'title': 'Add Loaner'})


@login_required
def loaner_edit(request, pk):
    loaner = get_object_or_404(Loaner, pk=pk)
    if request.method == 'POST':
        form = LoanerForm(request.POST, instance=loaner)
        if form.is_valid():
            form.save()
            messages.success(request, "Loaner updated.")
            return redirect('property:loaner_list')
    else:
        form = LoanerForm(instance=loaner)
    return render(request, 'property/loaner_form.html', {'form': form, 'title': 'Edit Loaner'})


@login_required
def loaner_detail(request, pk):
    loaner = get_object_or_404(Loaner, pk=pk)
    loans = loaner.loans.select_related('property_item').all()
    return render(request, 'property/loaner_detail.html', {'loaner': loaner, 'loans': loans})


# ---------- LOAN CRUD ----------
@login_required
def loan_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    loans = PropertyLoan.objects.select_related('property_item', 'loaner').all()
    if q:
        loans = loans.filter(
            Q(loan_code__icontains=q) |
            Q(property_item__name__icontains=q) |
            Q(loaner__full_name__icontains=q)
        )
    if status:
        loans = loans.filter(status=status)

    # auto-refresh overdue flags
    for loan in loans:
        if loan.is_overdue and loan.status == 'active':
            loan.status = 'overdue'
            loan.save(update_fields=['status'])

    return render(request, 'property/loan_list.html', {
        'loans': loans,
        'q': q,
        'status': status,
        'status_choices': PropertyLoan.STATUS_CHOICES,
    })


@login_required
def loan_create(request):
    if request.method == 'POST':
        form = PropertyLoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.handled_by = request.user
            loan.save()

            # decrement available quantity
            prop = loan.property_item
            prop.quantity_available = max(0, prop.quantity_available - loan.quantity)
            if prop.quantity_available == 0:
                prop.status = 'loaned'
            prop.save()

            messages.success(request, "Loan recorded successfully.")
            return redirect('property:loan_list')
    else:
        form = PropertyLoanForm()
    return render(request, 'property/loan_form.html', {'form': form, 'title': 'New Loan'})


@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(PropertyLoan, pk=pk)
    return render(request, 'property/loan_detail.html', {'loan': loan})


@login_required
def loan_return(request, pk):
    loan = get_object_or_404(PropertyLoan, pk=pk)
    if request.method == 'POST':
        form = ReturnLoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            if not loan.actual_return_date:
                loan.actual_return_date = timezone.now().date()
            loan.status = 'returned'
            loan.save()

            # restore quantity
            prop = loan.property_item
            prop.quantity_available = min(prop.quantity_total,
                                          prop.quantity_available + loan.quantity)
            if prop.status == 'loaned' and prop.quantity_available > 0:
                prop.status = 'available'
            prop.save()

            messages.success(request, "Loan marked as returned.")
            return redirect('property:loan_list')
    else:
        form = ReturnLoanForm(instance=loan, initial={'actual_return_date': timezone.now().date()})
    return render(request, 'property/loan_return.html', {'form': form, 'loan': loan})


@login_required
def overdue_loans(request):
    today = timezone.now().date()
    loans = PropertyLoan.objects.filter(
        status__in=['active', 'overdue'],
        expected_return_date__lt=today
    ).select_related('property_item', 'loaner')
    return render(request, 'property/overdue_loans.html', {'loans': loans})