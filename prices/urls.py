from django.urls import include, path

from . import views

app_name = 'prices'

urlpatterns = [
    path('start_price/', include([
        path('<tender>/create/', views.StartPriceCreateView.as_view(), name='startprice_create'),
        path('<tender>/<price>/copy/', views.StartPriceCopyView.as_view(), name='startprice_copy'),
        path('<tender>/<pk>/delete/', views.StartPriceDeleteView.as_view(), name='startprice_delete'),
        path('<price>/update/', views.StartPriceUpdateView.as_view(), name='startprice_update'),
    ])),
    path('contract_price/', include([
        path('<contract>/create/', views.ContractPriceCreateView.as_view(), name='contractprice_create'),
        path('<contract>/<pk>/copy/', views.ContractPriceCopyView.as_view(), name='contractprice_copy'),
        path('<contract>/<pk>/delete/', views.ContractPriceDeleteView.as_view(), name='contractprice_delete'),
        path('<pk>/update/', views.ContractPriceUpdateView.as_view(), name='contractprice_update'),
    ])),
    path('contract_price_change/', include([
        path('<contract>/<pk>/delete', views.ContractPriceChangeDeleteView.as_view(), name='contract_price_change_delete'),
        path('<pk>/update', views.ContractPriceChangeUpdateView.as_view(), name='contract_price_change_update'),
    ])),
]
