from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('monitor/<int:pk>/', views.monitor, name='monitor'),   
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]
