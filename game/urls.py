from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('<int:creator_id>/<int:game_id>/create-manage/', views.create_manage, name='create_manage'),
    path('<int:creator_id>/<int:pk>/monitor/', views.monitor, name='monitor'),
    path('<int:creator_id>/<int:game_id>/results/', views.results, name='results'),
]
