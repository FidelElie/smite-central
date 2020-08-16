from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="central"),
    path('privacy/', views.privacy, name="privacy"),
]
