from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Member, MemberRegistrationRequest, MemberChild
from .forms import (
    MemberForm, MemberChildFormSet, OtherFamilyMemberFormSet,
    MemberRegistrationForm, RegistrationReviewForm,
)

User = get_user_model()


# ═══════════════════════════════════════════════════════════════
#   EXISTING MEMBER VIEWS (unchanged)
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
#   NEW: PUBLIC REGISTRATION
# ═══════════════════════════════════════════════════════════════

def register(request):
    """Public registration form — no login required."""
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            reg = form.save()
            messages.success(
                request,
                "Your registration request has been submitted. "
                "An administrator will review it shortly."
            )
            # Optional: notify admins by email
            try:
                admin_emails = list(User.objects.filter(is_superuser=True)
                                    .exclude(email='')
                                    .values_list('email', flat=True))
                if admin_emails:
                    send_mail(
                        subject=f"New Member Registration: {reg.full_name}",
                        message=(
                            f"A new registration request was submitted.\n\n"
                            f"Name: {reg.full_name}\n"
                            f"Phone: {reg.phone_number}\n"
                            f"Email: {reg.email}\n\n"
                            f"Review it in the admin panel."
                        ),
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ggh.local'),
                        recipient_list=admin_emails,
                        fail_silently=True,
                    )
            except Exception:
                pass
            return redirect('members:register_success')
    else:
        form = MemberRegistrationForm()
    return render(request, 'members/register.html', {'form': form})


def register_success(request):
    return render(request, 'members/register_success.html')


# ═══════════════════════════════════════════════════════════════
#   NEW: ADMIN REVIEW
# ═══════════════════════════════════════════════════════════════

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


@login_required
@user_passes_test(is_admin)
def registration_requests(request):
    """Admin-only list of pending registration requests."""
    status_filter = request.GET.get('status', 'pending')
    qs = MemberRegistrationRequest.objects.all()
    if status_filter in ['pending', 'approved', 'rejected']:
        qs = qs.filter(status=status_filter)

    counts = {
        'pending': MemberRegistrationRequest.objects.filter(status='pending').count(),
        'approved': MemberRegistrationRequest.objects.filter(status='approved').count(),
        'rejected': MemberRegistrationRequest.objects.filter(status='rejected').count(),
    }

    return render(request, 'members/registration_requests.html', {
        'requests': qs,
        'status_filter': status_filter,
        'counts': counts,
    })


@login_required
@user_passes_test(is_admin)
def registration_detail(request, pk):
    reg = get_object_or_404(MemberRegistrationRequest, pk=pk)
    return render(request, 'members/registration_detail.html', {'reg': reg})


