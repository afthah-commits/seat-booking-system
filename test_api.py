import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000/api/seats'

print("Testing API Endpoints...")
print("=" * 50)

# Test 1: Get shows
print("\n1. Testing GET /api/seats/shows/")
resp = requests.get(f"{BASE_URL}/shows/")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    shows = resp.json().get('shows', [])
    print(f"Found {len(shows)} shows")
    if shows:
        print(f"First show: {shows[0]}")
else:
    print(f"Error: {resp.text}")

# Test 2: Register a user
print("\n2. Testing POST /api/seats/register/")
session = requests.Session()
username = f"test_user_{int(time.time() * 1000)}"
reg_resp = session.post(f"{BASE_URL}/register/", json={
    'username': username,
    'password': 'test123'
})
print(f"Status: {reg_resp.status_code}")
print(f"Response: {reg_resp.json()}")

# Test 3: Login
print("\n3. Testing POST /api/seats/login/")
login_resp = session.post(f"{BASE_URL}/login/", json={
    'username': username,
    'password': 'test123'
})
print(f"Status: {login_resp.status_code}")
print(f"Response: {login_resp.json()}")

# Test 4: Get seats
if shows:
    show_id = shows[0]['id']
    print(f"\n4. Testing GET /api/seats/?show_id={show_id}")
    seats_resp = session.get(f"{BASE_URL}/?show_id={show_id}")
    print(f"Status: {seats_resp.status_code}")
    if seats_resp.status_code == 200:
        data = seats_resp.json()
        print(f"Stats: {data.get('stats')}")
        available = [s for s in data.get('seats', []) if s['status'] == 'AVAILABLE']
        print(f"Available seats: {len(available)}")
        
        # Test 5: Hold a seat
        if available:
            seat = available[0]
            print(f"\n5. Testing POST /api/seats/hold-batch/ for seat {seat['row']}{seat['number']}")
            hold_resp = session.post(f"{BASE_URL}/hold-batch/", json={
                'show_id': show_id,
                'seats': [{'row': seat['row'], 'number': seat['number']}]
            })
            print(f"Status: {hold_resp.status_code}")
            print(f"Response: {hold_resp.json()}")
            
            # Test 6: Book the seat
            if hold_resp.status_code == 200:
                print(f"\n6. Testing POST /api/seats/book-batch/")
                book_resp = session.post(f"{BASE_URL}/book-batch/", json={
                    'show_id': show_id,
                    'seats': [{'row': seat['row'], 'number': seat['number']}]
                })
                print(f"Status: {book_resp.status_code}")
                print(f"Response: {book_resp.json()}")

print("\n" + "=" * 50)
print("API Test Complete!")
