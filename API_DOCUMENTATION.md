# 📡 API Documentation - Seat Booking System

## Base URL
```
http://localhost:8000/api/seats
```

---

## 🔐 Authentication

Most endpoints require authentication. Use session-based authentication after logging in.

### Register User
**POST** `/register/`

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password",
  "email": "john@example.com"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully"
}
```

**Error Responses:**
- `400` - Missing required fields
- `409` - Username already exists

---

### Login
**POST** `/login/`

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful"
}
```

**Error Response:**
- `401` - Invalid credentials

---

### Logout
**POST** `/logout/`

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

## 🎬 Show Management

### List Shows
**GET** `/shows/`

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD format)

**Response (200 OK):**
```json
{
  "shows": [
    {
      "id": 1,
      "movie": "Avatar: The Way of Water",
      "screen": "Screen 2 (Indie Hall)",
      "start_time": "2026-01-18T18:58:00Z",
      "end_time": "2026-01-18T21:58:00Z",
      "price": "100.00",
      "poster_url": "/media/posters/avatar.jpg"
    }
  ]
}
```

---

## 💺 Seat Management

### Get Seats for Show
**GET** `/?show_id={id}`

**Query Parameters:**
- `show_id` (required): ID of the show

**Response (200 OK):**
```json
{
  "show_id": 1,
  "screen": "Screen 2 (Indie Hall)",
  "stats": {
    "available": 38,
    "held": 2,
    "booked": 0
  },
  "seats": [
    {
      "id": 1,
      "row": "A",
      "number": 1,
      "status": "AVAILABLE",
      "is_held_expired": false
    },
    {
      "id": 2,
      "row": "A",
      "number": 2,
      "status": "HELD",
      "is_held_expired": false
    },
    {
      "id": 3,
      "row": "A",
      "number": 3,
      "status": "BOOKED",
      "is_held_expired": false
    }
  ]
}
```

**Seat Status Values:**
- `AVAILABLE` - Seat is free to book
- `HELD` - Seat is temporarily reserved (10-minute TTL)
- `BOOKED` - Seat is confirmed and paid

**Note:** `is_held_expired` indicates if a HELD seat's TTL has expired (making it effectively available)

---

### Hold Single Seat
**POST** `/hold/`

**Authentication:** Required

**Request Body:**
```json
{
  "show_id": 1,
  "row": "A",
  "number": 5
}
```

**Response (200 OK):**
```json
{
  "message": "Seat held successfully",
  "expires_at": "2026-01-18T19:08:00Z"
}
```

**Error Responses:**
- `400` - Missing required fields
- `401` - Authentication required
- `404` - Seat not found
- `409` - Seat already taken

---

### Hold Multiple Seats (Batch)
**POST** `/hold-batch/`

**Authentication:** Required

**Request Body:**
```json
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6},
    {"row": "B", "number": 1}
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully held 3 seats",
  "expires_at": "2026-01-18T19:08:00Z"
}
```

**Error Responses:**
- `400` - Invalid request or seat already taken
- `401` - Authentication required

**Important:** This operation is atomic - either all seats are held or none are.

---

### Book Single Seat
**POST** `/book/`

**Authentication:** Required

**Request Body:**
```json
{
  "show_id": 1,
  "row": "A",
  "number": 5
}
```

**Response (200 OK):**
```json
{
  "message": "Seat booked successfully"
}
```

**Error Responses:**
- `400` - Seat not held by you or hold expired
- `401` - Authentication required
- `403` - Seat held by another user
- `404` - Seat not found
- `409` - Seat already booked

**Prerequisites:**
- Seat must be in HELD status
- Seat must be held by the requesting user
- Hold must not be expired

---

### Book Multiple Seats (Batch)
**POST** `/book-batch/`

**Authentication:** Required

**Request Body:**
```json
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6}
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully booked 2 seats",
  "total_paid": "200.00"
}
```

**Error Responses:**
- `400` - Seats not held by you or validation failed
- `401` - Authentication required

**Important:** This operation is atomic - either all seats are booked or none are.

---

### Release Held Seats (Batch)
**POST** `/release-hold-batch/`

**Authentication:** Required

**Request Body:**
```json
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6}
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Holds released successfully"
}
```

**Error Response:**
- `401` - Authentication required

**Note:** Only releases seats held by the requesting user.

---

## 📋 Booking Management

