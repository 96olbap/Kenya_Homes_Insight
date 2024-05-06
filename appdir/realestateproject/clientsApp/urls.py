from django.conf import settings
from django.urls import path, include
from . import views as client_views


urlpatterns = [
    path('', client_views.homepage, name='homepage'),
    path('signup/', client_views.signup, name='signup'),
    path('profiles/<int:pk>/', client_views.ProfileDetailView.as_view(), name='profile'),
    path('profiles/<int:pk>/update', client_views.ProfileUpdateView.as_view(), name='profileUpdate'),
]