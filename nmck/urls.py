from django.urls import path

from . import views

app_name = 'nmck'

urlpatterns = [
    path('create/', views.CreateNmckView.as_view(), name='create'),
]
