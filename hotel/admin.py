from django.contrib import admin
from hotel.models import Room, RoomType, Homeimages,Payment, Hotel, Booking, Review, Zumalogo, BookedRoom

# Register your models here.
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(Hotel)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Homeimages)
admin.site.register(Zumalogo)
admin.site.register(BookedRoom)
admin.site.register(Payment)