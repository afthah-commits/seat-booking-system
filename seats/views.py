import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Seat, Movie, ShowTime, Screen
from django.db.models import Q, Count, Sum
from decimal import Decimal


def theatre_dashboard(request):
    return render(request, 'seats/dashboard.html')

def list_shows(request):
    date_str = request.GET.get('date') # YYYY-MM-DD
    shows = ShowTime.objects.filter(end_time__gt=timezone.now()).select_related('movie', 'screen').order_by('start_time')
    
    if date_str:
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            shows = shows.filter(start_time__date=target_date)
        except ValueError:
            pass

    data = []
    for show in shows:
        poster_url = None
        try:
            if show.movie.poster:
                poster_url = show.movie.poster.url
        except Exception:
            poster_url = None

        data.append({
            'id': show.id,
            'movie': show.movie.title,
            'screen': show.screen.name,
            'start_time': show.start_time.isoformat(),
            'end_time': show.end_time.isoformat(),
            'price': str(show.base_price),
            'poster_url': poster_url
        })
    return JsonResponse({'shows': data})


def get_ticket(request, booking_id):
    # For now, searching by Seat ID works since we book seats.
    # In a more advanced system, we'd have a Booking model.
    try:
        seat = get_object_or_404(Seat, id=booking_id, status='BOOKED')
        data = {
            'ticket_id': seat.id,
            'movie': seat.show_time.movie.title,
            'screen': seat.show_time.screen.name,
            'time': seat.show_time.start_time,
            'seat': f"{seat.row_id}{seat.number}",
            'price': str(seat.show_time.base_price),
            'booked_by': seat.held_by,
            'message': "Thank you for booking with us! Please show this ticket at the entrance."
        }
        return JsonResponse({'ticket': data})
    except Exception as e:
        return JsonResponse({'error': 'Ticket not found'}, status=404)


