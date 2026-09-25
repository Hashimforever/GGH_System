from django.db import models
from django.utils import timezone

class Member(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('resigned', 'Resigned'),
    ]

    member_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    residential_address = models.TextField(blank=True)
    date_of_membership = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    occupation = models.CharField(max_length=100, blank=True)
    
    # Marital and Family Status
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, default='single')
    
    # If married
    spouse_name = models.CharField(max_length=100, blank=True)
    spouse_phone = models.CharField(max_length=20, blank=True)
    
    # Parent status (using generic terms or specific as requested)
    husband_father_alive = models.BooleanField(default=True, verbose_name="Member's Father Alive")
    husband_mother_alive = models.BooleanField(default=True, verbose_name="Member's Mother Alive")
    wife_father_alive = models.BooleanField(default=True, verbose_name="Spouse's Father Alive")
    wife_mother_alive = models.BooleanField(default=True, verbose_name="Spouse's Mother Alive")
    
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='members/photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            year = timezone.now().year
            last_member = Member.objects.filter(member_id__endswith=f"/{year}").order_by('id').last()
            if last_member:
                last_num = int(last_member.member_id.split('/')[0].replace('GGH', ''))
                new_num = last_num + 1
            else:
                new_num = 1
            self.member_id = f"GGH{new_num:03d}/{year}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.member_id})"

class MemberChild(models.Model):
    member = models.ForeignKey(Member, related_name='children', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class OtherFamilyMember(models.Model):
    member = models.ForeignKey(Member, related_name='other_family_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.relation})'

