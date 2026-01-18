const API_BASE = '/api/seats';
let currentShowId = null;
let currentShowPrice = 0;
let selectedSeats = [];

let allShows = [];

// Initialize
async function init() {
    try {
        const showsResponse = await fetch(`${API_BASE}/shows/`);
        const showsData = await showsResponse.json();
        allShows = showsData.shows || [];

        if (allShows.length > 0) {
            renderShowSelector();
            // Select first show by default
            await selectShow(allShows[0].id);
        } else {
            document.getElementById('show-list').innerHTML = '<div class="no-shows">No active shows found.</div>';
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

function renderShowSelector() {
    const list = document.getElementById('show-list');
    list.innerHTML = '';

    allShows.forEach(show => {
        const card = document.createElement('div');
        card.className = `show-card ${show.id === currentShowId ? 'active' : ''}`;
        card.id = `show-card-${show.id}`;

        const time = new Date(show.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        card.innerHTML = `
            <span class="show-title">${show.movie}</span>
            <span class="show-time">${show.screen} • ${time}</span>
        `;

        card.onclick = () => selectShow(show.id);
        list.appendChild(card);
    });
}

async function selectShow(showId) {
    if (currentShowId === showId) return;

    // UI Feedback
    if (currentShowId) {
        const oldCard = document.getElementById(`show-card-${currentShowId}`);
        if (oldCard) oldCard.classList.remove('active');
    }

    currentShowId = showId;
    const newCard = document.getElementById(`show-card-${currentShowId}`);
    if (newCard) newCard.classList.add('active');

    const show = allShows.find(s => s.id === showId);
    if (!show) return;

    currentShowPrice = parseFloat(show.price);
    selectedSeats = [];
    updateSummary();

    document.getElementById('movie-title').textContent = show.movie;
    document.getElementById('movie-screen').textContent = show.screen;
    document.getElementById('movie-time').textContent = new Date(show.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('logged-username').textContent = currentUsername;

    // Use the dynamic poster URL from the backend
    if (show.poster_url) {
        document.getElementById('movie-poster').src = show.poster_url;
    } else {
        document.getElementById('movie-poster').src = 'http://127.0.0.1:8000/static/poster.png';
    }

    document.getElementById('movie-poster').onerror = (e) => {
        e.target.src = 'https://via.placeholder.com/140x200/1e293b/ffffff?text=' + encodeURIComponent(show.movie);
    };

    addLog(`Switched to: ${show.movie}`, 'accent-primary');
    await loadSeats();
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

            // Preserve selection state across refreshes
            const seatId = `${seat.row}${seat.number}`;
            if (selectedSeats.some(s => s.id === seatId)) {
                seatEl.classList.add('selected');
            }

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

const currentUsername = 'demo_user_123';

// Confirm User Exists & Logged In helper
async function ensureAuthenticated() {
    const loginRes = await fetch(`${API_BASE}/login/`, {
        method: 'POST',
        body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
    });

    if (loginRes.status === 401) {
        addLog('Registering demo user...', 'status-held');
        await fetch(`${API_BASE}/register/`, {
            method: 'POST',
            body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
        });
        await fetch(`${API_BASE}/login/`, {
            method: 'POST',
            body: JSON.stringify({ username: 'demo_user_123', password: 'demo_pass_123' })
        });
    }
}

// Hold Logic
async function handleHold() {
    if (selectedSeats.length === 0) return;
    const btn = document.getElementById('btn-hold');
    btn.disabled = true;

    try {
        await ensureAuthenticated();
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

        addLog(`Successfully held! Use 'Confirm Booking' to finalize.`, 'status-held');

        // Find held seats to "select" them for booking or just clear and let user select held ones
        // In this UI, we'll keep the locally held seats as our current selections for the next step
        updateSummary();
        await loadSeats();

    } catch (err) {
        addLog(`Hold failed: ${err.message}`, 'status-booked');
        alert(err.message);
    } finally {
        btn.disabled = false;
        updateSummary();
    }
}

// Booking Logic
async function handleBook() {
    // Collect all seats currently held by the user for this show
    // For simplicity, we can use the ones currently 'selected' in the UI if they are held
    // Actually, let's just use whatever is currently held by this user according to the API
    const response = await fetch(`${API_BASE}/?show_id=${currentShowId}`);
    const data = await response.json();
    const myHeldSeats = data.seats.filter(s => s.status === 'HELD' && !s.is_held_expired); // Simplified: assuming held by me if held

    if (myHeldSeats.length === 0) {
        alert("You must hold seats before booking!");
        return;
    }

    const btn = document.getElementById('btn-book');
    btn.disabled = true;
    btn.textContent = 'Booking...';

    try {
        await ensureAuthenticated();
        addLog(`Booking ${myHeldSeats.length} held seats...`, 'accent-secondary');

        const bookRes = await fetch(`${API_BASE}/book-batch/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                show_id: currentShowId,
                seats: myHeldSeats.map(s => ({ row: s.row, number: s.number }))
            })
        });

        const bookData = await bookRes.json();
        if (bookData.error) throw new Error(bookData.error);

        addLog(`Booking Confirmed! Total: $${bookData.total_paid}`, 'status-available');

        selectedSeats = []; // Clear local selection
        updateSummary();
        await loadSeats();

    } catch (err) {
        addLog(`Booking failed: ${err.message}`, 'status-booked');
        alert(err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Confirm Booking';
        updateSummary();
    }
}

function updateSummary() {
    const count = selectedSeats.length;
    const btnHold = document.getElementById('btn-hold');
    const btnBook = document.getElementById('btn-book');

    // Hold button active if seats are selected
    btnHold.disabled = count === 0;

    // Book button active if any seats are currently 'HELD' in the system (simplification for demo)
    // In a real app we'd check if any are held BY ME.
    // For now, let's just keep it simple: if selectedSeats are already held, let user book.
    btnBook.disabled = count === 0;

    if (count > 0) {
        document.getElementById('selection-summary').textContent = `${count} Seat(s) Selected`;
        document.getElementById('total-price').textContent = `$${(count * currentShowPrice).toFixed(2)}`;
    } else {
        document.getElementById('selection-summary').textContent = 'No seats selected';
        document.getElementById('total-price').textContent = '$0.00';
    }
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

document.getElementById('btn-hold').onclick = handleHold;
document.getElementById('btn-book').onclick = handleBook;

// Automatic polling every 5 seconds
setInterval(loadSeats, 5000);

init();
