from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from members.models import Member
from finance.models import FinancialTransaction
from loans.models import Loan
from .models import SystemSettings, HomePage, Announcement
from .forms import SystemSettingsForm, HomePageForm, AnnouncementForm


# ──────────────────────────────────────────────
# PUBLIC: Home page (no login required)
# ──────────────────────────────────────────────
def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    content = HomePage.get_content()
    sys = SystemSettings.get_settings()
    announcements = Announcement.objects.filter(is_active=True)

    stats = {}
    if content.show_stats:
        from django.utils import timezone
        stats = {
            'total_members': Member.objects.filter(status='active').count(),
            'years_active': timezone.now().year - 2020,  # adjust founding year via settings later
        }

    return render(request, 'core/home.html', {
        'content': content,
        'sys': sys,
        'announcements': announcements,
        'stats': stats,
    })


# ──────────────────────────────────────────────
# PROTECTED: Dashboard
# ──────────────────────────────────────────────
@login_required
def dashboard(request):
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='active').count()

    incomes = FinancialTransaction.objects.filter(
        transaction_type__startswith='income_'
    ).aggregate(total=Sum('amount'))['total'] or 0
    expenses = FinancialTransaction.objects.filter(
        transaction_type__startswith='expense_'
    ).aggregate(total=Sum('amount'))['total'] or 0
    cash_balance = incomes - expenses
    active_loans = Loan.objects.filter(status='active').count()
    settings = SystemSettings.get_settings()

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'cash_balance': cash_balance,
        'incomes': incomes,
        'expenses': expenses,
        'active_loans': active_loans,
        'settings': settings,
    }
    return render(request, 'core/dashboard.html', context)


# ──────────────────────────────────────────────
# PROTECTED: System Settings
# ──────────────────────────────────────────────
@login_required
def system_settings(request):
    obj = SystemSettings.get_settings()
    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'System settings saved successfully.')
            return redirect('core:settings')
    else:
        form = SystemSettingsForm(instance=obj)
    return render(request, 'core/settings.html', {'form': form, 'settings': obj})


# ──────────────────────────────────────────────
# PROTECTED: Homepage Content Management
# ──────────────────────────────────────────────
@login_required
def manage_homepage(request):
    obj = HomePage.get_content()
    if request.method == 'POST':
        form = HomePageForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homepage content updated successfully.')
            return redirect('core:manage_homepage')
    else:
        form = HomePageForm(instance=obj)

    announcements = Announcement.objects.all()
    return render(request, 'core/manage_homepage.html', {
        'form': form,
        'announcements': announcements,
    })


@login_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement added.')
            return redirect('core:manage_homepage')
    else:
        form = AnnouncementForm()
    return render(request, 'core/announcement_form.html', {'form': form, 'title': 'New Announcement'})


@login_required
def announcement_edit(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated.')
            return redirect('core:manage_homepage')
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, 'core/announcement_form.html', {'form': form, 'title': 'Edit Announcement'})


@login_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, 'Announcement deleted.')
    return redirect('core:manage_homepage')
