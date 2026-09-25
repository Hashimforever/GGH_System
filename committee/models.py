from django.db import models
from members.models import Member

class CommitteePosition(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class CommitteeAssignment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='committee_assignments')
    position = models.ForeignKey(CommitteePosition, on_delete=models.CASCADE, related_name='assignments')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.member} - {self.position} ({self.start_date} to {self.end_date or 'Present'})"
