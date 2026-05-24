from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.index, name='index'),
    path('calculate/', views.calculate, name='calculate'),
    path('history/', views.history, name='history'),
    path('about/', views.about, name='about'),
    path('history/clear/', views.clear_history, name='clear_history'),
]
