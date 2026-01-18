from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_mins = models.IntegerField()
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)

    def __str__(self):
        return self.title


class Screen(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ShowTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='shows')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='shows', null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # Note: price is now per show, though we could keep a default per show.
    # The user wanted 100 rs for all, so we'll set it here.
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.movie.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Seat(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('HELD', 'Held'),
        ('BOOKED', 'Booked'),
    ]

    show_time = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='seats')
    row_id = models.CharField(max_length=2) # e.g. 'A', 'B'
    number = models.IntegerField() # e.g. 1, 2, 3
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    held_by = models.CharField(max_length=100, null=True, blank=True)
    hold_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('show_time', 'row_id', 'number')
        indexes = [
            models.Index(fields=['show_time', 'row_id', 'number']),
        ]

@receiver(post_save, sender=ShowTime)
def create_seats_for_show(sender, instance, created, **kwargs):
    if created:
        # Auto-generate a standard 50-seat grid (Rows A-E, 10 seats each)
        seats = []
        for row in ['A', 'B', 'C', 'D', 'E']:
            for num in range(1, 11):
                seats.append(Seat(show_time=instance, row_id=row, number=num))
        Seat.objects.bulk_create(seats)
