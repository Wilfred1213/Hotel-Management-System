from django.db import models
from django.contrib.auth.models import User

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    description = models.TextField()
    images = models.ImageField(upload_to='hotel_images', null=True, blank=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=10000)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    images = models.ImageField(upload_to='room_images', null=True, blank=True)

    def __str__(self):
        return self.name
    

class Room(models.Model):
    name = models.CharField(max_length=100, default = 'room name')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, default=1)
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    images = models.ImageField(upload_to='room_images', null=True, blank=True)
    description = models.TextField(max_length=10000, null=True)
    

    def __str__(self):
        return f"{self.name} - Room {self.room_number} - Available {self.is_available}"
    
    def is_available_between_dates(self, check_in, check_out):
        bookings = Booking.objects.filter(
            room=self,
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        return not bookings.exists()


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
   

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} - Room {self.room.room_number}"
    
class BookedRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    
    # def save(self, *args, **kwargs):
    #     self.num_of_days = (self.booking.check_out - self.booking.check_in).days
    #     self.total_price = self.num_of_days * self.room.price
    #     super(BookedRoom, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.booking.room} - Room {self.room.room_number}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, default=1)
    rating = models.PositiveIntegerField()
    review_text = models.TextField()
    images = models.ImageField(upload_to='review_image', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"

class Homeimages(models.Model):
    title = models.CharField(max_length=200)
    description= models.TextField(max_length =10000)
    images = models.ImageField(upload_to='home_images', null=True, blank=True)
    
class Zumalogo(models.Model):
    name= models.CharField(max_length=200)
    logo= models.ImageField(upload_to='zuma-logo', null=True, blank=True)
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    charge_id = models.CharField(max_length=100)
    status = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    

    def __str__(self):
        return f"Payment {self.pk} - User: {self.user.username}, Amount: {self.amount}, Status: {self.status}"

    