from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from seats.models import Seat, Movie, ShowTime, Screen

class Command(BaseCommand):
    help = 'Seeds the database with initial theatre data'

    def handle(self, *args, **kwargs):
        # Clear all existing data
        Seat.objects.all().delete()
        ShowTime.objects.all().delete()
        Movie.objects.all().delete()
        Screen.objects.all().delete()
        from django.contrib.auth.models import User
        User.objects.filter(username='demo_user_123').delete()
        User.objects.create_user(username='demo_user_123', password='demo_pass_123')
        
        self.stdout.write("Cleared all existing data and recreated demo user.")

        # 1. Create Screens
        s1 = Screen.objects.create(name="Screen 1 (Main Hall)", description="50 seats large hall")
        s2 = Screen.objects.create(name="Screen 2 (Indie Hall)", description="30 seats cozy hall")

        # 2. Create Movies
        m1 = Movie.objects.create(title="Avatar: The Way of Water", duration_mins=192, poster="posters/avatar.png")
        m2 = Movie.objects.create(title="Inception", duration_mins=148, poster="posters/inception.png")
        m3 = Movie.objects.create(title="Top Gun: Maverick", duration_mins=130, poster="posters/top_gun.png")

        # 3. Create ShowTimes
        shows = [
            ShowTime(movie=m1, screen=s1, start_time=timezone.now() + timedelta(hours=2), end_time=timezone.now() + timedelta(hours=5)),
            ShowTime(movie=m1, screen=s2, start_time=timezone.now() + timedelta(hours=6), end_time=timezone.now() + timedelta(hours=9)),
            ShowTime(movie=m2, screen=s2, start_time=timezone.now() + timedelta(hours=3), end_time=timezone.now() + timedelta(hours=6)),
            ShowTime(movie=m3, screen=s1, start_time=timezone.now() + timedelta(hours=1), end_time=timezone.now() + timedelta(hours=3)),
        ]
        ShowTime.objects.bulk_create(shows)
        all_shows = ShowTime.objects.all()

        total_seats = 0
        for show in all_shows:
            seats = []
            if "Screen 1" in show.screen.name:
                rows = ['A', 'B', 'C', 'D', 'E']
                seats_per_row = 10
            else:
                rows = ['A', 'B', 'C']
                seats_per_row = 10

            for row in rows:
                for num in range(1, seats_per_row + 1):
                    seats.append(Seat(show_time=show, row_id=row, number=num))
            
            Seat.objects.bulk_create(seats)
            total_seats += len(seats)
            
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {total_seats} seats across {all_shows.count()} shows."))
