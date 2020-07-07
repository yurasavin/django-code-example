from typing import Optional

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views import generic

from tickets.models import Ticket

from core.tasks import send_message_to_telegram

from .models import Worker


@login_required
def rules(request):
    return render(request, 'tenders/rules.html')


class UserTicketsDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    template_name = 'tenders/user_tickets.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tickets = Ticket.objects.filter(worker=self.object.id)
        context['tickets'] = tickets
        return context


class CustomLoginView(LoginView):
    """
    Добавляет уведомление о входе в стандартную вьюшку
    """

    def get(self, request, *args, **kwargs):
        """
        Если пользователь уже залогинен, перекидывает его на главную страницу
        """
        if request.user.is_authenticated:
            return redirect('tickets:home')
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        """Вызывает отправку уведомление о попытке входа"""
        password = form.cleaned_data['password']
        username = form.cleaned_data['username']
        ip = self.request.headers.get('cf-connecting-ip')
        country = self.request.headers.get('cf-ipcountry')
        self.send_login_notification(
            username=username,
            ip=ip,
            password=password,
            country=country,
            success=False,
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        """Вызывает отправку уведомление об успешном входе"""
        username = form.cleaned_data['username']
        ip = self.request.headers.get('cf-connecting-ip')
        self.send_login_notification(username=username, ip=ip)
        return super().form_valid(form)

    def send_login_notification(
            self,
            username: str,
            ip: str,
            password: Optional[str] = None,
            country: Optional[str] = None,
            success: bool = True):
        """Отправляет в бот нотификацию при логине пользователя"""
        if success:
            message = (
                f'Выполнен вход пользователем <b>{username}</b>\n'
                f'IP: <b>{ip}</b>'
            )
        else:
            message = (
                f'Попытка входа под пользователем <b>{username}</b>\n'
                f'Пароль: <b>{password}</b>\n'
                f'Страна: <b>{country}</b>\n'
                f'IP: <b>{ip}</b>'
            )
        send_message_to_telegram.delay(message)
