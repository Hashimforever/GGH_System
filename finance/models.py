from django.db import models
from django.utils import timezone

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    category = models.CharField(max_length=100, default="General", help_text="e.g. Office Supplies, Maintenance, Event")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    transaction_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recorded_by = models.ForeignKey('accounts.User', related_name='recorded_withdrawals', on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey('accounts.User', related_name='approved_withdrawals', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.purpose} - {self.amount} ({self.status})"

class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('income_contribution', 'Member Contribution'),
        ('income_registration', 'Registration Fee'),
        ('income_other', 'Other Income'),
        ('income_loan_repayment', 'Loan Repayment'),
        ('expense_withdrawal', 'Withdrawal/Expense'),
        ('expense_loan_disbursement', 'Loan Disbursement'),
    ]

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255)
    
    # Generic relations could be used, but explicit fields are simpler if sparse
    payment = models.ForeignKey('contributions.ActualPayment', null=True, blank=True, on_delete=models.CASCADE)
    withdrawal = models.ForeignKey(Withdrawal, null=True, blank=True, on_delete=models.CASCADE)
    loan_disbursement = models.ForeignKey('loans.Loan', null=True, blank=True, on_delete=models.CASCADE)
    loan_repayment = models.ForeignKey('loans.LoanRepayment', null=True, blank=True, on_delete=models.CASCADE)
    member = models.ForeignKey('members.Member', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"
