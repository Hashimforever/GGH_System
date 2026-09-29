from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import (
    Member, MemberChild, OtherFamilyMember,
    MemberRegistrationRequest,
)


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'gender', 'date_of_birth', 
            'phone_number', 'email', 'residential_address', 
            'date_of_membership', 'status', 'occupation',
            'marital_status', 'spouse_name', 'spouse_phone',
            'husband_father_alive', 'husband_mother_alive',
            'wife_father_alive', 'wife_mother_alive',
            'emergency_contact_name', 'emergency_contact_phone', 'photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_membership': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'residential_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control', 'id': 'id_marital_status'}),
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date().isoformat()
        if not self.instance.pk:
            self.fields['date_of_membership'].initial = today
            self.fields['status'].initial = 'active'
            self.fields['marital_status'].initial = 'single'
        for field_name in ['gender', 'date_of_birth', 'phone_number', 'email',
                           'residential_address', 'occupation', 'spouse_name',
                           'spouse_phone', 'emergency_contact_name',
                           'emergency_contact_phone', 'photo']:
            self.fields[field_name].required = False
        self.fields['date_of_membership'].required = False
        self.fields['status'].required = False
        self.fields['marital_status'].required = False

    def clean_date_of_membership(self):
        val = self.cleaned_data.get('date_of_membership')
        if not val:
            return timezone.now().date()
        return val

    def clean_status(self):
        val = self.cleaned_data.get('status')
        if not val:
            return 'active'
        return val

    def clean_marital_status(self):
        val = self.cleaned_data.get('marital_status')
        if not val:
            return 'single'
        return val


MemberChildFormSet = inlineformset_factory(
    Member, MemberChild,
    fields=['name', 'date_of_birth'],
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    }
)

OtherFamilyMemberFormSet = inlineformset_factory(
    Member, OtherFamilyMember,
    fields=['name', 'relation'],
    extra=1,
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'relation': forms.TextInput(attrs={'class': 'form-control'}),
    }
)


# ═══════════════════════════════════════════════════════════════
#   Public member registration system
# ═══════════════════════════════════════════════════════════════

class MemberRegistrationForm(forms.ModelForm):
    """Public registration form — no login required."""
    class Meta:
        model = MemberRegistrationRequest
        fields = [
            # Personal
            'first_name', 'last_name', 'gender', 'date_of_birth',
            'phone_number', 'email', 'residential_address',
            'occupation', 'marital_status',

            # Spouse (shown only if married)
            'spouse_name', 'spouse_phone', 'spouse_occupation',

            # Applicant's parents
            'father_name', 'father_alive',
            'mother_name', 'mother_alive',

            # Spouse's parents
            'spouse_father_name', 'spouse_father_alive',
            'spouse_mother_name', 'spouse_mother_alive',

            # Children & emergency
            'children_details',
            'emergency_contact_name', 'emergency_contact_phone',
        ]
        widgets = {
            # Personal
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0907773121'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'residential_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-control', 'id': 'id_marital_status'}),

            # Spouse
            'spouse_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_occupation': forms.TextInput(attrs={'class': 'form-control'}),

            # Parents
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_alive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_alive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'spouse_father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_father_alive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'spouse_mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'spouse_mother_alive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Children & emergency
            'children_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Example:\nAbdi | 2015-03-12 | Male\nHanna | 2018-07-25 | Female'
            }),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if len(phone) < 7:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean(self):
        cleaned = super().clean()
        married = cleaned.get('marital_status') == 'married'
        # If married, spouse name is required
        if married and not cleaned.get('spouse_name'):
            self.add_error('spouse_name', "Please enter your spouse's name.")
        return cleaned


class RegistrationReviewForm(forms.ModelForm):
    """Used by admin to reject with a reason or add notes."""
    class Meta:
        model = MemberRegistrationRequest
        fields = ['rejection_reason', 'admin_notes']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }