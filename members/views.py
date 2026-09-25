from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Member
from .forms import MemberForm, MemberChildFormSet, OtherFamilyMemberFormSet

@login_required
def member_list(request):
    members = Member.objects.all().order_by('-date_of_membership')
    return render(request, 'members/member_list.html', {'members': members})

@login_required
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        child_formset = MemberChildFormSet(request.POST, prefix='children')
        family_formset = OtherFamilyMemberFormSet(request.POST, prefix='family')
        
        if form.is_valid() and child_formset.is_valid() and family_formset.is_valid():
            member = form.save()
            child_formset.instance = member
            child_formset.save()
            family_formset.instance = member
            family_formset.save()
            messages.success(request, f'Member {member.member_id} successfully registered!')
            return redirect('members:member_list')
    else:
        form = MemberForm()
        child_formset = MemberChildFormSet(prefix='children')
        family_formset = OtherFamilyMemberFormSet(prefix='family')
    
    return render(request, 'members/member_form.html', {
        'form': form, 
        'child_formset': child_formset,
        'family_formset': family_formset,
        'title': 'Register New Member'
    })

@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        child_formset = MemberChildFormSet(request.POST, instance=member, prefix='children')
        family_formset = OtherFamilyMemberFormSet(request.POST, instance=member, prefix='family')

        if form.is_valid() and child_formset.is_valid() and family_formset.is_valid():
            form.save()
            child_formset.save()
            family_formset.save()
            messages.success(request, f'Member {member.member_id} updated successfully!')
            return redirect('members:member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)
        child_formset = MemberChildFormSet(instance=member, prefix='children')
        family_formset = OtherFamilyMemberFormSet(instance=member, prefix='family')

    return render(request, 'members/member_form.html', {
        'form': form,
        'child_formset': child_formset,
        'family_formset': family_formset,
        'title': f'Edit Member — {member.member_id}',
        'member': member,
        'is_edit': True,
    })

from contributions.models import ExpectedPayment, ActualPayment
from loans.models import Loan

@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    expected_payments = ExpectedPayment.objects.filter(member=member).order_by('-period__year', '-period__month')
    actual_payments = ActualPayment.objects.filter(member=member).order_by('-payment_date')
    loans = Loan.objects.filter(member=member).order_by('-application_date')
    
    return render(request, 'members/member_detail.html', {
        'member': member,
        'expected_payments': expected_payments,
        'actual_payments': actual_payments,
        'loans': loans
    })
