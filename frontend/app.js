const API_BASE = 'http://127.0.0.1:8000/api/seats';
let currentShowId = null;
let currentShowPrice = 0;
let selectedSeats = [];

// Initialize
async function init() {
    try {
        const showsResponse = await fetch(`${API_BASE}/shows/`);
        const showsData = await showsResponse.json();

        if (showsData.shows && showsData.shows.length > 0) {
            const show = showsData.shows[0];
            currentShowId = show.id;
            currentShowPrice = parseFloat(show.price);

            document.getElementById('movie-title').textContent = show.movie;
            document.getElementById('movie-screen').textContent = show.screen;
            document.getElementById('movie-time').textContent = new Date(show.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Use the generated poster or a fallback
            document.getElementById('movie-poster').src = 'http://127.0.0.1:8000/static/poster.png'; // Need to serve this
            document.getElementById('movie-poster').onerror = (e) => {
                e.target.src = 'https://via.placeholder.com/140x200/1e293b/ffffff?text=STUDIO+A';
            };

            await loadSeats();
        }

        document.getElementById('loading-overlay').style.display = 'none';
        document.getElementById('main-dashboard').style.display = 'block';
    } catch (err) {
        console.error('Initialization failed:', err);
        document.getElementById('loading-overlay').innerHTML = `
          <div style="text-align: center; padding: 20px; background: #0f172a; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h2 style="color: #ef4444; margin-bottom: 20px; font-size: 2rem;">CONNECTION ERROR</h2>
            <p style="color: #94a3b8; margin-bottom: 20px;">Could not connect to the Backend Server at ${API_BASE}</p>
            <button onclick="location.reload()" class="btn btn-primary" style="padding: 12px 24px; background: linear-gradient(135deg, #0ea5e9, #a855f7); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">Retry Connection</button>
          </div>
        `;
    }
}

async function loadSeats() {
    try {
        const response = await fetch(`${API_BASE}/?show_id=${currentShowId}`);
        const data = await response.json();

        renderStats(data.stats);
        renderSeats(data.seats);
    } catch (err) {
        console.error('Failed to load seats:', err);
    }
}

function renderStats(stats) {
    document.getElementById('stats-available').textContent = stats.available;
    document.getElementById('stats-held').textContent = stats.held;
    document.getElementById('stats-booked').textContent = stats.booked;
}

function renderSeats(seats) {
    const grid = document.getElementById('seat-grid');
    grid.innerHTML = '';

    // Group seats by row
    const rows = {};
    seats.forEach(seat => {
        if (!rows[seat.row]) rows[seat.row] = [];
        rows[seat.row].push(seat);
    });

    Object.keys(rows).sort().forEach(rowKey => {
        const rowEl = document.createElement('div');
        rowEl.className = 'seat-row';

        const label = document.createElement('div');
        label.className = 'row-label';
        label.textContent = rowKey;
        rowEl.appendChild(label);

        rows[rowKey].forEach(seat => {
            const seatEl = document.createElement('div');
            seatEl.className = `seat ${seat.status.toLowerCase()}`;
            if (seat.is_held_expired) seatEl.className = 'seat available';

            seatEl.textContent = seat.number;
            seatEl.dataset.row = seat.row;
            seatEl.dataset.number = seat.number;

            seatEl.onclick = () => toggleSeatSelection(seatEl, seat);

            rowEl.appendChild(seatEl);
        });

        grid.appendChild(rowEl);
    });
}

function toggleSeatSelection(el, seat) {
    if (el.classList.contains('booked')) return;

    const seatId = `${seat.row}${seat.number}`;
    const idx = selectedSeats.findIndex(s => s.id === seatId);

    if (idx > -1) {
        selectedSeats.splice(idx, 1);
        el.classList.remove('selected');
    } else {
        selectedSeats.push({ id: seatId, row: seat.row, number: seat.number });
        el.classList.add('selected');
    }

    updateSummary();
}

function updateSummary() {
    const count = selectedSeats.length;
    const btn = document.getElementById('btn-book');

    if (count > 0) {
        document.getElementById('selection-summary').textContent = `${count} Seat(s) Selected`;
        document.getElementById('total-price').textContent = `$${(count * currentShowPrice).toFixed(2)}`;
        btn.disabled = false;
        btn.textContent = `Hold & Book ${count} Seat(s)`;
    } else {
        document.getElementById('selection-summary').textContent = 'No seats selected';
        document.getElementById('total-price').textContent = '$0.00';
        btn.disabled = true;
        btn.textContent = 'Confirm Booking';
    }
}

// Log helper
function addLog(msg, type = 'accent-primary') {
    const content = document.getElementById('log-content');
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `
    <div class="log-dot" style="background: var(--${type});"></div>
    <div>
      <div class="log-msg">${msg}</div>
      <div class="log-time">${new Date().toLocaleTimeString()}</div>
    </div>
  `;
    content.prepend(item);
}

// Booking Flow
async function handleAction() {
    if (selectedSeats.length === 0) return;

    const btn = document.getElementById('btn-book');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    try {
        // 1. Ensure logged in (using demo credentials for simplicity in this demo)
        const loginRes = await fetch(`${API_BASE}/login/`, {
            method: 'POST',
            body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
        });

        if (loginRes.status === 401) {
            addLog('Logging in as demo user...', 'status-held');
            await fetch(`${API_BASE}/register/`, {
                method: 'POST',
                body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
            });
            await fetch(`${API_BASE}/login/`, {
                method: 'POST',
                body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
            });
        }

        // 2. Hold Seats
        addLog(`Requesting hold for ${selectedSeats.length} seats...`, 'status-held');
        const holdRes = await fetch(`${API_BASE}/hold-batch/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                show_id: currentShowId,
                seats: selectedSeats.map(s => ({ row: s.row, number: s.number }))
            })
        });

        const holdData = await holdRes.json();
        if (holdData.error) throw new Error(holdData.error);

        addLog(`Seats held! Confirming booking...`, 'accent-secondary');

        // 3. Book Seats
        const bookRes = await fetch(`${API_BASE}/book-batch/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                show_id: currentShowId,
                seats: selectedSeats.map(s => ({ row: s.row, number: s.number }))
            })
        });

        const bookData = await bookRes.json();
        if (bookData.error) throw new Error(bookData.error);

        addLog(`Success! Paid $${bookData.total_paid}`, 'status-available');

        selectedSeats = [];
        updateSummary();
        await loadSeats();

    } catch (err) {
        addLog(`Error: ${err.message}`, 'status-booked');
        alert(err.message);
    } finally {
        btn.disabled = false;
        updateSummary();
    }
}

document.getElementById('btn-book').onclick = handleAction;

// Automatic polling every 5 seconds
setInterval(loadSeats, 5000);

init();
