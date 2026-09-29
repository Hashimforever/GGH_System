from django import forms
from django.utils import timezone
from .models import Property, Loaner, PropertyLoan, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'code', 'category', 'description', 'quantity_total',
                  'quantity_available', 'unit_price', 'purchase_date', 'status',
                  'image', 'location', 'notes', 'deduct_from_finance']   # ⭐ NEW
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantity_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_available': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'deduct_from_finance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),   # ⭐ NEW
        }


class LoanerForm(forms.ModelForm):
    class Meta:
        model = Loaner
        fields = ['full_name', 'phone', 'email', 'id_number', 'address', 'is_member', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_member': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PropertyLoanForm(forms.ModelForm):
    class Meta:
        model = PropertyLoan
        fields = ['loan_code', 'property_item', 'loaner', 'quantity',
                  'loan_date', 'expected_return_date', 'purpose',
                  'condition_on_loan', 'notes']
        widgets = {
            'loan_code': forms.TextInput(attrs={'class': 'form-control'}),
            'property_item': forms.Select(attrs={'class': 'form-control'}),
            'loaner': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'condition_on_loan': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        prop = cleaned.get('property_item')
        qty = cleaned.get('quantity')
        if prop and qty:
            if qty > prop.quantity_available:
                raise forms.ValidationError(
                    f"Only {prop.quantity_available} unit(s) of '{prop.name}' are available."
                )
        return cleaned


class ReturnLoanForm(forms.ModelForm):
    class Meta:
        model = PropertyLoan
        fields = ['actual_return_date', 'condition_on_return', 'notes']
        widgets = {
            'actual_return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'condition_on_return': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LoanerWithLoanForm(forms.ModelForm):
    """
    Combined form: Create a Loaner AND optionally record a material loan
    in a single submission.
    """
    # ── Optional Loan fields ──
    property_item = forms.ModelChoiceField(
        queryset=Property.objects.filter(quantity_available__gt=0),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Material to Loan",
        empty_label="— Select material (optional) —",
    )
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    loan_date = forms.DateField(
        required=False,
        initial=timezone.now,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    expected_return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    purpose = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Purpose",
    )
    condition_on_loan = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Condition on Loan",
    )
    loan_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Loan Code (leave blank to auto-generate)",
    )

    class Meta:
        model = Loaner
        fields = ['full_name', 'phone', 'email', 'id_number', 'address', 'is_member', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_member': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        prop = cleaned.get('property_item')
        qty = cleaned.get('quantity')
        loan_date = cleaned.get('loan_date')
        expected_return = cleaned.get('expected_return_date')

        if prop:
            if not qty or qty < 1:
                self.add_error('quantity', "Quantity must be at least 1 when loaning a material.")
            elif qty > prop.quantity_available:
                self.add_error('quantity',
                    f"Only {prop.quantity_available} unit(s) of '{prop.name}' are available.")
            if not expected_return:
                self.add_error('expected_return_date', "Please set an expected return date.")
            if expected_return and loan_date and expected_return < loan_date:
                self.add_error('expected_return_date',
                    "Expected return date cannot be before the loan date.")
        return cleaned

    def save(self, commit=True):
        loaner = super().save(commit=commit)

        prop = self.cleaned_data.get('property_item')
        if prop and commit:
            qty = self.cleaned_data.get('quantity') or 1
            code = self.cleaned_data.get('loan_code') or self._generate_loan_code()

            loan = PropertyLoan.objects.create(
                loan_code=code,
                property_item=prop,
                loaner=loaner,
                quantity=qty,
                loan_date=self.cleaned_data.get('loan_date') or timezone.now().date(),
                expected_return_date=self.cleaned_data.get('expected_return_date'),
                purpose=self.cleaned_data.get('purpose', ''),
                condition_on_loan=self.cleaned_data.get('condition_on_loan', ''),
                handled_by=getattr(self, 'current_user', None),
            )

            prop.quantity_available = max(0, prop.quantity_available - qty)
            if prop.quantity_available == 0:
                prop.status = 'loaned'
            prop.save()

        return loaner

    def _generate_loan_code(self):
        last = PropertyLoan.objects.order_by('-id').first()
        next_id = (last.id + 1) if last else 1
        return f"LOAN-{next_id:04d}"