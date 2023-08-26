from django.urls import path
from . import views

app_name ='authentications'

urlpatterns = [
   
    path('register_user', views.register_user, name ='register_user'),
    path('loggin', views.loggin, name ='loggin'),
    path('logout', views.logout, name ='logout'),
    
]