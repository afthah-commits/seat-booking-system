from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Movie, Screen, ShowTime, Seat
import json

class SeatBookingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.movie = Movie.objects.create(title="Test Movie", duration_mins=120)
        self.screen = Screen.objects.create(name="Screen 1")
        self.show = ShowTime.objects.create(
            movie=self.movie, 
            screen=self.screen, 
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=3)
        )
        self.seat = Seat.objects.create(show_time=self.show, row_id="A", number=1)
        self.client.login(username='testuser', password='password123')

    def test_seat_availability_stats(self):
        """Verify that the seat list returns correct availability stats."""
        response = self.client.get(f'/api/seats/?show_id={self.show.id}')
        data = response.json()
        self.assertEqual(data['stats']['available'], 1)
        self.assertEqual(data['stats']['held'], 0)
        self.assertEqual(data['stats']['booked'], 0)

    def test_hold_and_book_flow(self):
        """Verify the standard flow: Available -> Hold -> Book."""
        # 1. Hold
        hold_data = {'show_id': self.show.id, 'row': "A", 'number': 1}
        response = self.client.post('/api/seats/hold/', data=json.dumps(hold_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify stats update
        response = self.client.get(f'/api/seats/?show_id={self.show.id}')
        self.assertEqual(response.json()['stats']['held'], 1)

        # 2. Book
        book_data = {'show_id': self.show.id, 'row': "A", 'number': 1}
        response = self.client.post('/api/seats/book/', data=json.dumps(book_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # Verify final status
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, 'BOOKED')
        
    def test_expired_hold_becomes_available(self):
        """Verify that an expired hold is treated as available."""
        self.seat.status = 'HELD'
        self.seat.held_by = 'otheruser'
        self.seat.hold_expires_at = timezone.now() - timedelta(minutes=1)
        self.seat.save()
        
        # Attempt to hold
        hold_data = {'show_id': self.show.id, 'row': "A", 'number': 1}
        response = self.client.post('/api/seats/hold/', data=json.dumps(hold_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Seat held successfully (previous hold expired)')
