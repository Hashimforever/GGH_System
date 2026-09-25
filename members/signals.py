from django.db.models.signals import post_save
from django.dispatch import receiver
from members.models import Member
from finance.models import FinancialTransaction
from core.models import SystemSettings

@receiver(post_save, sender=Member)
def create_registration_fee_transaction(sender, instance, created, **kwargs):
    if created:
        settings = SystemSettings.get_settings()
        if settings.registration_fee > 0:
            FinancialTransaction.objects.create(
                transaction_type='income_registration',
                amount=settings.registration_fee,
                member=instance,
                description=f"Registration fee for new member {instance.member_id}"
            )
