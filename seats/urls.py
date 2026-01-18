from django.urls import path
from . import views

urlpatterns = [
    path('', views.seat_list, name='seat_list'),
    path('hold/', views.hold_seat, name='hold_seat'),
    path('book/', views.book_seat, name='book_seat'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('hold-batch/', views.hold_multiple_seats, name='hold_batch'),
    path('book-batch/', views.book_multiple_seats, name='book_batch'),
    path('release-hold-batch/', views.release_batch_holds, name='release_hold_batch'),
    path('shows/', views.list_shows, name='list_shows'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/ticket/', views.get_ticket, name='get_ticket'),
]
