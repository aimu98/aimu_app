from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.shortcuts import render, redirect,get_object_or_404 
from photo_booking_app.models import Reservation
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView
from photo_booking_app.forms import CustomUserCreationForm
from .forms import ReservationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'hide_header': True})

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def mypage(request):
    return render(request, 'accounts/mypage.html')

@login_required
def reservation_history(request):
    today = timezone.localdate()
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'accounts/reservation_history.html', {
        'reservations': reservations,
        'today': today
    })

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if (reservation.date - date.today()).days >= 3:
        reservation.delete()
        messages.success(request, "予約をキャンセルしました。")
    else:
        messages.error(request, "3日以内の予約はキャンセルできません。")

    return redirect('reservation_history')

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('accounts:reservation_history')  # 編集完了後に予約履歴に戻す
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'accounts/edit_reservation.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('accounts:password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})

@login_required
def password_change_done(request):
    return render(request, 'accounts/password_change_done.html')

@login_required
def password_change_done(request):
    return render(request, 'accounts/password_change_done.html')

@login_required
def mypage(request):
    return render(request, 'accounts/mypage.html')

def custom_logout(request):
    logout(request)  
    return render(request, 'accounts/logout_done.html') 

