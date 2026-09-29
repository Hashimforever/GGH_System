from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Category of property/material (e.g., Chairs, Tents, Sound System)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    """A material/property item owned by the community."""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('loaned', 'Loaned Out'),
        ('damaged', 'Damaged'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, help_text="Unique property code e.g. PROP-001")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    description = models.TextField(blank=True, null=True)
    quantity_total = models.PositiveIntegerField(default=1)
    quantity_available = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='property/images/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True, help_text="Where the item is stored")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ⭐ FINANCE INTEGRATION
    deduct_from_finance = models.BooleanField(
        default=False,
        verbose_name="Deduct cost from Finance (creates a Withdrawal)",
        help_text="When checked, the total cost (unit_price × quantity_total) "
                  "is recorded as a withdrawal in the Finance module."
    )

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_low_stock(self):
        return self.quantity_available <= 1

    @property
    def total_cost(self):
        """Total purchase cost = unit_price × quantity_total."""
        try:
            return (self.unit_price or 0) * (self.quantity_total or 0)
        except Exception:
            return 0


class Loaner(models.Model):
    """A person who borrows materials."""
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True, help_text="National ID / Member ID")
    address = models.CharField(max_length=255, blank=True, null=True)
    is_member = models.BooleanField(default=False, help_text="Is this person a registered community member?")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def active_loans_count(self):
        return self.loans.filter(status__in=['active', 'overdue']).count()


class PropertyLoan(models.Model):
    """A loan record of a property/material to a loaner."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('partial', 'Partially Returned'),
        ('lost', 'Lost'),
    ]

    loan_code = models.CharField(max_length=50, unique=True, help_text="e.g. LOAN-001")
    property_item = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='loans')
    loaner = models.ForeignKey(Loaner, on_delete=models.CASCADE, related_name='loans')
    quantity = models.PositiveIntegerField(default=1)
    loan_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    purpose = models.TextField(blank=True, null=True, help_text="Why is it being borrowed?")
    condition_on_loan = models.CharField(max_length=200, blank=True, null=True)
    condition_on_return = models.CharField(max_length=200, blank=True, null=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='property_loans_handled'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.loan_code} - {self.property_item.name} → {self.loaner.full_name}"

    @property
    def is_overdue(self):
        if self.status in ['returned', 'lost']:
            return False
        return timezone.now().date() > self.expected_return_date

    def save(self, *args, **kwargs):
        # Auto-set overdue status
        if self.is_overdue and self.status == 'active':
            self.status = 'overdue'
        super().save(*args, **kwargs)