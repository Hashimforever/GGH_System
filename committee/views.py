from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from .models import CommitteePosition, CommitteeAssignment
from .forms import CommitteePositionForm, CommitteeAssignmentForm

# --- POSITIONS ---
class PositionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CommitteePosition
    template_name = 'committee/position_list.html'
    context_object_name = 'positions'
    permission_required = 'committee.view_committeeposition'

class PositionCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = CommitteePosition
    form_class = CommitteePositionForm
    template_name = 'committee/position_form.html'
    success_url = reverse_lazy('committee:position_list')
    success_message = "Position %(title)s created."
    permission_required = 'committee.add_committeeposition'

class PositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CommitteePosition
    form_class = CommitteePositionForm
    template_name = 'committee/position_form.html'
    success_url = reverse_lazy('committee:position_list')
    success_message = "Position %(title)s updated."
    permission_required = 'committee.change_committeeposition'

# --- ASSIGNMENTS ---
class AssignmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CommitteeAssignment
    template_name = 'committee/assignment_list.html'
    context_object_name = 'assignments'
    permission_required = 'committee.view_committeeassignment'

class AssignmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = CommitteeAssignment
    form_class = CommitteeAssignmentForm
    template_name = 'committee/assignment_form.html'
    success_url = reverse_lazy('committee:assignment_list')
    success_message = "Assignment created."
    permission_required = 'committee.add_committeeassignment'

class AssignmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CommitteeAssignment
    form_class = CommitteeAssignmentForm
    template_name = 'committee/assignment_form.html'
    success_url = reverse_lazy('committee:assignment_list')
    success_message = "Assignment updated."
    permission_required = 'committee.change_committeeassignment'