@login_required
@user_passes_test(is_admin)
def registration_approve(request, pk):
    """Approve a pending registration → create Member + User + send welcome email."""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings as dj_settings

    reg = get_object_or_404(MemberRegistrationRequest, pk=pk)

    if reg.status != 'pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('members:registration_requests')

    if request.method == 'POST':
        # ── 1. Create the Member ──
        member = Member.objects.create(
            first_name=reg.first_name,
            last_name=reg.last_name,
            gender=reg.gender,
            date_of_birth=reg.date_of_birth,
            phone_number=reg.phone_number,
            email=reg.email,
            residential_address=reg.residential_address,
            occupation=reg.occupation,
            marital_status=reg.marital_status,
            status='active',
            spouse_name=reg.spouse_name,
            spouse_phone=reg.spouse_phone,
            husband_father_alive=reg.father_alive,
            husband_mother_alive=reg.mother_alive,
            wife_father_alive=reg.spouse_father_alive,
            wife_mother_alive=reg.spouse_mother_alive,
            emergency_contact_name=reg.emergency_contact_name,
            emergency_contact_phone=reg.emergency_contact_phone,
        )

        # ── 2. Parse children ──
        if reg.children_details:
            from datetime import datetime
            for line in reg.children_details.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split('|')]
                if not parts or not parts[0]:
                    continue
                child = MemberChild(member=member, name=parts[0])
                if len(parts) >= 2 and parts[1]:
                    try:
                        child.date_of_birth = datetime.strptime(parts[1], '%Y-%m-%d').date()
                    except ValueError:
                        pass
                child.save()

        # ── 3. Create User account + SEND WELCOME EMAIL ──
        username = None
        temp_password = None
        email_sent = False
        email_error = None

        if reg.email:
            base_username = reg.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            temp_password = 'ChangeMe@123'
            try:
                User.objects.create_user(
                    username=username,
                    email=reg.email,
                    password=temp_password,
                )
                reg.admin_notes = (reg.admin_notes or '') + f"\nUser account created: {username}"

                # ── Build and send the email ──
                try:
                    site_url = dj_settings.SITE_URL if hasattr(dj_settings, 'SITE_URL') \
                               else request.build_absolute_uri('/').rstrip('/')
                    login_url = f"{site_url}/auth/login/"

                    context = {
                        'member': member,
                        'username': username,
                        'password': temp_password,
                        'login_url': login_url,
                        'association_name': getattr(dj_settings, 'ASSOCIATION_NAME', 'GGH Community Association'),
                    }

                    subject = f"Welcome to {context['association_name']} — Your Account is Ready"

                    # Render both HTML and plain-text versions
                    text_body = render_to_string('members/emails/welcome_email.txt', context)
                    html_body = render_to_string('members/emails/welcome_email.html', context)

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_body,
                        from_email=dj_settings.DEFAULT_FROM_EMAIL,
                        to=[reg.email],
                    )
                    msg.attach_alternative(html_body, "text/html")
                    msg.send(fail_silently=False)

                    email_sent = True
                    reg.admin_notes = (reg.admin_notes or '') + f"\nWelcome email sent to {reg.email}"

                except Exception as mail_err:
                    email_error = str(mail_err)
                    reg.admin_notes = (reg.admin_notes or '') + f"\nEmail failed: {mail_err}"

            except Exception as e:
                reg.admin_notes = (reg.admin_notes or '') + f"\nUser creation failed: {e}"

        # ── 4. Mark approved ──
        reg.status = 'approved'
        reg.reviewed_at = timezone.now()
        reg.reviewed_by = request.user
        reg.save()

        # ── 5. Show result message ──
        if email_sent:
            messages.success(
                request,
                f"✅ Approved: {reg.full_name} is now member {member.member_id}. "
                f"Welcome email sent to {reg.email}."
            )
        elif email_error:
            messages.warning(
                request,
                f"⚠️ Approved: {reg.full_name} is now member {member.member_id}. "
                f"BUT the welcome email failed: {email_error}"
            )
        elif not reg.email:
            messages.warning(
                request,
                f"⚠️ Approved: {reg.full_name} is now member {member.member_id}. "
                f"No email on file — please contact them manually."
            )
        else:
            messages.success(
                request,
                f"Approved: {reg.full_name} is now member {member.member_id}."
            )

        return redirect('members:registration_requests')

    return render(request, 'members/registration_approve_confirm.html', {'reg': reg})


@login_required
@user_passes_test(is_admin)
def registration_reject(request, pk):
    reg = get_object_or_404(MemberRegistrationRequest, pk=pk)

    if reg.status != 'pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('members:registration_requests')

    if request.method == 'POST':
        form = RegistrationReviewForm(request.POST, instance=reg)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.status = 'rejected'
            reg.reviewed_at = timezone.now()
            reg.reviewed_by = request.user
            reg.save()
            messages.info(request, f"Rejected: {reg.full_name}.")
            return redirect('members:registration_requests')
    else:
        form = RegistrationReviewForm(instance=reg)

    return render(request, 'members/registration_reject.html', {'reg': reg, 'form': form})