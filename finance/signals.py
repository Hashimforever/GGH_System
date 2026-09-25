from django.db.models.signals import post_save
from django.dispatch import receiver
from contributions.models import ActualPayment
from loans.models import Loan, LoanRepayment
from .models import Withdrawal, FinancialTransaction


@receiver(post_save, sender=ActualPayment)
def sync_contribution_transaction(sender, instance, **kwargs):
    """Create or update the FinancialTransaction whenever a contribution payment is saved."""
    if instance.amount_paid and instance.amount_paid > 0:
        obj, created = FinancialTransaction.objects.get_or_create(
            payment=instance,
            defaults={
                'transaction_type': 'income_contribution',
                'amount': instance.amount_paid,
                'description': f"Contribution by {instance.member.member_id} for {instance.period}",
            }
        )
        if not created and obj.amount != instance.amount_paid:
            obj.amount = instance.amount_paid
            obj.save()
    else:
        # amount_paid went to 0 (marked unpaid) — remove the transaction
        FinancialTransaction.objects.filter(payment=instance).delete()


@receiver(post_save, sender=Withdrawal)
def create_withdrawal_transaction(sender, instance, **kwargs):
    """Create a ledger entry once a withdrawal is approved."""
    if instance.status == 'approved':
        FinancialTransaction.objects.get_or_create(
            withdrawal=instance,
            defaults={
                'transaction_type': 'expense_withdrawal',
                'amount': instance.amount,
                'description': f"Withdrawal: {instance.purpose}",
            }
        )


@receiver(post_save, sender=Loan)
def create_loan_disbursement_transaction(sender, instance, **kwargs):
    """Create a ledger entry once a loan is approved and active."""
    if instance.status == 'active':
        FinancialTransaction.objects.get_or_create(
            loan_disbursement=instance,
            defaults={
                'transaction_type': 'expense_loan_disbursement',
                'amount': instance.amount,
                'description': f"Loan disbursed to {instance.member.member_id}",
            }
        )


@receiver(post_save, sender=LoanRepayment)
def create_loan_repayment_transaction(sender, instance, created, **kwargs):
    """Record income whenever a loan repayment is made."""
    if created and instance.amount > 0:
        FinancialTransaction.objects.create(
            transaction_type='income_loan_repayment',
            amount=instance.amount,
            loan_repayment=instance,
            description=f"Loan repayment by {instance.loan.member.member_id}",
        )
