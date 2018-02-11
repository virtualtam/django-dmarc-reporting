"""django-dmarc-reporting urls"""
from django.urls import path

from . import views

app_name = 'dmarc_reporting'
urlpatterns = [
    path('', views.domains_list, name='domains_list'),
]
