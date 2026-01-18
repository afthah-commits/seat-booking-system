# 🎬 Seat Booking System - Setup Complete!

## ✅ System Status: FULLY OPERATIONAL

Your professional movie seat booking backend is now running successfully!

---

## 🚀 Quick Start

### 1. **Start the Server**
```bash
.\venv\Scripts\python.exe manage.py runserver
```

### 2. **Access the Dashboard**
Open your browser and navigate to:
```
http://localhost:8000
```
⚠️ **Important:** Use `http://` (not `https://`)

### 3. **Default Login Credentials**
- **Username:** `demo_user_123`
- **Password:** `demo123`

---

## 🎯 What's Working

### ✅ Backend Features
- **Atomic State Transitions** - Seats move through AVAILABLE → HELD → BOOKED
- **Row-Level Locking** - `select_for_update()` prevents race conditions
- **10-Minute Hold TTL** - Automatic expiry for abandoned reservations
- **Concurrency Protection** - Tested with 10 simultaneous users
- **Idempotent Operations** - Safe to retry requests

### ✅ API Endpoints
All RESTful endpoints are functional:
- `GET /api/seats/shows/` - List all shows
- `GET /api/seats/?show_id={id}` - Get seat status
- `POST /api/seats/register/` - User registration
- `POST /api/seats/login/` - User authentication
- `POST /api/seats/hold-batch/` - Hold multiple seats
- `POST /api/seats/book-batch/` - Confirm booking
- `POST /api/seats/release-hold-batch/` - Release holds

### ✅ Frontend Dashboard
- **Real-time seat grid** with color-coded status
- **Live statistics** (Available, Held, Booked)
- **Activity log** showing all transactions
- **Multi-show support** with movie posters
- **Responsive design** with premium aesthetics

---

## 🧪 Testing

### Run Unit Tests
```bash
.\venv\Scripts\python.exe manage.py test seats
```

### Run Stress Test (Concurrency)
```bash
.\venv\Scripts\python.exe stress_test.py
```

### Run API Test
```bash
.\venv\Scripts\python.exe test_api.py
```

---

## 📊 Database

### Reset and Seed Data
```bash
.\venv\Scripts\python.exe manage.py seed_data
```

This creates:
- 4 movie shows (Top Gun, Avatar, Inception, etc.)
- 40 seats per show (Rows A-D, 10 seats each)
- Demo user account

### Access Django Admin
```
http://localhost:8000/admin/
```
Create a superuser first:
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```

---

## 🏗️ Architecture Highlights

### State Machine
```
AVAILABLE → HELD (10 min TTL) → BOOKED
     ↑         ↓
     └─────────┘ (Expiry/Release)
```

### Concurrency Protection
```python
with transaction.atomic():
    seat = Seat.objects.select_for_update().filter(...)
    # Atomic state check and update
    seat.status = 'HELD'
    seat.save()
```

### Hold Expiry Logic
- Timestamps stored in database
- Survives server crashes
- Automatic recovery on restart
- Dynamic availability calculation

---

## 📁 Project Structure

```
seat-booking-system/
├── seats/              # Main Django app
│   ├── models.py       # Movie, ShowTime, Seat, Screen
│   ├── views.py        # API endpoints
│   ├── urls.py         # URL routing
│   └── tests.py        # Unit tests
├── frontend/           # Dashboard UI
│   ├── index.html      # (Alternative static version)
│   ├── app.js
│   └── style.css
├── static/             # Served static files
│   ├── app.js
│   └── style.css
├── seats/templates/    # Django templates
│   └── seats/dashboard.html
├── stress_test.py      # Concurrency test
├── test_api.py         # API verification
└── requirements.txt    # Dependencies
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
USE_MYSQL=False
DB_NAME=seat_booking
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Switch to MySQL (Optional)
1. Set `USE_MYSQL=True` in `.env`
2. Install MySQL connector:
   ```bash
   pip install mysqlclient
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```

---

## 🎮 How to Use the Dashboard

1. **Select a Show** - Click on a movie card at the top
2. **Choose Seats** - Click on green (available) seats
3. **Hold Seats** - Click "Hold Seats" button (10-minute timer starts)
4. **Confirm Booking** - Click "Confirm Booking" to finalize
5. **Watch Activity Log** - See real-time updates on the right

---

## 🛡️ Failure Scenarios Handled

| Scenario | Solution |
|----------|----------|
| Server crash during hold | Timestamps in DB, system recovers |
| Concurrent booking attempts | Row-level locking, only 1 succeeds |
| Dropped network responses | Idempotent operations, safe retries |
| Abandoned carts | 10-min TTL, auto-release |
| Payment interruption | Hold expires, seat returns to pool |

---

## 📝 Next Steps

### For Development
- [ ] Add payment gateway integration
- [ ] Implement email confirmations
- [ ] Add seat pricing tiers (VIP, Regular, etc.)
- [ ] Create mobile app API
- [ ] Add analytics dashboard

### For Production
- [ ] Switch to PostgreSQL/MySQL
- [ ] Configure Gunicorn/uWSGI
- [ ] Set up Nginx reverse proxy
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure Redis for caching
- [ ] Set up monitoring (Sentry, etc.)

---

## 🐛 Troubleshooting

### Issue: "This site can't provide a secure connection"
**Solution:** Use `http://` not `https://`

### Issue: "No module named 'django'"
**Solution:** Activate virtual environment:
```bash
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Seats not showing
**Solution:** Run seed data:
```bash
python manage.py seed_data
```

### Issue: Port 8000 already in use
**Solution:** Kill the process or use different port:
```bash
python manage.py runserver 8080
```

---

## 📚 Documentation

- **README.md** - Project overview and setup
- **API Documentation** - See README.md for endpoint details
- **Code Comments** - Inline documentation in views.py

---

## ✨ Features Demonstrated

✅ **Backend Engineering**
- Django REST API design
- Database transaction management
- Concurrency control with locking
- State machine implementation
- TTL-based expiry logic

✅ **System Design**
- Atomic operations
- Race condition prevention
- Failure recovery
- Idempotent APIs
- Real-time updates

✅ **Testing**
- Unit tests for state transitions
- Stress testing for concurrency
- API integration tests

---

## 🎉 Success!

Your seat booking system is ready for demonstration and further development!

**Access it now at:** http://localhost:8000

---

*Built with Django 6.0.1 | Python 3.13 | SQLite*
