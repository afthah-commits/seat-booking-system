import requests
import concurrent.futures
import time

BASE_URL = 'http://127.0.0.1:8000/api/seats'

def attempt_booking(user_index, show_id, row, number):
    # Each thread needs its own session to avoid cookies/auth mixing
    session = requests.Session()
    username = f'stress_user_{user_index}_{int(time.time() * 1000)}'
    password = 'pass123'
    
    # Register and Login
    reg = session.post(f"{BASE_URL}/register/", json={'username': username, 'password': password})
    log = session.post(f"{BASE_URL}/login/", json={'username': username, 'password': password})
    
    if reg.status_code != 201 or log.status_code != 200:
        return f"User {user_index}: Auth Failed"

    # 2. Hold the seat
    hold_resp = session.post(f"{BASE_URL}/hold-batch/", json={
        'show_id': show_id,
        'seats': [{'row': row, 'number': number}]
    })
    
    if hold_resp.status_code != 200:
        return f"User {user_index}: Hold failed - {hold_resp.json().get('error')}"
    
    # 3. Try to book it
    book_resp = session.post(f"{BASE_URL}/book-batch/", json={
        'show_id': show_id,
        'seats': [{'row': row, 'number': number}]
    })
    
    if book_resp.status_code == 200:
        return f"SUCCESS: User {user_index} booked the seat!"
    else:
        return f"FAILED: User {user_index} blocked - {book_resp.json().get('error')}"

def run_stress_test():
    shows = requests.get(f"{BASE_URL}/shows/").json().get('shows', [])
    if not shows:
        print("No shows found.")
        return
    
    show_id = shows[0]['id']
    # Find a seat that is actually AVAILABLE
    resp = requests.get(f"{BASE_URL}/?show_id={show_id}")
    seats = resp.json().get('seats', [])
    available_seat = next((s for s in seats if s['status'] == 'AVAILABLE'), None)
    
    if not available_seat:
        print("No available seats found for this show.")
        return
        
    row = available_seat['row']
    number = available_seat['number']
    
    print(f"Starting stress test for Show {show_id}, Seat {row}{number}...")
    print("Simulating 10 simultaneous users...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_booking, i, show_id, row, number) for i in range(10)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    for r in results:
        print(r)

    success_count = sum(1 for r in results if "SUCCESS" in r)
    failure_count = sum(1 for r in results if "FAILED" in r or "failed" in r)
    
    print("\n" + "="*30)
    print("STRESS TEST RESULTS")
    print("="*30)
    print(f"Successful Bookings: {success_count}")
    print(f"Blocked/Failed:      {failure_count}")
    print("="*30)
    
    if success_count == 1:
        print("VERIFIED: System prevented double-booking under high concurrency!")
    else:
        print(f"WARNING: Success count is {success_count}. Should be exactly 1.")

if __name__ == "__main__":
    run_stress_test()
