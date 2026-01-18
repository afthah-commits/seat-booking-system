from django.core.management.base import BaseCommand
from django.utils import timezone
from seats.models import Seat

class Command(BaseCommand):
    help = 'Cleans up expired seat holds and makes them available'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        expired_holds = Seat.objects.filter(
            status='HELD',
            hold_expires_at__lt=now
        )
        
        count = expired_holds.count()
        if count > 0:
            expired_holds.update(
                status='AVAILABLE',
                held_by=None,
                hold_expires_at=None
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully cleared {count} expired holds.'))
        else:
            self.stdout.write(self.style.SUCCESS('No expired holds found.'))
