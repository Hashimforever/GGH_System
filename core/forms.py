from django import forms
from .models import SystemSettings, HomePage, Announcement
import calendar


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        exclude = ['updated_at']
        widgets = {
            'association_name': forms.TextInput(attrs={'class': 'form-control'}),
            'association_tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'association_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'association_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'association_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 5}),
            'registration_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'default_monthly_contribution': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loan_interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_loan_multiplier': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_payment_penalty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'january_amount':   forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'february_amount':  forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'march_amount':     forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'april_amount':     forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'may_amount':       forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'june_amount':      forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'july_amount':      forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'august_amount':    forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'september_amount': forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'october_amount':   forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'november_amount':  forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'december_amount':  forms.NumberInput(attrs={'class': 'form-control month-amount', 'step': '0.01', 'placeholder': 'Use default'}),
            'fiscal_year_start_month': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'january_amount': 'January', 'february_amount': 'February', 'march_amount': 'March',
            'april_amount': 'April', 'may_amount': 'May', 'june_amount': 'June',
            'july_amount': 'July', 'august_amount': 'August', 'september_amount': 'September',
            'october_amount': 'October', 'november_amount': 'November', 'december_amount': 'December',
        }


class HomePageForm(forms.ModelForm):
    class Meta:
        model = HomePage
        exclude = ['updated_at']
        widgets = {
            'hero_title': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_background_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'hero_text_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'login_button_label': forms.TextInput(attrs={'class': 'form-control'}),
            'about_title': forms.TextInput(attrs={'class': 'form-control'}),
            'about_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'announcements_title': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_title': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body', 'is_active', 'pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
