from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail', views.detail, name='detail'),
    path('record', views.record, name='record'),
    path('callback', views.callback, name='callback'),
]

