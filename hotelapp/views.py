import math
from random import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from hotelapp.models import RoomType, Zumalogo, Review,BookingItem, Booking, Room, Payment, Availability
from django.contrib import messages
from hotelapp.forms import BookingForm, ReviewForm
from django.db.models import Q
from datetime import datetime

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests
import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from hotelapp.availability import is_room_available,find_available_room

from django.db.models import Avg


# Create your views here.
def home(request):
    reviews= Review.objects.all()
    type_of_room = RoomType.objects.all()
    logo = Zumalogo.objects.first()
    
    roomtypes = RoomType.objects.annotate(avg_rating=Avg('booking__review__rating')).order_by('-avg_rating')
   
    highest_avg_rating = 0  # Initialize with a low value
    trending_room_type=None
    for roomtype in roomtypes:
        if roomtype.avg_rating is not None and roomtype.avg_rating > highest_avg_rating:
            highest_avg_rating = roomtype.avg_rating
            trending_room_type = roomtype
    
    context ={
        'trending_room_type': trending_room_type,
        'roomtypes':type_of_room,
        'logos':logo,
        'reviews':reviews,
    }
    return render(request, 'hotelapp/home.html', context)

def all_categories(request, roomtype_id):
    room = Room.objects.get(id=roomtype_id)
    type_of_rooms = RoomType.objects.get(id=room.id)
    get_all_room_category = type_of_rooms.room_set.all()
    
    context = {
        
        'category':get_all_room_category,
        
    }
    
    return render(request, 'hotelapp/all_categories.html', context)


def room_availability(request, roomtype_id):
    room =None
    type_of_rooms=None
    try:
        room = Room.objects.get(id=roomtype_id)
        type_of_rooms = RoomType.objects.get(id=room.id)
    except RoomType.DoesNotExist and Room.DoesNotExist:
        messages.info(request, 'No room added yet to this category')
       
    # get_all_room_category = type_of_rooms.room_set.all()
    rooms = Room.objects.filter(room_type=type_of_rooms, is_available=True)#.exclude(
                #booking__check_out__gte=check_in,  # Exclude booked rooms for check_out date >= check_in date
               # booking__check_in__lte=check_out,   # Exclude booked rooms for check_in date <= check_out date
           # )
    # room_field = Room.objects.filter(room_type=type_of_rooms)
    
    type_of_room = RoomType.objects.all()
    logo = Zumalogo.objects.first()
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            existing_booking = Booking.objects.filter(
                Q(room__in=rooms) &
                (Q(check_in__range=(check_in, check_out)) | Q(check_out__range=(check_in, check_out)))
            )
            if existing_booking.exists():
                messages.info(request, 'Sorry! This is already booke within the range of your check in and check out. Try another date')
                return redirect('room_availability', roomtype_id = roomtype_id)
            else:
               
                messages.info(request, 'Your room is available. Proceed with payment.')
                return redirect('booking_room', roomtype_id=roomtype_id )
                
    else:
        form = BookingForm()
      

    context = {
        'form': form,
        'room_type': room,
        'room': rooms,
        'rooms':room,
        # 'category':get_all_room_category,
        'type_of_rooms':type_of_rooms,
        'roomtypes':type_of_room,
        'logos':logo
    }
    
    return render(request, 'hotelapp/availability.html', context)


