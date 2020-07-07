import datetime

from django.urls import path

from . import views

app_name = 'worker'

# текущий год для показа закупок на текущий год
CURRENT_YEAR = datetime.datetime.today().year

urlpatterns = [
    path('user_tickets/<pk>/', views.UserTicketsDetailView.as_view(), name='user_tickets'),
    path('rules/', views.rules, name='rules'),
]
