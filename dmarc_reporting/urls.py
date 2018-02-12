"""django-dmarc-reporting urls"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'dmarc_reporting'
urlpatterns = [
    path('', views.domains_list, name='domains_list'),
    path('domains/', views.domains_list, name='domains_list'),
    path('feedbackreports/<int:domain_pk>', views.feedback_reports, name="feedback_reports"),
    path('login/', auth_views.LoginView.as_view(template_name='dmarc_reporting/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': 'dmarc_reporting:login'}, name='logout'),
]
