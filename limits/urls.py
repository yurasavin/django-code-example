"""Урлы для лимитов"""
from django.urls import include, path

from . import views

app_name = 'limits'

urlpatterns = [
    path('limit/', include([
        path('', views.LimitInfo.as_view(), name='limit'),
        path('<int:year>/', views.LimitInfo.as_view(), name='limit_info'),
        path('update/', views.UpdateLimitsFromFile.as_view(), name='update_limits'),  # noqa: E501
    ]))
]