def my_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    bookings = Seat.objects.filter(status='BOOKED', held_by=request.user.username).order_by('-show_time__start_time')
    data = [{
        'id': b.id,
        'movie': b.show_time.movie.title if b.show_time else "Unknown",
        'start_time': b.show_time.start_time if b.show_time else None,
        'row': b.row_id,
        'number': b.number,
        'price': str(b.show_time.base_price)
    } for b in bookings]
    return JsonResponse({'bookings': data})

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=409)

        user = User.objects.create_user(username=username, password=password, email=email)
        return JsonResponse({'message': 'User registered successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

@csrf_exempt
def hold_multiple_seats(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        show_id = data.get('show_id')
        seats_data = data.get('seats', []) # Expect list of {'row': 'A', 'number': 1}
        
        if not show_id:
            return JsonResponse({'error': 'show_id is required'}, status=400)
        if not seats_data or not isinstance(seats_data, list):
            return JsonResponse({'error': 'A list of seats is required'}, status=400)
            
        with transaction.atomic():
            seats_to_hold = []
            for item in seats_data:
                row = item.get('row')
                number = item.get('number')
                
                # Lock and fetch
                seat = Seat.objects.select_for_update().filter(show_time_id=show_id, row_id=row, number=number).first()
                
                if not seat:
                    raise Exception(f"Seat {row}{number} not found for show {show_id}")
                
                # Check status
                is_available = seat.status == 'AVAILABLE'
                is_expired_hold = (seat.status == 'HELD' and seat.hold_expires_at and seat.hold_expires_at < timezone.now())
                is_already_my_hold = (seat.status == 'HELD' and seat.held_by == request.user.username)
                
                if is_available or is_expired_hold or is_already_my_hold:
                    seat.status = 'HELD'
                    seat.held_by = request.user.username
                    seat.hold_expires_at = timezone.now() + timedelta(minutes=10)
                    seats_to_hold.append(seat)
                else:
                    raise Exception(f"Seat {row}{number} is already taken by someone else")
            
            # Save all if loop finished without exception
            for seat in seats_to_hold:
                seat.save()
                
            return JsonResponse({
                'message': f'Successfully held {len(seats_to_hold)} seats',
                'expires_at': seats_to_hold[0].hold_expires_at
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def release_batch_holds(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        show_id = data.get('show_id')
        seats_data = data.get('seats', [])
        
        with transaction.atomic():
            for item in seats_data:
                row = item.get('row')
                number = item.get('number')
                seat = Seat.objects.select_for_update().filter(
                    show_time_id=show_id, 
                    row_id=row, 
                    number=number,
                    status='HELD',
                    held_by=request.user.username
                ).first()
                
                if seat:
                    seat.status = 'AVAILABLE'
                    seat.held_by = None
                    seat.hold_expires_at = None
                    seat.save()
                    
        return JsonResponse({'message': 'Holds released successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def book_multiple_seats(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        show_id = data.get('show_id')
        seats_data = data.get('seats', [])
        if not show_id:
            return JsonResponse({'error': 'show_id is required'}, status=400)
        if not seats_data or not isinstance(seats_data, list):
            return JsonResponse({'error': 'A list of seats is required'}, status=400)
            
        with transaction.atomic():
            seats_to_book = []
            total_price = Decimal('0')
            for item in seats_data:
                row = item.get('row')
                number = item.get('number')
                
                seat = Seat.objects.select_for_update().filter(show_time_id=show_id, row_id=row, number=number).first()
                if not seat:
                    raise Exception(f"Seat {row}{number} not found for show {show_id}")
                
                if seat.status != 'HELD' or seat.held_by != request.user.username:
                    raise Exception(f"Seat {row}{number} is not held by you")
                
                if seat.hold_expires_at and seat.hold_expires_at < timezone.now():
                    raise Exception(f"Hold for seat {row}{number} has expired")
                    
                seat.status = 'BOOKED'
                seat.hold_expires_at = None
                seat.save()
                
                seats_to_book.append(seat)
                total_price += Decimal(str(seat.show_time.base_price))
                

            return JsonResponse({
                'message': f'Successfully booked {len(seats_to_book)} seats',
                'total_paid': str(total_price.quantize(Decimal('0.01')))
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def seat_list(request):
    show_id = request.GET.get('show_id')
    if not show_id:
        # Fallback to first upcoming show if not specified (optional)
        first_show = ShowTime.objects.filter(end_time__gt=timezone.now()).order_by('start_time').first()
        if not first_show:
            return JsonResponse({'seats': [], 'message': 'No upcoming shows'})
        show_id = first_show.id

    seats = Seat.objects.filter(show_time_id=show_id).select_related('show_time__screen').order_by('row_id', 'number')
    screen_name = "Main"
    if seats.exists() and seats[0].show_time and seats[0].show_time.screen:
        screen_name = seats[0].show_time.screen.name

    stats = Seat.objects.filter(show_time_id=show_id).aggregate(
        available=Count('id', filter=Q(status='AVAILABLE') | Q(status='HELD', hold_expires_at__lt=timezone.now())),
        held=Count('id', filter=Q(status='HELD', hold_expires_at__gt=timezone.now())),
        booked=Count('id', filter=Q(status='BOOKED'))
    )

    data = []
    for seat in seats:
        data.append({
            'id': seat.id,
            'row': seat.row_id,
            'number': seat.number,
            'status': seat.status,
            'is_held_expired': seat.status == 'HELD' and seat.hold_expires_at and seat.hold_expires_at < timezone.now()
        })
    return JsonResponse({
        'show_id': show_id, 
        'screen': screen_name, 
        'stats': stats,
        'seats': data
    })

@csrf_exempt
def hold_seat(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        show_id = data.get('show_id')
        row = data.get('row')
        number = data.get('number')
        user_id = request.user.username # Use the logged in user
        
        if not all([show_id, row, number, user_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
            
        with transaction.atomic():
            # Lock the row for update to handle concurrency
            seat = Seat.objects.select_for_update().filter(show_time_id=show_id, row_id=row, number=number).first()
            
            if not seat:
                return JsonResponse({'error': 'Seat not found'}, status=404)
            
            # Check if seat is available
            if seat.status == 'AVAILABLE':
                seat.status = 'HELD'
                seat.held_by = user_id
                seat.hold_expires_at = timezone.now() + timedelta(minutes=10) # Hold for 10 mins
                seat.save()
                return JsonResponse({'message': 'Seat held successfully', 'expires_at': seat.hold_expires_at})
            
            # Check if seat is already held but expired
            if seat.status == 'HELD':
                if seat.hold_expires_at and seat.hold_expires_at < timezone.now():
                    # Expired, so we can take it
                    seat.status = 'HELD'
                    seat.held_by = user_id
                    seat.hold_expires_at = timezone.now() + timedelta(minutes=10)
                    seat.save()
                    return JsonResponse({'message': 'Seat held successfully (previous hold expired)', 'expires_at': seat.hold_expires_at})
                
                return JsonResponse({'error': 'Seat is currently held by someone else'}, status=409)
                
            if seat.status == 'BOOKED':
                 return JsonResponse({'error': 'Seat is already booked'}, status=409)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
         return JsonResponse({'error': str(e)}, status=500)
         
    return JsonResponse({'error': 'Unknown error'}, status=500)

@csrf_exempt
def book_seat(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        show_id = data.get('show_id')
        row = data.get('row')
        number = data.get('number')
        user_id = request.user.username
        
        if not all([show_id, row, number, user_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
            
        with transaction.atomic():
            seat = Seat.objects.select_for_update().filter(show_time_id=show_id, row_id=row, number=number).first()
            
            if not seat:
                return JsonResponse({'error': 'Seat not found'}, status=404)
                
            if seat.status == 'BOOKED':
                return JsonResponse({'error': 'Seat is already booked'}, status=409)
                
            if seat.status == 'HELD':
                if seat.held_by != user_id:
                     return JsonResponse({'error': 'Seat is held by another user'}, status=403)
                
                if seat.hold_expires_at and seat.hold_expires_at < timezone.now():
                    return JsonResponse({'error': 'Hold has expired, please hold again'}, status=400)
                    
                seat.status = 'BOOKED'
                seat.held_by = user_id # Keep track of who booked it
                seat.hold_expires_at = None
                seat.save()
                return JsonResponse({'message': 'Seat booked successfully'})
            
            if seat.status == 'AVAILABLE':
                return JsonResponse({'error': 'You must hold the seat before booking'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Unknown error'}, status=500)
