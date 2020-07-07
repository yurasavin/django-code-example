from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.urls import reverse_lazy

from tickets.models import Ticket

from .models import Tender


class TenderCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView,
):
    """Представление для создания закупки"""
    model = Tender
    permission_required = ['tenders.add_tender']

    def get_form_class(self):
        """Расширяет родительский метод, определяет нужно ли поле ИКЗ"""
        ticket_id = self.kwargs['ticket']
        ticket = Ticket.objects.get(id=ticket_id)
        law = ticket.tender_type.law
        self.fields = self.model.get_fields_for_view(law)
        return super().get_form_class()

    def form_valid(self, form):
        """Определяет заявку и сохраняет закупку"""
        ticket_id = self.kwargs['ticket']
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.tender_type.law == 223:
            form.cleaned_data['smp'] = False
        self.object = Tender.objects.create(
            ticket=ticket,
            **form.cleaned_data,
        )
        return HttpResponseRedirect(self.get_success_url())


class TenderUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView
):
    model = Tender
    permission_required = ['tenders.change_tender']
    
    def get_form_class(self):
        """Расширяет родительский метод, определяет нужно ли поле ИКЗ"""
        tender_id = self.kwargs['pk']
        tender = Tender.objects.get(id=tender_id)
        law = tender.ticket.tender_type.law
        self.fields = self.model.get_fields_for_view(law)
        return super().get_form_class()


class TenderDetailView(LoginRequiredMixin, generic.DetailView):
    """Представление для просмотра закупки"""
    model = Tender


class TenderDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView
):
    """Представление для удаления закупки"""
    model = Tender
    permission_required = ['tenders.delete_tender']
    success_url = reverse_lazy('tickets:reestr')
