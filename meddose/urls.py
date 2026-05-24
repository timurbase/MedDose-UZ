"""
URL configuration for meddose project
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')),
    # Favicon 404 ni oldini olish
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# Custom error handlers
handler404 = 'calculator.views.handler404'
handler500 = 'calculator.views.handler500'
