from django.urls import include, path

from . import views

app_name = 'contracts'

urlpatterns = [
    path('<ticket>/create/', views.ContractCreateView.as_view(), name='contract_create'),
    path('<pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('<pk>/update/', views.ContractUpdateView.as_view(), name='contract_update'),
    path('<pk>/delete/', views.ContarctDeleteView.as_view(), name='contract_delete'),
    path('<pk>/contract_for_buh/', views.ContractForBuhView.as_view(), name='contract_for_buh'),
    path('contract_change/', include([
        path('<contract>/', views.ContractChangeCreateView.as_view(), name='create_contract_change'),
        path('<pk>/update/', views.ContractChangeUpdateView.as_view(), name='contract_change_update'),
        path('<contract>/<pk>/delete/', views.ContractChangeDeleteView.as_view(), name='contract_change_delete'),
    ])),
]
