from django.urls import path

from . import views

app_name = 'tenders'

urlpatterns = [
    path('<ticket>/create/', views.TenderCreateView.as_view(), name='tender_create'),
    path('<pk>/', views.TenderDetailView.as_view(), name='tender_detail'),
    path('<pk>/update/', views.TenderUpdateView.as_view(), name='tender_update'),
    path('<pk>/delete/', views.TenderDeleteView.as_view(), name='tender_delete'),
]
