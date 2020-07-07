"""Урлы для лимитов"""
from django.urls import include, path

from . import views

app_name = 'limits'

urlpatterns = [
    path('limit/', include([
        path('', views.LimitInfo.as_view(), name='limit'),
        path('<int:year>/', views.LimitInfo.as_view(), name='limit_info'),
        path('update/', views.UpdateLimitsFromFile.as_view(), name='update_limits'),  # noqa: E501
    ])),
    path('source/', include([
        path('<pk>/used/', views.SourceUsedInfo.as_view(), name='source_info_used'),  # noqa: E501
        path('<pk>/in_use/', views.SourceInUseInfo.as_view(), name='source_info_in_use'),  # noqa: E501
    ])),
    path('subdivision/', include([
        path('<pk>/used/', views.SubdivisionUsedInfo.as_view(), name='subdivision_info_used'),  # noqa: E501
        path('<pk>/in_use/', views.SubdivisionInUseInfo.as_view(), name='subdivision_info_in_use'),  # noqa: E501
    ])),
    path('article/', include([
        path('<pk>/used/', views.ArticleUsedInfo.as_view(), name='article_info_used'),  # noqa: E501
        path('<pk>/in_use/', views.ArticleInUseInfo.as_view(), name='article_info_in_use'),  # noqa: E501
    ])),
    path('limit_money/', include([
        path('<pk>/used/', views.LimitMoneyUsedInfo.as_view(), name='money_info_used'),  # noqa: E501
        path('<pk>/in_use/', views.LimitMoneyInUseInfo.as_view(), name='money_info_in_use'),  # noqa: E501
    ])),
    path('debt/', include([
        path('', views.DebtInfoView.as_view(), name='debt'),
        path('<int:year>/create/', views.DebtCreateView.as_view(), name='debt_create'),  # noqa: E501
        path('<int:pk>/change/', views.DebtUpdateView.as_view(), name='debt_update'),  # noqa: E501
        path('<int:pk>/delete/', views.DebtDeleteView.as_view(), name='debt_delete'),  # noqa: E501
        path('<int:year>/', views.DebtInfoView.as_view(), name='debt_info'),
    ])),
]
