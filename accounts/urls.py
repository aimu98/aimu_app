from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import signup_view
app_name = 'accounts' 

urlpatterns = [
    path('mypage/', views.mypage, name='mypage'),
    path('reservations_history/', views.reservation_history, name='reservation_history'),
     path('reservation/edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('signup/', views.signup_view, name='signup'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reservations/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('password_change/', views.password_change, name='password_change'),
    path('password_change/done/', views.password_change_done, name='password_change_done'),
    path('logout/', views.custom_logout, name='logout'),
]

