from django.db import models
from django.utils import timezone
import calendar


class HomePage(models.Model):
    """
    Singleton model for the public-facing homepage content.
    Managed by the admin from the portal.
    """
    # --- Hero Section ---
    hero_title = models.CharField(
        max_length=200, default='Welcome to GGH Community',
        help_text='Large heading displayed in the hero banner.'
    )
    hero_subtitle = models.CharField(
        max_length=400, blank=True,
        help_text='Short tagline under the hero title.'
    )
    hero_background_color = models.CharField(
        max_length=20, default='#343a40',
        help_text='CSS color for the hero background (e.g. #343a40 or #1a6b3c).'
    )
    hero_text_color = models.CharField(max_length=20, default='#ffffff')
    show_login_button = models.BooleanField(default=True)
    login_button_label = models.CharField(max_length=60, default='Member Login')

    # --- About Section ---
    show_about = models.BooleanField(default=True)
    about_title = models.CharField(max_length=200, default='About Us')
    about_body = models.TextField(
        blank=True,
        help_text='Rich text / paragraphs describing the association.'
    )

    # --- Announcements Section ---
    show_announcements = models.BooleanField(default=True)
    announcements_title = models.CharField(max_length=200, default='Latest Announcements')

    # --- Contact / Footer Section ---
    show_contact = models.BooleanField(default=True)
    contact_title = models.CharField(max_length=200, default='Contact Us')
    contact_body = models.TextField(blank=True)

    # --- Stats counters (optional display) ---
    show_stats = models.BooleanField(default=True, help_text='Show member count / year counters on homepage.')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Home Page Content'

    def __str__(self):
        return 'Home Page Content'

    @classmethod
    def get_content(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    pinned = models.BooleanField(default=False, help_text='Show at the top of the list.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pinned', '-created_at']

    def __str__(self):
        return self.title


class SystemSettings(models.Model):
    """
    Singleton model — only one record should exist.
    Accessed via SystemSettings.get_settings().
    """
    # --- Association Info ---
    association_name = models.CharField(max_length=200, default='GGH Community Association')
    association_tagline = models.CharField(max_length=255, blank=True, default='')
    association_email = models.EmailField(blank=True)
    association_phone = models.CharField(max_length=30, blank=True)
    association_address = models.TextField(blank=True)
    currency_symbol = models.CharField(max_length=10, default='$')

    # --- Financial Defaults ---
    registration_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text='One-time registration / joining fee for new members.'
    )
    default_monthly_contribution = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text='Default monthly contribution amount used when auto-generating expected payments.'
    )
    loan_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text='Annual interest rate (%) applied to loans.'
    )
    max_loan_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2, default=3.00,
        help_text='Maximum loan amount as a multiple of total contributions.'
    )
    late_payment_penalty = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text='Fixed penalty charged for late monthly contributions.'
    )

    # --- Per-Month Override ---
    january_amount   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Leave blank to use default')
    february_amount  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    march_amount     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    april_amount     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    may_amount       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    june_amount      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    july_amount      = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    august_amount    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    september_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    october_amount   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    november_amount  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    december_amount  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # --- Other Settings ---
    fiscal_year_start_month = models.IntegerField(
        default=1,
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        help_text='Month the financial year begins (usually January).'
    )
    enable_late_penalty = models.BooleanField(default=False)
    allow_partial_payments = models.BooleanField(default=True)
    auto_generate_expected_on_member_create = models.BooleanField(
        default=False,
        help_text='Automatically create ExpectedPayments for all months when a new member is registered.'
    )

    updated_at = models.DateTimeField(auto_now=True)

    MONTH_FIELDS = [
        'january_amount', 'february_amount', 'march_amount', 'april_amount',
        'may_amount', 'june_amount', 'july_amount', 'august_amount',
        'september_amount', 'october_amount', 'november_amount', 'december_amount'
    ]

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return 'System Settings'

    @classmethod
    def get_settings(cls):
        """Return the single settings record, creating it if it doesn't exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_monthly_amount(self, month_number):
        """Return the configured amount for a specific month (1–12)."""
        field = self.MONTH_FIELDS[month_number - 1]
        override = getattr(self, field)
        return override if override is not None else self.default_monthly_contribution

    def get_annual_expected(self):
        """Return total expected annual contribution per member."""
        return sum(self.get_monthly_amount(m) for m in range(1, 13))

    def get_month_summary(self):
        """Return a list of (month_name, amount) for display."""
        return [
            (calendar.month_name[m], self.get_monthly_amount(m))
            for m in range(1, 13)
        ]
