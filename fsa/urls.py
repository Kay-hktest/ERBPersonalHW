from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_summary, name='activity_summary'),
]