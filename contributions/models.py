from django.db import models
from members.models import Member
from django.utils import timezone

class PaymentPeriod(models.Model):
    month = models.IntegerField(choices=[(i, i) for i in range(1, 13)])
    year = models.IntegerField(default=timezone.now().year)

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"{self.month}/{self.year}"

class ExpectedPayment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='expected_payments')
    period = models.ForeignKey(PaymentPeriod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('member', 'period')

    def __str__(self):
        return f"{self.member} - {self.period} - {self.amount}"

class ActualPayment(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overpaid', 'Overpaid'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='actual_payments')
    period = models.ForeignKey(PaymentPeriod, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        expected = ExpectedPayment.objects.filter(member=self.member, period=self.period).first()
        if expected:
            if self.amount_paid == 0:
                self.status = 'unpaid'
            elif self.amount_paid < expected.amount:
                self.status = 'partial'
            elif self.amount_paid == expected.amount:
                self.status = 'paid'
            else:
                self.status = 'overpaid'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member} - {self.period} - {self.amount_paid}"
