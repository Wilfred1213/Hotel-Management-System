from django.shortcuts import render, redirect, reverse
from hotel.models import RoomType, Zumalogo,Booking, Room, BookedRoom, Payment
from django.contrib import messages
from hotel.forms import BookingForm
from django.db.models import Q
import paystack
import paystackapi
from datetime import datetime

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

    if request.method == 'POST':
        # Process the form submission and get the payment amount
        amount = total_amount  # Get the actual amount from the booked room

        # Create a Paystack transaction
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'amount': amount * 100,  # Paystack expects amount in kobo (multiply by 100)
            'email': 'user@example.com',  # Replace with the customer's email
            'callback_url': settings.PAYSTACK_CALLBACK_URL,
            'metadata': {
                'room_ids': room_ids,  # Pass the list of room IDs as metadata
            }
        }
        response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)
        data = response.json()

        # Redirect the user to the Paystack payment page
        return redirect(data['data']['authorization_url'])

    return render(request, 'hotel/success_page.html', context)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def paystack_callback(request):
    if request.method == 'POST':
        # Get the payment status and other details from the request data
        payment_status = request.POST.get('status', '')
        amount = request.POST.get('amount', '')
        charge_id = request.POST.get('reference', '')
        user = request.user
        room_id = request.session.get('room_session_{}'.format(user.id)).get('room_id')

        # Find the booking and room associated with this payment
        booking = Booking.objects.get(id=room_id)
        room = booking.room

        if payment_status == 'success':
            # Payment was successful, save the payment details to the Payment model
            payment = Payment.objects.create(
                user=user,
                amount=amount,
                charge_id=charge_id,
                status=True,
                room=room,
            )

            # Mark the booking as paid and update room availability
            booking.is_paid = True
            booking.save()
            room.is_available = False
            room.save()

            # Redirect to the home page or a success page
            return redirect('home')
        else:
            # Payment was not successful, handle the error scenario as needed
            # You can redirect to an error page or display an error message
            return redirect('error')  # Replace 'error' with the name/url of your error page view
    else:
        # Handle cases where the callback is not a POST request
        return HttpResponse(status=400)  # Return a 400 Bad Request response



def cancel_order(request, booked_id):
    cancel = Booking.objects.get(id = booked_id)
    cancel.delete()

    messages.info(request, f'You cancel {cancel.room.name} order')
    return redirect('booked_room')


def create_payment_intent(request, room_id):
    room = Room.objects.get(id = room_id)
    room.is_available = False
    room.save()
    messages.info(request, 'Payment made successful')
    return redirect('booked_room')


