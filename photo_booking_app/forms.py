from django import forms
from photo_booking_app.models import Reservation, AvailableSlot
from datetime import timedelta, date, datetime, time
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# class ReservationForm(forms.ModelForm):
#     start_time = forms.ChoiceField(choices=[], required=True)
#     end_time = forms.ChoiceField(choices=[], required=True)

#     class Meta:
#         model = Reservation
#         fields = ['name', 'children_name', 'date', 'start_time', 'end_time', 'plan']
#         widgets = {
#             'date': forms.SelectDateWidget,
#         }

#     def __init__(self, *args, **kwargs):
#         selected_date = kwargs.pop('selected_date', None)
#         super().__init__(*args, **kwargs)

#         # 時間の選択肢を初期化
#         if selected_date:
#             try:
#                 date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
#                 slots = AvailableSlot.objects.filter(date=date_obj).order_by('start_time')
#             except ValueError:
#                 slots = AvailableSlot.objects.none()
#         else:
#             slots = AvailableSlot.objects.none()

#         # ChoiceFieldのvalueは文字列で統一
#         time_choices = [
#             (slot.start_time.strftime('%H:%M'), slot.start_time.strftime('%H:%M')) for slot in slots
#         ]

#         self.fields['start_time'].choices = time_choices
#         self.fields['end_time'].choices = time_choices


        
#     def save(self, user=None, commit=True):
#         reservation = super().save(commit=False)
#         if user is not None:
#             reservation.user = user
            
#         reservation.start_time = datetime.strptime(self.cleaned_data['start_time'], "%H:%M").time()
#         reservation.end_time = datetime.strptime(self.cleaned_data['end_time'], "%H:%M").time()
#         if commit:
#             reservation.save() 
#         return reservation
            
class AvailableSlotForm(forms.ModelForm):
    class Meta:
        model = AvailableSlot
        fields = ['date', 'start_time', 'end_time']

class ReservationEditForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time','plan', 'name', 'children_name']

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today() + timedelta(days=3):
            raise forms.ValidationError("予約の変更は3日前までしかできません。")
        return selected_date

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='名字')
    last_name = forms.CharField(max_length=30, required=True, label='名前')
    email = forms.EmailField(required=True, label='メールアドレス')

    class Meta:
        model = User
        fields = ('username', "email",'first_name', 'last_name', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user