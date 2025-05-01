
# accounts/forms.py
from django import forms
from photo_booking_app.models import Reservation  # ← これも大事！

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name', 'children_name', 'date', 'start_time', 'end_time', 'plan']
