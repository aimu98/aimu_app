from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .forms import AvailableSlotForm,ReservationEditForm, CustomUserCreationForm
from photo_booking_app.models import Reservation , AvailableSlot, User
from datetime import datetime, time, timedelta , date
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LogoutView, PasswordResetView
from django.contrib.auth.forms import PasswordResetForm,UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse,reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes 
from django.contrib.auth import get_user_model
from django.views.generic import CreateView


# @login_required
# def reservation_form(request):
#     if request.method == 'POST':
#         selected_date = request.POST.get('date')
#         form = ReservationForm(request.POST, selected_date=selected_date)

#         if form.is_valid():
#             reservation = form.save(commit=False)
#             reservation.user = request.user
#             reservation.save()

#             # メール送信（お客様）
#             send_mail(
#                 subject='【撮影予約完了のお知らせ】',
#                 message=(
#                     f"{request.user.first_name} 様\n\n"
#                     f"以下の内容でご予約を承りました。\n\n"
#                     f"日付: {reservation.date}\n"
#                     f"時間: {reservation.start_time}〜{reservation.end_time}\n"
#                     f"プラン: {reservation.get_plan_display()}\n\n"
#                     f"ご不明点があればご連絡ください。"
#                 ),
#                 from_email='no-reply@example.com',
#                 recipient_list=[request.user.email],
#                 fail_silently=False,
#             )

#             # メール送信（管理者）
#             send_mail(
#                 subject='【新しい予約が入りました】',
#                 message=(
#                     f"新しい予約が入りました。\n"
#                     f"お名前：{reservation.name}\n"
#                     f"日付：{reservation.date}\n"
#                     f"時間：{reservation.start_time}〜{reservation.end_time}\n"
#                     f"プラン：{reservation.get_plan_display()}"
#                 ),
#                 from_email='no-reply@example.com',
#                 recipient_list=['your_admin_email@example.com'],
#                 fail_silently=False,
#             )

#             return redirect('reservation_done')
#         else:
#             # バリデーションエラー表示
#             return render(request, 'photo_booking_app/reservation_form.html', {'form': form})
    
#     else:
#         form = ReservationForm()

#     return render(request, 'photo_booking_app/reservation_form.html', {'form': form})


@login_required
def reservation_form(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        plan = request.POST.get('plan')
        name = request.POST.get('name')
        children_name = request.POST.get('children_name')

        try:
            reservation = Reservation.objects.create(
                user=request.user,
                date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                start_time=datetime.strptime(start_time_str, '%H:%M').time(),
                end_time=datetime.strptime(end_time_str, '%H:%M').time(),
                plan=plan,
                name=name,
                children_name=children_name,
            )

            # メール送信（お客様）
            send_mail(
                subject='【撮影予約完了のお知らせ】',
                message=(
                    f"{request.user.first_name} 様\n\n"
                    f"以下の内容でご予約を承りました。\n\n"
                    f"日付: {reservation.date}\n"
                    f"時間: {reservation.start_time}〜{reservation.end_time}\n"
                    f"プラン: {reservation.get_plan_display()}\n\n"
                    f"ご不明点があればご連絡ください。"
                ),
                from_email='no-reply@example.com',
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            # メール送信（管理者）
            send_mail(
                subject='【新しい予約が入りました】',
                message=(
                    f"新しい予約が入りました。\n"
                    f"保護者名：{reservation.name}\n"
                    f"お子様名：{reservation.children_name}\n"
                    f"日付：{reservation.date}\n"
                    f"時間：{reservation.start_time}〜{reservation.end_time}\n"
                    f"プラン：{reservation.get_plan_display()}"
                ),
                from_email='no-reply@example.com',
                recipient_list=['ay.1031.ld@gmail.com'],
                fail_silently=False,
            )

            return redirect('reservation_done')

        except Exception as e:
            messages.error(request, f"予約に失敗しました: {e}")
            return render(request, 'photo_booking_app/reservation_form.html')

    return render(request, 'photo_booking_app/reservation_form.html')



def reservation_done(request):
    return render(request, 'photo_booking_app/reservation_done.html')

def get_available_dates(request):
    available_slots = AvailableSlot.objects.values_list('date', flat=True).distinct()
    dates = [slot.strftime('%Y-%m-%d') for slot in available_slots]
    return JsonResponse({'available_dates': dates})

def get_available_times(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'available_times': []})

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'available_times': []})

    slots = AvailableSlot.objects.filter(date=date_obj)

    time_slots = [
        f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
        for slot in slots
    ]
    return JsonResponse({'available_times': time_slots})


