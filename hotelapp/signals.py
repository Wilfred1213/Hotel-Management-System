from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Booking

@receiver(post_save, sender=Booking)
def send_notification_email(sender, instance, created, **kwargs):
    if created: 
        user_info = instance.user
        user_email = user_info.email
        subject = 'Your booking at Zuma Resort'
        message = f'You sucessfully booked a room on Zuma from {instance.check_in} to {instance.check_out}\n\n'
        message += f'Amount Paid: {instance.total_price}\n\n'
        message += f'Room Category: {instance.room_type}'
        # message += f'Booking Id: {instance.room_type}'
        from_email = 'mathiaswilfred7@yahoo.com'
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)
