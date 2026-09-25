from django import forms
from .models import PaymentPeriod, ExpectedPayment, ActualPayment

class PaymentPeriodForm(forms.ModelForm):
    class Meta:
        model = PaymentPeriod
        fields = ['month', 'year']
        widgets = {
            'month': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ActualPaymentForm(forms.ModelForm):
    class Meta:
        model = ActualPayment
        fields = ['member', 'period', 'amount_paid', 'payment_date', 'payment_method', 'reference_number']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
