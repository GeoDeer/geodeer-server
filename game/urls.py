from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('main-menu/<int:creator_id>', views.main_menu, name='main_menu'),
    path('create-manage/<int:creator_id>/', views.create_manage, name='create_manage'),
    path('monitor/<int:pk>/<int:creator_id>/', views.monitor, name='monitor'), 
]
