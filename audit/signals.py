from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from members.models import Member
from finance.models import FinancialTransaction
from loans.models import Loan
from contributions.models import ActualPayment
from .models import AuditLog
from .middleware import get_current_user

def log_action(instance, action):
    user = get_current_user()
    model_name = instance.__class__.__name__
    object_id = str(instance.pk)
    
    # Avoid recursive logging if it's the AuditLog itself, though we aren't listening to it
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        details=str(instance)
    )

@receiver(post_save, sender=Member)
@receiver(post_save, sender=FinancialTransaction)
@receiver(post_save, sender=Loan)
@receiver(post_save, sender=ActualPayment)
def log_post_save(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'
    log_action(instance, action)

@receiver(post_delete, sender=Member)
@receiver(post_delete, sender=FinancialTransaction)
@receiver(post_delete, sender=Loan)
@receiver(post_delete, sender=ActualPayment)
def log_post_delete(sender, instance, **kwargs):
    log_action(instance, 'Deleted')
