from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime
import json
from .models import PaymentPeriod, ExpectedPayment, ActualPayment
from members.models import Member
from .forms import PaymentPeriodForm, ActualPaymentForm

@login_required
def contribution_dashboard(request):
    periods = PaymentPeriod.objects.all().order_by('-year', '-month')
    recent_payments = ActualPayment.objects.all().order_by('-payment_date')[:10]
    
    # Generate Matrix Data
    year = int(request.GET.get('year', datetime.now().year))
    members = Member.objects.filter(status='active').order_by('last_name', 'first_name')
    months = list(range(1, 13))
    
    matrix_periods = PaymentPeriod.objects.filter(year=year)
    expected_qs = ExpectedPayment.objects.filter(period__in=matrix_periods)
    actual_qs = ActualPayment.objects.filter(period__in=matrix_periods)
    
    matrix = []
    for member in members:
        member_data = {'member': member, 'months': []}
        member_expected = [e for e in expected_qs if e.member_id == member.id]
        member_actual = [a for a in actual_qs if a.member_id == member.id]
        
        for month in months:
            exp = next((e for e in member_expected if e.period.month == month), None)
            act = next((a for a in member_actual if a.period.month == month), None)
            
            status = 'unpaid'
            amount_expected = exp.amount if exp else 0
            
            if act and act.amount_paid > 0:
                if act.amount_paid >= amount_expected:
                    status = 'paid'
                else:
                    status = 'partial'
                    
            member_data['months'].append({
                'month': month,
                'status': status,
                'expected': float(amount_expected),
                'actual': float(act.amount_paid) if act else 0.0
            })
        matrix.append(member_data)

    return render(request, 'contributions/dashboard.html', {
        'periods': periods,
        'recent_payments': recent_payments,
        'year': year,
        'matrix': matrix,
        'months': months,
        'year_range': range(2023, datetime.now().year + 3),
    })

@login_required
def generate_expected(request):
    from core.models import SystemSettings
    cfg = SystemSettings.get_settings()

    if request.method == 'POST':
        form = PaymentPeriodForm(request.POST)
        if form.is_valid():
            period, created = PaymentPeriod.objects.get_or_create(
                month=form.cleaned_data['month'],
                year=form.cleaned_data['year']
            )

            # Use system-configured amount; POST override only if explicitly supplied
            default_amount = request.POST.get('default_amount', '').strip()
            if default_amount:
                amount = float(default_amount)
            else:
                amount = float(cfg.get_monthly_amount(period.month))

            active_members = Member.objects.filter(status='active')
            count = 0
            for member in active_members:
                _, exp_created = ExpectedPayment.objects.get_or_create(
                    member=member,
                    period=period,
                    defaults={'amount': amount}
                )
                if exp_created:
                    count += 1

            messages.success(request, f'Generated {count} expected payments for {period} @ {cfg.currency_symbol}{amount:.2f}.')
            return redirect('contributions:dashboard')
    else:
        form = PaymentPeriodForm()

    return render(request, 'contributions/generate.html', {
        'form': form,
        'cfg': cfg
    })

@login_required
def bulk_record_matrix(request):
    year = int(request.GET.get('year', datetime.now().year))
    from core.models import SystemSettings
    from finance.models import FinancialTransaction
    cfg = SystemSettings.get_settings()
    members = Member.objects.filter(status='active').order_by('last_name', 'first_name')
    months = list(range(1, 13))
    
    if request.method == 'POST':
        updated_count = 0
        for member in members:
            # Check Reg Fee
            if f'reg_fee_{member.id}' in request.POST:
                reg_fee_str = request.POST.get(f'reg_fee_{member.id}')
                if reg_fee_str:
                    reg_fee_val = float(reg_fee_str)
                    if reg_fee_val > 0:
                        obj, created = FinancialTransaction.objects.get_or_create(
                            transaction_type='income_registration',
                            member=member,
                            defaults={
                                'amount': reg_fee_val,
                                'description': f'Registration fee for {member.member_id}',
                                'transaction_date': member.date_of_membership
                            }
                        )
                        if not created and obj.amount != reg_fee_val:
                            obj.amount = reg_fee_val
                            obj.save()
                            updated_count += 1
                        elif created:
                            updated_count += 1
                else:
                    # If explicitly cleared or 0
                    FinancialTransaction.objects.filter(transaction_type='income_registration', member=member).delete()

            # Check 12 months
            for i in months:
                amount_str = request.POST.get(f'amount_{member.id}_{i}')
                if amount_str:
                    amount_val = float(amount_str)
                    period, _ = PaymentPeriod.objects.get_or_create(month=i, year=year)
                    if amount_val > 0:
                        actual, created = ActualPayment.objects.get_or_create(
                            member=member, period=period,
                            defaults={'amount_paid': amount_val, 'recorded_by': request.user}
                        )
                        if not created and actual.amount_paid != amount_val:
                            actual.amount_paid = amount_val
                            actual.recorded_by = request.user
                            actual.save()
                            updated_count += 1
                        elif created:
                            updated_count += 1
                    else:
                        ActualPayment.objects.filter(member=member, period=period).delete()
        
        messages.success(request, f'Successfully recorded {updated_count} payment updates for {year}.')
        return redirect(f"{request.path}?year={year}")

    # Prepare matrix data
    periods = PaymentPeriod.objects.filter(year=year)
    actual_qs = ActualPayment.objects.filter(period__in=periods).select_related('member', 'period')
    reg_fee_qs = FinancialTransaction.objects.filter(transaction_type='income_registration')
    
    matrix = []
    for member in members:
        member_actuals = [a for a in actual_qs if a.member_id == member.id]
        member_reg = next((r for r in reg_fee_qs if r.member_id == member.id), None)
        
        row = {
            'member': member,
            'reg_fee_paid': float(member_reg.amount) if member_reg else 0.0,
            'months': []
        }
        for i in months:
            act = next((a for a in member_actuals if a.period.month == i), None)
            row['months'].append({
                'month': i,
                'amount_paid': float(act.amount_paid) if act else 0.0
            })
        matrix.append(row)
        
    return render(request, 'contributions/bulk_record_matrix.html', {
        'year': year,
        'year_range': range(2023, datetime.now().year + 3),
        'matrix': matrix,
        'months': months,
        'expected_reg_fee': float(cfg.registration_fee)
    })

