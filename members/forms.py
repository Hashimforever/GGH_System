from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Member, MemberChild, OtherFamilyMember

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
        # Pre-fill initial values shown in form when rendering blank (GET)
        today = timezone.now().date().isoformat()
        if not self.instance.pk:
            self.fields['date_of_membership'].initial = today
            self.fields['status'].initial = 'active'
            self.fields['marital_status'].initial = 'single'
        # Mark clearly optional fields
        for field_name in ['gender', 'date_of_birth', 'phone_number', 'email',
                           'residential_address', 'occupation', 'spouse_name',
                           'spouse_phone', 'emergency_contact_name',
                           'emergency_contact_phone', 'photo']:
            self.fields[field_name].required = False
        # Make status/marital_status/date_of_membership not strictly required
        # because we supply defaults in clean()
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
