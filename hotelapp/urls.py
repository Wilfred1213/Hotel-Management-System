from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.home, name ='home'),
    path('booking_room/<int:roomtype_id>/', views.booking_room, name ='booking_room'),
    path('available_rooms/<int:room_id>/', views.available_rooms, name ='available_rooms'),
    path('booked_room/', views.booked_room, name ='booked_room'),
    path('room_availability/<int:roomtype_id>/', views.room_availability, name ='room_availability'),
    path('all_categories/<int:roomtype_id>/', views.all_categories, name ='all_categories'),
    path('cancel_order/<int:booked_id>/', views.cancel_order, name ='cancel_order'),
    path('paydetail/<int:room_id>/', views.paydetail, name='paydetail'),
    path('payment/<int:availability_id>/', views.payment, name='payment'),
    path('payindividually/', views.payindividually, name='payindividually'),
    path('review_room/<int:booking_id>/', views.review_room, name='review_room'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    
]