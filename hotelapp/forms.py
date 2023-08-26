from django import forms
from hotelapp.models import Booking, Room, Hotel,Review
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class MyDateInput(forms.widgets.DateInput):
    input_type = 'date'

class BookingForm(forms.Form):
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all())
    check_in = forms.DateField(widget=MyDateInput())
    check_out = forms.DateField(widget=MyDateInput())

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model =Review
        fields = ['hotel', 'rating', 'review_text', 'images']
        
    def clean(self):
        cleaned_data = super().clean()
        review_text = cleaned_data.get('review_text')
        if len(review_text) >= 1000:
            raise forms.ValidationError('Review text must not be more than 1000 words')
        return cleaned_data