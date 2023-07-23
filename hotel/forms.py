from django import forms
from hotel.models import Booking, Room, RoomType, Hotel
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class MyDateInput(forms.widgets.DateInput):
    input_type = 'date'

class BookingForm(forms.Form):
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all())
    # room = forms.ModelChoiceField(queryset=Room.objects.all())
    check_in = forms.DateField(widget=MyDateInput())
    check_out = forms.DateField(widget=MyDateInput())
   

    # def __init__(self, *args, **kwargs):
    #     super(BookingForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper(self)
    #     self.helper.form_method = 'post'
    #     self.helper.add_input(Submit('submit', 'Check Availability'))

    #     self.helper.layout = Layout(
    #         Field('hotel', css_class='form-control'),
    #         Field('room', css_class='form-control'),
    #         Field('room_type', css_class='form-control'),
    #         Field('check_in', css_class='advanced-calendar form-control'),
    #         Field('check_out', css_class='advanced-calendar form-control'),
    #         Field('total_price', css_class='form-control'),
    #         Submit('submit', 'Check Availability', css_class='btn btn-primary')
    #     )
    
