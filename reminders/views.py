import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .models import Appointment


class AppointmentListView(ListView):
    """Shows users a list of appointments"""
    
    model = Appointment
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created__date=datetime.date.today())


class AppointmentDetailView(DetailView):
    """Shows users a single appointment"""

    model = Appointment


class AppointmentCreateView(SuccessMessageMixin, CreateView):
    """Powers a form to create a new appointment"""

    model = Appointment
    fields = [
        "name",
        "phone_number",
        "home_phone",
        "time",
        "time_zone",
        "comm_pref",
        "email",
        "reminder_days",
    ]
    success_message = "Appointment successfully created."


class AppointmentUpdateView(SuccessMessageMixin, UpdateView):
    """Powers a form to edit existing appointments"""

    model = Appointment
    fields = [
        "name",
        "phone_number",
        "home_phone",
        "time",
        "time_zone",
        "comm_pref",
        "email",
    ]
    success_message = "Appointment successfully updated."


class AppointmentDeleteView(DeleteView):
    """Prompts users to confirm deletion of an appointment"""

    model = Appointment
    success_url = reverse_lazy("list_appointments")
