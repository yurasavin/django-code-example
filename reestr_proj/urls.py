"""reestr_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from functools import partial
from django.views import defaults

from worker.views import CustomLoginView

handler403 = partial(defaults.permission_denied, template_name='main/403.html')
handler404 = partial(defaults.page_not_found, template_name='main/404.html')
handler500 = partial(defaults.server_error, template_name='main/500.html')

urlpatterns = [
    path('staff_only/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('ktru/', include('ktru.urls')),
    path('limits/', include('limits.urls')),
    path('', include('tickets.urls')),
    path('tenders/', include('tenders.urls')),
    path('contracts/', include('contracts.urls')),
    path('prices/', include('prices.urls')),
    path('reports/', include('reports.urls')),
    path('docx-maker/', include('make_docs.urls')),
    path('worker/', include('worker.urls')),
    path('nmck/', include('nmck.urls')),
    path('drugs/', include('drugs.urls')),
    path('metrics/', include('metrics.urls')),
    path('audit/', include('audit.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('silk/', include('silk.urls', namespace='silk')),
    ] + urlpatterns
