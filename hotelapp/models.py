from django.db import models
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# from authentications.models import CustomUser
from random import random
import random
import math
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    description = models.TextField()
    images = models.ImageField(upload_to='hotel_images', null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'hotelapp'


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    images = models.ImageField(upload_to='room_images', null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        app_label = 'hotelapp'

class Room(models.Model):
    name = models.CharField(max_length=100, default = 'room name')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, default=1)
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    images = models.ImageField(upload_to='room_images', null=True, blank=True)
    description = models.TextField(max_length=10000, null=True)
    
    class Meta:
            app_label = 'hotelapp'
   
    def __str__(self):
        return f"{self.name}- Room type {self.room_type.name} - Room {self.room_number} - Available {self.is_available}"
    
    
    def is_available_between_dates(self, check_in, check_out):
        bookings = Booking.objects.filter(
            room_type__room=self,
            check_in__lte=check_out,
            check_out__gte=check_in
        )
        return not bookings.exists()

    
    @classmethod
    def find_available_room(cls, hotel, room_type, check_in, check_out, initial_room=None):
        """
        Find an available room of the given room_type in the specified hotel for the specified dates.
        If initial_room is provided and not available, find another available room within the same room type.
        """
        rooms = cls.objects.filter(hotel=hotel, room_type=room_type, is_available=True)
        
        if initial_room and not initial_room.is_available_between_dates(check_in, check_out):
            rooms = rooms.exclude(id=initial_room.id)
        
        for room in rooms:
            if room.is_available_between_dates(check_in, check_out):
                return room
        
        return None

        

class Availability(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booked_rooms = models.ManyToManyField(Room)  # Many-to-many relationship with Room model
    
    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} - Room Type {self.room_type.name}"
    
    class Meta:
            app_label = 'hotelapp'
            
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=1)
    # availability = models.ForeignKey(Availability, on_delete=models.DO_NOTHING, null=True, blank=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False) 
    
    # Fields to store availability data
    availability_hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='booking_availability', default=1)
    availability_room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='booking_availability', default=1)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} - Room Type: {self.room_type.name} -  Room Name: {self.room.name} - Check In: {self.check_in} - Check Out: {self.check_out}" 
    class Meta:
            app_label = 'hotelapp'

    # def __str__(self):
    #     return f"{self.user.username} - {self.hotel.name} - Room {self.availability.room.room_number}" 
class BookingItem(models.Model):
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='booking_items', default=1)
    
    def __str__(self):
        booked_room_names = ', '.join(room.name for room in self.availability.booked_rooms.all())
        return f"User - {self.availability.user.username} Hotel - {self.availability.hotel.name} - Room Type: {self.availability.room_type.name} - Room Names: {booked_room_names} - Check In: {self.availability.check_in} - Check Out: {self.availability.check_out}" 
    
    class Meta:
            app_label = 'hotelapp'
            
@receiver(post_save, sender=Availability)
def auto_save_bookingitem(instance, created, sender, **kwargs):
    if created:
        booking, created = BookingItem.objects.get_or_create(
         availability=instance  
          
        )
        booking.save()
    
class Review(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    rating = models.PositiveIntegerField()
    review_text = models.TextField()
    images = models.ImageField(upload_to='review_image', null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, default=1)
    review_date = models.DateTimeField(default=timezone.now)
    
    def update_rating(self):
        initiate_rating = 0
        self.rating +=initiate_rating
        return initiate_rating

    def __str__(self):
        return f"Usher: {self.booking.user.first_name} -Hotel: {self.hotel.name} -Roomtype: {self.booking.room_type.name} -Rating: {self.rating}"
    class Meta:
        ordering =['rating']
        app_label = 'hotelapp'
# @receiver(pre_save, sender =Review)
# def update_rating_field(sender, instance, created, **kwargs):
#     if created:
#         new_rating = 0
#         instance.rating +=new_rating
        
class Homeimages(models.Model):
    title = models.CharField(max_length=200)
    description= models.TextField(max_length =10000)
    images = models.ImageField(upload_to='home_images', null=True, blank=True)
    class Meta:
            app_label = 'hotelapp'
            
class Zumalogo(models.Model):
    name= models.CharField(max_length=200)
    logo= models.ImageField(upload_to='zuma-logo', null=True, blank=True)
    
    class Meta:
            app_label = 'hotelapp'
            
class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    charge_id = models.CharField(max_length=100, null = True)
    status = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add=True, null = True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null = True, blank =True)
    
    class Meta:
            app_label = 'hotelapp'
            ordering = ('-timestamp',)
            
    def __str__(self):
        user_info = f"User: {self.booking.user}" if self.booking else "User: None"
        return (
            f"Payment {self.pk} - {user_info} - Amount: {self.amount}"
            f" - Status: {self.status} - Room Type: {self.room_type}"
            f" - Room Name: {self.room} - Room No: {self.room.room_number}"
        )

    # def __str__(self):
    #     return f"Payment {self.pk} - User: {self.booking.user} - Amount: {self.amount}- Status: {self.status} - Room Type: {self.room_type} - Room Name: {self.room} - Room No: {self.room.room_number}"

@receiver(post_save, sender = Booking)
def auto_save_payment(sender, instance, created, **kwargs):
    if created:
        get_days = (instance.check_out - instance.check_in).days
        total_amount = get_days * instance.total_price
        
        pay, created = Payment.objects.get_or_create(
            user =instance.user,
            amount = total_amount,
            charge_id=random.randint(1000000, 9999999),
            status=True,
            room=instance.room,  # Assign the specific room instance
            room_type =instance.room_type,
            booking=instance,
            )
        pay.save()
