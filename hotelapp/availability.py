from hotelapp.models import Availability,Room, Booking
from django.db.models import Q
import datetime


# def is_room_available(room, check_in, check_out):
#     # Check if the room is available for the specified date range
#     existing_booking = Availability.objects.filter(
#         Q(room=room) &
#         (Q(check_in__range=(check_in, check_out)) | Q(check_out__range=(check_in, check_out)))
#     )
#     if existing_booking.exists():
#         return False, None  # Room is not available for the specified date range
#     else:
#         return True, room  # Room is available for the specified date range

# def get_alternative_room(room, check_in, check_out):
#     # Find an alternative available room of the same type
#     room_type = room.room_type
#     available_rooms = Room.objects.filter(room_type=room_type, is_available=True)
#     for available_room in available_rooms:
#         if is_room_available(available_room, check_in, check_out)[0]:
#             return available_room
#     return None  # No alternative room available

# # def check_availability(room, check_in, check_out):
# #     avail_room =[]
# #     booking_list = Availability.objects.filter(room=room)
# #     for booking in booking_list:
# #         if booking.check_in > check_out or booking.check_out < check_in:
# #             avail_room.append(True)
# #         avail_room.append(False)
# #     return all(avail_room)
    
# def check_availability(room, check_in, check_out):
#     booking_list = Availability.objects.filter(room=room)
#     for booking in booking_list:
#         if not (booking.check_out < check_in or booking.check_in > check_out):
#             return False
#         return True
    


# def find_available_room(room_type, check_in, check_out):
#     available_rooms = Room.objects.filter(room_type=room_type, is_available=True)
#     for room in available_rooms:
#         if room.is_available_between_dates(check_in, check_out):
#             return room
#     return None


# Define these functions in your views.py or a utility module

def is_room_available(room, check_in, check_out):
    
    conflicting_bookings = Booking.objects.filter(
        room=room,
        check_in__lt=check_out,
        check_out__gt=check_in
    )
    return not conflicting_bookings.exists()

def find_available_room(hotel, room_type, check_in, check_out):
    """
    Find an available room of the given room_type in the specified hotel for the specified dates.
    """
    rooms = Room.objects.filter(hotel=hotel, room_type=room_type)
    for room in rooms:
        if is_room_available(room, check_in, check_out):
            return room
    return None