@login_required(login_url ='authentications:loggin')
def booking_room(request, roomtype_id):
    logo = Zumalogo.objects.first()
    room_type = RoomType.objects.get(id=roomtype_id)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

    if not rooms.exists():
        messages.error(request, 'No rooms are available for booking. Please choose different dates.')
        return redirect('available_rooms', roomtype_id=room_type.id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            existing_booking = Availability.objects.filter(
                room_type=room_type,
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            for room in rooms:
                if is_room_available(room =room, check_in=check_in, check_out=check_out):
                    booked_room_numbers = set()
                    for booking in existing_booking:
                        booked_room_numbers.update(room.room_number for room in booking.booked_rooms.all())
                                
                    available_rooms = rooms.exclude(room_number__in=booked_room_numbers)
                    if available_rooms.exists():
                        available_room = available_rooms.first()
                        booking = Availability.objects.create(
                            user=request.user,
                            hotel=available_room.hotel,
                            room_type=room_type,
                            check_in=check_in,
                            check_out=check_out,
                            total_price=room_type.price
                        )
                        booking.booked_rooms.add(available_room)

                        messages.info(request, 'An available room has been booked for you. Proceed with payment.')
                        return redirect('payindividually')
                    else:
                        messages.error(request, 'No rooms are available for booking.')
                        return redirect('available_rooms', roomtype_id=room_type.id)
                else:
                    messages.info(request, 'Room is booked within the date you choose. Select another date please!')
                    return redirect('booking_room', roomtype_id=room_type.id)

    else:
        form = BookingForm()

    context = {
        'form': form,
        'room_type': room_type,
        'room': rooms,
        'category': room_type.room_set.all(),
        'type_of_rooms': room_type,
        'logos': logo,
    }

    return render(request, 'hotelapp/booking_page.html', context)



def available_rooms(request, room_id):
    room = Room.objects.get(id=room_id)
    available_room = Room.objects.filter(room_type=room.room_type, is_available=True)
    
    context = {
        'availability':available_room,
    }
    return render(request, 'hotelapp/error_page.html', context)

@login_required(login_url='authentications:loggin')
def payindividually(request):
    user = request.user
    
    all_booked_rooms = Availability.objects.filter(user =user)
    type_of_room = RoomType.objects.all()
    logo = Zumalogo.objects.first()
    bookings = Booking.objects.filter(user=user)
    
    get_first_item_that_meet_the_criteria = all_booked_rooms.first()
    
    booking_items = BookingItem.objects.filter(availability__in=all_booked_rooms)
    
    total_price=None
    for book in all_booked_rooms:
        checkin = book.check_in
        checkout = book.check_out
        number_of_days = (checkout - checkin).days
        total_price = book.room_type.price * number_of_days
        
        book.number_of_days = number_of_days
        book.total_price = total_price
        
    for booking_item in booking_items:
        checkin = booking_item.availability.check_in
        checkout = booking_item.availability.check_out
        number_of_days = (checkout - checkin).days
        booking_item.number_of_days = number_of_days
        
    context = {
        'all_booked_rooms':all_booked_rooms,
        'logos':logo, 
        'roomtypes':type_of_room,
        'total': total_price,
        'bookings':bookings,
        'items':booking_items,
        'days':number_of_days
    }
    return render(request, 'hotelapp/all_booked.html', context)

@login_required(login_url='authentications:loggin')
def paydetail(request, room_id):
    type_of_room = RoomType.objects.all()
    logo = Zumalogo.objects.first()
        
    details = Availability.objects.get(id=room_id)
    # booking = Booking.objects.get(payment__charge_id = details)
    
    
    checkin = details.check_in
    checkout = details.check_out
    number_of_days = (checkout - checkin).days
    total_price = details.room_type.price * number_of_days
        
    context = {
        'room':details,
        'number_of_days':number_of_days, 
        'roomtypes':type_of_room,
        'logos':logo, 
        'total_price':total_price,
        # 'booking':booking     
    }
    return render(request, 'hotelapp/book_detail.html', context)
    
@login_required(login_url='authentications:loggin')    
def booked_room(request):
    user = request.user
    room_booked = Availability.objects.filter(user=user)
    

    total_amount = 0
    # room_ids = [room.room.id for room in room_booked]
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

    return render(request, 'hotelapp/success_page.html', context)



def cancel_order(request, booked_id):
    try:
        cancel = BookingItem.objects.get(id=booked_id)
    except Availability.DoesNotExist:
        messages.error(request, 'Invalid booking ID. Please try again.')
        return redirect('payindividually')

    # Save the room and room type details before deleting the object
    room_type = cancel.availability.hotel
    cancel.delete()
    messages.info(request, f'You canceled the booking for {room_type}')
    return redirect('payindividually')

@login_required(login_url='authentications:loggin')
def payment(request, availability_id):
    # try:
    user = request.user
    availability = Availability.objects.get(id=availability_id)
    booked_item = BookingItem.objects.get(availability=availability)
    
    # Find the initially booked rooms queryset
    original_booked_rooms = availability.booked_rooms.all()

    # Create an empty list to store available rooms
    available_rooms = []

    # Check if each originally booked room is available, and if not, find an available room
    for original_room in original_booked_rooms:
        if not original_room.is_available_between_dates(availability.check_in, 
                                                        availability.check_out):
            
            available_room = find_available_room(availability.hotel, 
                                                    availability.room_type, 
                                                    availability.check_in, 
                                                    availability.check_out)
            if available_room:
                available_rooms.append(available_room)
        else:
            available_rooms.append(original_room)

    # Create bookings for the user with the assigned rooms
    if available_rooms:
        for available_room in available_rooms:
            booking = Booking.objects.create(
                user=request.user,
                hotel=availability.hotel,
                room=available_room,
                room_type=availability.room_type,
                check_in=availability.check_in,
                check_out=availability.check_out,
                total_price=availability.total_price,
                is_paid=True,
                availability_hotel=availability.hotel,
                availability_room_type=availability.room_type
            )
        if booking:
                try:
                    # Delete the BookingItem after successful booking creation
                    booked_item.delete()
                    messages.info(request, 'You successfully paid')
                    return redirect('home')
                except Exception as e:
                    messages.error(request, f'Error deleting BookingItem: {str(e)}')
                    return redirect('home')
        
    else:
        messages.error(request, 'No available rooms. Booking could not be created.')
        return redirect('home')


def review_room(request, booking_id):
    booking = Booking.objects.get(id = booking_id)
    
    if request.method =='POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            rating_add = form.cleaned_data['rating']
            save_review = form.save(commit=False)
            save_review.user = request.user
            save_review.booking = booking
            save_review.update_rating =int(rating_add)
            save_review.save()
            messages.info(request, 'Thank You for rating this room')
            return redirect('home')
        
        else:
            messages.info(request, 'Error occur while saving. Adjust your data')
            return redirect('payindividually')
    form = ReviewForm()
    context = {
        'form': form,
    }
    return render(request, 'hotelapp/review_page.html', context)  

def delete_review(request, review_id):
    delete_id = Review.objects.get(id=review_id)
    delete_id.delete()
    messages.info(request, 'You deleted this review')
    return redirect('home')
        
        