@login_required
@require_POST
def toggle_payment_status(request):
    try:
        data = json.loads(request.body)
        member_id = data.get('member_id')
        month = int(data.get('month'))
        year = int(data.get('year'))
        current_status = data.get('status') # 'paid' or 'unpaid'
        
        member = Member.objects.get(id=member_id)
        period, _ = PaymentPeriod.objects.get_or_create(month=month, year=year)
        
        expected, _ = ExpectedPayment.objects.get_or_create(
            member=member, period=period,
            defaults={'amount': 0}
        )
        
        # If currently unpaid, we mark as paid (amount = expected.amount or 50 if 0)
        # If currently paid, we mark as unpaid (amount = 0)
        actual, created = ActualPayment.objects.get_or_create(
            member=member, period=period,
            defaults={'amount_paid': 0, 'recorded_by': request.user}
        )
        
        if current_status == 'unpaid':
            # Need to mark as paid
            amount_to_pay = expected.amount if expected.amount > 0 else 50.00
            actual.amount_paid = amount_to_pay
            actual.recorded_by = request.user
            actual.save()
            new_status = 'paid'
        else:
            # Need to mark as unpaid
            actual.amount_paid = 0
            actual.recorded_by = request.user
            actual.save()
            new_status = 'unpaid'
            
        return JsonResponse({'success': True, 'new_status': new_status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def member_profile_payments(request, member_id):
    """A view to record/manage all payments for a single member across a year."""
    member = get_object_or_404(Member, pk=member_id)
    year = int(request.GET.get('year', datetime.now().year))
    
    if request.method == 'POST':
        # Admin is bulk updating payments for this member
        from core.models import SystemSettings
        cfg = SystemSettings.get_settings()
        
        # Expected inputs: month_1=paid, amount_1=50, month_2=paid, amount_2=50...
        updated_count = 0
        for i in range(1, 13):
            is_paid = request.POST.get(f'month_{i}') == 'on'
            amount_str = request.POST.get(f'amount_{i}')
            
            period, _ = PaymentPeriod.objects.get_or_create(month=i, year=year)
            expected, _ = ExpectedPayment.objects.get_or_create(
                member=member, period=period,
                defaults={'amount': cfg.get_monthly_amount(i)}
            )
            
            actual, created = ActualPayment.objects.get_or_create(
                member=member, period=period,
                defaults={'amount_paid': 0, 'recorded_by': request.user}
            )
            
            if is_paid:
                amount_val = float(amount_str) if amount_str else float(expected.amount)
                if amount_val == 0: amount_val = float(cfg.get_monthly_amount(i)) # fallback
                if actual.amount_paid != amount_val:
                    actual.amount_paid = amount_val
                    actual.recorded_by = request.user
                    actual.save()
                    updated_count += 1
            else:
                if actual.amount_paid != 0:
                    actual.amount_paid = 0
                    actual.recorded_by = request.user
                    actual.save()
                    updated_count += 1
                    
        messages.success(request, f"Updated {updated_count} payment records for {member}.")
        return redirect(f"{request.path}?year={year}")
        
    # Get all periods for the year
    periods = PaymentPeriod.objects.filter(year=year).order_by('month')
    expected_qs = ExpectedPayment.objects.filter(member=member, period__in=periods)
    actual_qs = ActualPayment.objects.filter(member=member, period__in=periods)
    
    from core.models import SystemSettings
    cfg = SystemSettings.get_settings()
    
    months_data = []
    for i in range(1, 13):
        exp = next((e for e in expected_qs if e.period.month == i), None)
        act = next((a for a in actual_qs if a.period.month == i), None)
        
        default_amount = cfg.get_monthly_amount(i)
        
        months_data.append({
            'month': i,
            'month_name': datetime(year, i, 1).strftime('%B'),
            'expected_amount': exp.amount if exp else default_amount,
            'actual_amount': act.amount_paid if act else 0,
            'is_paid': (act.amount_paid > 0) if act else False,
        })
        
    return render(request, 'contributions/member_profile.html', {
        'member': member,
        'year': year,
        'year_range': range(2023, datetime.now().year + 3),
        'months_data': months_data,
    })
