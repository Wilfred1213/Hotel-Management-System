import math
from random import random
from django.shortcuts import render, redirect, reverse
from hotel.models import RoomType, Zumalogo,Booking, Room, BookedRoom, Payment
from django.contrib import messages
from hotel.forms import BookingForm
from django.db.models import Q
import paystack
import paystackapi
from datetime import datetime
from . import env

from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests

from django.utils import timezone


# Create your views here.
def home(request):
    type_of_room = RoomType.objects.all()
    logo = Zumalogo.objects.first()
    context ={
        'roomtypes':type_of_room,
        'logos':logo
    }
    return render(request, 'hotel/home.html', context)

def all_categories(request, roomtype_id):
    room = Room.objects.get(id=roomtype_id)
    type_of_rooms = RoomType.objects.get(id=room.id)
    get_all_room_category = type_of_rooms.room_set.all()
    
    context = {
        
        'category':get_all_room_category,
        
    }
    
    return render(request, 'hotel/all_categories.html', context)


def room_availability(request, roomtype_id):
    room = Room.objects.get(id=roomtype_id)
    type_of_rooms = RoomType.objects.get(id=room.id)
    get_all_room_category = type_of_rooms.room_set.all()
    rooms = Room.objects.filter(room_type=type_of_rooms, is_available=True)
    room_field = Room.objects.filter(room_type=type_of_rooms)


    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # room = form.cleaned_data['room']
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            existing_booking = Booking.objects.filter(
                Q(room=room) &
                (Q(check_in__range=(check_in, check_out)) | Q(check_out__range=(check_in, check_out)))
            )
            if existing_booking.exists():
                messages.info(request, 'Sorry! This is already booke within the range of your check in and check out. Try another date')
                return redirect('room_availability', roomtype_id = roomtype_id)
            else:
                messages.info(request, 'The room is available, you can proceed to book it')
                return redirect('booking_room', roomtype_id=roomtype_id )
                
    else:
        form = BookingForm()
        # form.fields['room'].queryset = room_field

    context = {
        'form': form,
        'room_type': room,
        'room': rooms,
        'rooms':room,
        'category':get_all_room_category,
        'available':type_of_rooms
    }
    
    return render(request, 'hotel/availability.html', context)




def booking_room(request, roomtype_id):
    room = Room.objects.get(id=roomtype_id)
    type_of_rooms = RoomType.objects.get(id=room.id)
    get_all_room_category = type_of_rooms.room_set.all()
    rooms = Room.objects.filter(room_type=type_of_rooms, is_available=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            

            existing_booking = Booking.objects.filter(
                Q(room=room) &
                (Q(check_in__range=(check_in, check_out)) | Q(check_out__range=(check_in, check_out)))
            )
            if existing_booking.exists():
                # return render(request, 'hotel/error_page.html')# messages.error(request, 'Sorry, the room is already booked for the specified dates.')
                return redirect('available_rooms', room_id=room.room_type_id)
            else:
                booking = Booking.objects.create(
                    user=request.user,
                    hotel=room.hotel,
                    room=room,
                    room_type=type_of_rooms,
                    check_in=check_in,
                    check_out=check_out,
                    total_price=type_of_rooms.price
                )
                room.is_available = False
                room.save()
                BookedRoom.objects.create(user =request.user, booking=booking, room =room, total_price = room.price)

                messages.info(request, 'Your room is available. Proceed with payment.')
                return redirect('booked_room')
                
    else:
        form = BookingForm()
        # form.fields['room'].queryset = room_field

    context = {
        'form': form,
        'room_type': room,
        'room': rooms,
        'rooms':room,
        'category':get_all_room_category,
    }
    
    return render(request, 'hotel/booking_page.html', context)

def available_rooms(request, room_id):
    room = Room.objects.get(id=room_id)
    available_room = Room.objects.filter(room_type=room.room_type, is_available=True)
    
    context = {
        'availability':available_room,
    }
    return render(request, 'hotel/error_page.html', context)

def booked_room(request):
    user = request.user
    room_booked = Booking.objects.filter(user=user)

    total_amount = 0
    room_ids = [room.room.id for room in room_booked]
    for room in room_booked:
        check_in = room.check_in
        check_out = room.check_out
        num_of_days = (check_out - check_in).days
        total_amount += num_of_days * room.total_price  # Add the current room's total amount to the overall total

        room.num_of_days = num_of_days
        room.total_amount = total_amount

    context = {
        'booked': room_booked,
        'total': total_amount,  # Use the total_amount calculated in the loop
    }

    return render(request, 'hotel/success_page.html', context)



def cancel_order(request, booked_id):
    cancel = Booking.objects.get(id = booked_id)
    cancel.delete()

    messages.info(request, f'You cancel {cancel.room.name} order')
    return redirect('booked_room')