def available_slots_view(request):
    available_slots = AvailableSlot.objects.all()
    return render(request, 'photo_booking_app/available_slots.html', {'available_slots': available_slots})


def add_available_slot(request):
    if request.method == 'POST':
        form = AvailableSlotForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_available_slots') 
    else:
        form = AvailableSlotForm()

    return render(request, 'photo_booking_app/add_available_slot.html', {'form': form})

# def add_event_to_google_calendar(reservation):
#     SCOPES = ['https://www.googleapis.com/auth/calendar']
#     creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
#     service = build('calendar', 'v3', credentials=creds)

#     event = {
#         'summary': f'📷 予約: {reservation.name}',
#         'description': reservation.message,
#         'start': {
#             'dateTime': datetime.combine(reservation.slot.date, reservation.slot.start_time).isoformat(),
#             'timeZone': 'Asia/Tokyo',
#         },
#         'end': {
#             'dateTime': datetime.combine(reservation.slot.date, reservation.slot.end_time).isoformat(),
#             'timeZone': 'Asia/Tokyo',
#         },
#     }

#     service.events().insert(calendarId='ay.1031.ld@group.calendar.google.com', body=event).execute()
    

  
@require_POST  
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
def mypage(request):
    return render(request, 'accounts/mypage.html')
    
def test_mail(request):
    send_mail(
        'テストメール件名',
        'これはDjangoからのテストメールです。',
        'ay.1031.ld@gmail.com',  # 送信者
        ['furutono.a.b'],     # 受信者
        fail_silently=False,
    )
    return HttpResponse("テストメールを送信しました！")



def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, 'photo_booking_app/reservation_detail.html', {'reservation': reservation})

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if (reservation.date - date.today()).days < 3:
        messages.error(request, "3日以内の予約は編集できません。")
        return redirect('reservation_history')

    if request.method == 'POST':
        form = ReservationEditForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save()
            messages.success(request, "予約内容を更新しました。")
            
            send_mail(
                subject='【予約変更通知】予約が編集されました',
                message=(
                    f"以下の予約がユーザー {request.user.username} によって変更されました：\n\n"
                    f"予約日: {updated_reservation.date}\n"
                    f"時間: {updated_reservation.start_time} ～ {updated_reservation.end_time}\n"
                    f"プラン: {updated_reservation.plan}\n"
                    f"名前: {updated_reservation.name}\n"
                    f"お子様の名前: {updated_reservation.children_name}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL, request.user.email],
                fail_silently=False,
            )
            return redirect('reservation_history')
    else:
        form = ReservationEditForm(instance=reservation)

    return render(request, 'photo_booking_app/edit_reservation.html', {'form': form, 'reservation': reservation})

@staff_member_required
def admin_reservation_dashboard(request):
    reservations = Reservation.objects.all().order_by('-date', '-start_time')
    print(reservations)  # データが正しく取得されているかコンソールで確認
    return render(request, 'photo_booking_app/admin_dashboard.html', {'reservations': reservations})

def admin_reservation_list(request, user_id=None):
    users = User.objects.all()
    if user_id:
        reservations = Reservation.objects.filter(user__id=user_id).order_by('-date', '-start_time')
    else:
        reservations = Reservation.objects.all().order_by('-date', '-start_time')

    print(reservations)  # データが正しく取得されているかコンソールで確認
    return render(request, 'photo_booking_app/admin_reservation_list.html', {'reservations': reservations})

def logout_done(request):
    return render(request, 'photo_booking_app/logout_done.html')

def home(request):
    return render(request, 'home.html', {'hide_header': True})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None  

            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk)) 
                domain = get_current_site(request).domain
                link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                reset_url = f'http://{domain}{link}'

                subject = "パスワードリセットリンク"
                message = render_to_string('password_reset_email.html', {
                    'reset_url': reset_url,
                })
                send_mail(subject, message, 'no-reply@example.com', [email])
                return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_request.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
   
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST.get('password')
                user.set_password(password)
                user.save()
                return redirect('password_reset_complete')
            return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    except Exception:
        pass
    return redirect('password_reset')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')