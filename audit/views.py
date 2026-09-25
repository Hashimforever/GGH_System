from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import AuditLog

class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit/auditlog_list.html'
    context_object_name = 'logs'
    permission_required = 'audit.view_auditlog'
    paginate_by = 50
    ordering = ['-timestamp']