### My Bookings
**GET** `/my-bookings/`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "bookings": [
    {
      "id": 15,
      "movie": "Avatar: The Way of Water",
      "start_time": "2026-01-18T18:58:00Z",
      "row": "A",
      "number": 5,
      "price": "100.00"
    }
  ]
}
```

**Error Response:**
- `401` - Authentication required

---

### Get Ticket
**GET** `/booking/{booking_id}/ticket/`

**Path Parameters:**
- `booking_id`: ID of the booked seat

**Response (200 OK):**
```json
{
  "ticket": {
    "ticket_id": 15,
    "movie": "Avatar: The Way of Water",
    "screen": "Screen 2 (Indie Hall)",
    "time": "2026-01-18T18:58:00Z",
    "seat": "A5",
    "price": "100.00",
    "booked_by": "john_doe",
    "message": "Thank you for booking with us! Please show this ticket at the entrance."
  }
}
```

**Error Response:**
- `404` - Ticket not found

---

## 🔄 State Transitions

### Seat Lifecycle

```
┌─────────────┐
│  AVAILABLE  │
└──────┬──────┘
       │ POST /hold/ or /hold-batch/
       ▼
┌─────────────┐
│    HELD     │ ◄──┐
│ (10 min TTL)│    │ Automatic expiry
└──────┬──────┘    │ or manual release
       │           │
       │ POST /book/ or /book-batch/
       ▼           │
┌─────────────┐    │
│   BOOKED    │    │
└─────────────┘    │
                   │
       POST /release-hold-batch/
       └────────────┘
```

### Business Rules

1. **Hold Duration:** 10 minutes from hold time
2. **Atomic Operations:** Batch operations are all-or-nothing
3. **Concurrency:** Row-level locking prevents double-booking
4. **Idempotency:** Re-holding your own held seat extends the TTL
5. **Auto-Expiry:** Expired holds are automatically treated as available

---

## 🚨 Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Missing fields, invalid data |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Trying to book someone else's hold |
| 404 | Not Found | Seat or show doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 409 | Conflict | Seat already taken |
| 500 | Server Error | Database or system error |

---

## 📊 Rate Limiting

**Current Limits:** None (development)

**Recommended Production Limits:**
- Authentication endpoints: 5 requests/minute per IP
- Booking endpoints: 10 requests/minute per user
- Read endpoints: 60 requests/minute per user

---

## 🧪 Example Workflows

### Complete Booking Flow

```javascript
// 1. Register
POST /api/seats/register/
{
  "username": "alice",
  "password": "secure123",
  "email": "alice@example.com"
}

// 2. Login
POST /api/seats/login/
{
  "username": "alice",
  "password": "secure123"
}

// 3. Get available shows
GET /api/seats/shows/

// 4. View seats for a show
GET /api/seats/?show_id=1

// 5. Hold seats
POST /api/seats/hold-batch/
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6}
  ]
}

// 6. Confirm booking (within 10 minutes)
POST /api/seats/book-batch/
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6}
  ]
}

// 7. View my bookings
GET /api/seats/my-bookings/

// 8. Get ticket details
GET /api/seats/booking/15/ticket/
```

### Cancel Held Seats

```javascript
// Release holds before they expire
POST /api/seats/release-hold-batch/
{
  "show_id": 1,
  "seats": [
    {"row": "A", "number": 5},
    {"row": "A", "number": 6}
  ]
}
```

---

## 🔧 Testing with cURL

### Register and Login
```bash
# Register
curl -X POST http://localhost:8000/api/seats/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Login (save cookies)
curl -X POST http://localhost:8000/api/seats/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' \
  -c cookies.txt

# Use session for subsequent requests
curl -X GET http://localhost:8000/api/seats/shows/ \
  -b cookies.txt
```

### Hold and Book
```bash
# Hold seats
curl -X POST http://localhost:8000/api/seats/hold-batch/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"show_id":1,"seats":[{"row":"A","number":1}]}'

# Book seats
curl -X POST http://localhost:8000/api/seats/book-batch/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"show_id":1,"seats":[{"row":"A","number":1}]}'
```

---

## 📝 Notes

- All timestamps are in ISO 8601 format (UTC)
- Session cookies are used for authentication
- CSRF protection is disabled for API endpoints (development only)
- All monetary values are strings with 2 decimal places
- Batch operations are atomic transactions

---

## 🔗 Related Documentation

- [Setup Guide](SETUP_COMPLETE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [README](README.md)

---

**API Version:** 1.0  
**Last Updated:** January 18, 2026
