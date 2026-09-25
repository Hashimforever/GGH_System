from django import forms
from .models import CommitteePosition, CommitteeAssignment
from members.models import Member

class CommitteePositionForm(forms.ModelForm):
    class Meta:
        model = CommitteePosition
        fields = ('title', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CommitteeAssignmentForm(forms.ModelForm):
    class Meta:
        model = CommitteeAssignment
        fields = ('member', 'position', 'start_date', 'end_date')
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
