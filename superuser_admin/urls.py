from django.urls import path
from . import views

urlpatterns = [
    path('', views.superuser_login, name='superuser_login'),
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('add-admin/', views.add_admin, name='add_admin'),
    path('manage-admins/', views.admin_manage, name='admin_manage'),
    path('logout/', views.superuser_logout, name='superuser_logout'),
]
