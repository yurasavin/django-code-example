from django.urls import include, path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.TicketHomeView.as_view(), name='home'),
    path('reestr/', include([
        path('', views.TicketsListView.as_view(), name='reestr'),
        path('<int:year>/', views.TicketsListView.as_view(), name='reestr_by_year'),
        path('my/', views.WorkerCurrentTicketsListView.as_view(), name='my_current_tickets'),
        path('my/<int:worker>', views.WorkerCurrentTicketsListView.as_view(), name='worker_current_tickets'),
    ])),
    path('ticket/', include([
        path('create/', views.TicketCreate.as_view(), name='ticket_create'),
        path('<pk>/update/', views.TicketUpdate.as_view(), name='ticket_update'),
        path('<pk>/delete/', views.TicketDelete.as_view(), name='ticket_delete'),
    ])),
]
