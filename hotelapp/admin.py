from django.contrib import admin
from hotelapp.models import Room, RoomType,BookingItem,Review, Availability, Homeimages,Payment, Hotel, Booking,  Zumalogo
# Register your models here.
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(Hotel)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Homeimages)
admin.site.register(Zumalogo)
admin.site.register(Availability)
admin.site.register(Payment)
admin.site.register(BookingItem)