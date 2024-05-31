from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name = 'register'),
    path('predict/', views.predict, name='predict'),
    path('contact/', views.contact, name = 'contact'),
]