async function submitPG(e) {
  e.preventDefault();

  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    return;
  }

  const data = {
    name: document.getElementById("name").value,
    area: document.getElementById("area").value,
    city: document.getElementById("city").value,
    latitude: parseFloat(document.getElementById("latitude").value),
    longitude: parseFloat(document.getElementById("longitude").value),
    price: parseFloat(document.getElementById("price").value),
    gender_type: document.getElementById("gender").value,
    description: document.getElementById("description").value
  };

  try {
    const res = await fetch("https://pg-finder-production.up.railway.app/api/v1/pgs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (res.status === 200 || res.status === 201) {
      alert("PG created successfully");
      window.location.href = "index.html";
    } else {
      alert("Error: " + JSON.stringify(result));
    }

  } catch (err) {
    console.error(err);
    alert("Server error");
  }
}
async function loginUser(email, password) {
  try {
    const res = await fetch("https://pg-finder-production.up.railway.app/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.status === 200) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "index.html";
    } else {
      alert("Login failed: " + JSON.stringify(data));
    }
  } catch (err) {
    console.error("Login error:", err);
    alert("Server error. Please try again.");
  }
}

async function registerUser(name, email, password) {
  try {
    const res = await fetch("https://pg-finder-production.up.railway.app/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password, role: "user" })
    });

    const data = await res.json();

    if (res.status === 200 || res.status === 201) {
      localStorage.setItem("token", data.access_token);
      window.location.href = "index.html";
    } else {
      alert("Signup failed: " + JSON.stringify(data));
    }
  } catch (error) {
    console.error("Signup error:", error);
    alert("Server error. Please try again.");
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "index.html";
}

// ─── Navbar Auth ───────────────────────────────────────────────
function updateNavbar() {
  const nav = document.getElementById("nav-auth");
  if (!nav) return;

  const user = (() => {
    try { return JSON.parse(localStorage.getItem("user")); } catch { return null; }
  })();

  if (user) {
    // Show user avatar initial + name + logout
    const initial = (user.name || user.email || "U")[0].toUpperCase();
    nav.innerHTML = `
      <div class="nav-user">
        <div class="nav-avatar">${initial}</div>
        <span class="nav-username">${user.name || user.email}</span>
        <button class="btn-nav btn-logout" onclick="logout()">Logout</button>
      </div>
    `;
  } else {
    nav.innerHTML = `
      <a href="login.html" class="btn-nav-ghost">Login</a>
      <a href="signup.html" class="btn-nav">Sign Up</a>
    `;
  }
}

// ─── PG Data ────────────────────────────────────────────────────
let PGS = [
  {
    id: 1, name: "Sunrise PG Home", area: "Kahilipara", gender: "girls",
    price: 4500, dist: 0.6, rating: 4.7, reviews: 32,
    tags: ["WiFi", "Food", "AC"],
    amenities: ["🌐 WiFi", "🍽️ 3 Meals/Day", "❄️ AC", "🔒 24/7 Security", "👗 Laundry", "📚 Study Room"],
    desc: "A cozy, women-only PG with home-cooked food, excellent security, and a study room. Just 10 minutes walk from GU main gate. Rooms available on single and double sharing.",
    color: "#1a2a1a", img: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80"
  },
  {
    id: 2, name: "Lotus Boys Hostel", area: "Six Mile", gender: "boys",
    price: 3800, dist: 1.2, rating: 4.3, reviews: 18,
    tags: ["WiFi", "Parking"],
    amenities: ["🌐 WiFi", "🏍️ Parking", "🔒 Security", "💧 24hr Water", "⚡ Power Backup"],
    desc: "Budget-friendly boys hostel near Six Mile with generator backup and safe parking. Monthly, quarterly, and annual plans available.",
    color: "#1a1a2a", img: "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&q=80"
  },
  {
    id: 3, name: "Urban Nest Co-Living", area: "Zoo Road", gender: "co-ed",
    price: 7200, dist: 0.9, rating: 4.8, reviews: 56,
    tags: ["WiFi", "AC", "Food", "Gym"],
    amenities: ["🌐 WiFi", "❄️ AC", "🍽️ Food", "🏋️ Gym", "🛁 Attached Bath", "📺 TV Lounge", "🧺 Laundry"],
    desc: "Modern co-living space with premium amenities. Community events every weekend, high-speed internet, and fully air-conditioned rooms.",
    color: "#2a1a1a", img: "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=800&q=80"
  },
  {
    id: 4, name: "Green Valley PG", area: "Beltola", gender: "girls",
    price: 5000, dist: 1.8, rating: 4.5, reviews: 24,
    tags: ["WiFi", "Laundry", "Food"],
    amenities: ["🌐 WiFi", "🍽️ 2 Meals/Day", "🧺 Laundry", "🌳 Garden", "🔒 Security"],
    desc: "Peaceful PG with a beautiful garden, perfect for students who need a quiet study environment. Home-cooked North and South Indian meals.",
    color: "#1a2a20", img: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80"
  },
  {
    id: 5, name: "Metro Boys PG", area: "Khanapara", gender: "boys",
    price: 3200, dist: 2.1, rating: 4.0, reviews: 12,
    tags: ["WiFi", "Security"],
    amenities: ["🌐 WiFi", "🔒 Security", "💧 Hot Water", "⚡ Power Backup", "🏍️ Parking"],
    desc: "Most affordable PG option near Khanapara. Clean rooms, good internet, and close to the metro stop.",
    color: "#1e1a2a", img: "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80"
  },
  {
    id: 6, name: "The Scholar's Den", area: "Panjabari", gender: "co-ed",
    price: 6500, dist: 0.4, rating: 4.9, reviews: 41,
    tags: ["WiFi", "AC", "Study Hall", "Food"],
    amenities: ["🌐 WiFi", "❄️ AC", "📚 Study Hall", "🍽️ 3 Meals/Day", "🛁 Attached Bath", "🔒 Biometric Entry", "🧺 Laundry"],
    desc: "Scholar's Den is designed for serious students. It has a dedicated 24/7 study hall, biometric entry, and is just 400 metres from the main institute. Rated #1 by students.",
    color: "#2a201a", img: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80"
  },
  {
    id: 7, name: "HomeAway Residency", area: "RG Baruah Rd", gender: "girls",
    price: 4800, dist: 1.5, rating: 4.4, reviews: 29,
    tags: ["WiFi", "AC", "Laundry"],
    amenities: ["🌐 WiFi", "❄️ AC", "🧺 Laundry", "📺 Common TV", "🔒 CCTV", "💧 Hot Water"],
    desc: "Safe, clean, and comfortable accommodation for girls. CCTV on all floors, strict visitor policy, and just 2 minutes from a bus stop.",
    color: "#1a1e2a", img: "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&q=80"
  },
  {
    id: 8, name: "Campus Edge PG", area: "Geetanagar", gender: "boys",
    price: 5500, dist: 0.7, rating: 4.6, reviews: 35,
    tags: ["WiFi", "Food", "AC", "Parking"],
    amenities: ["🌐 WiFi", "🍽️ 2 Meals/Day", "❄️ AC", "🏍️ Parking", "📚 Study Room", "⚡ Power Backup", "🔒 Security"],
    desc: "Premium boys PG right next to campus. Fully furnished rooms, power backup, and delicious food. Popular with engineering students.",
    color: "#1a2428", img: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80"
  }
];

let activeFilter = 'all';
let activePriceFilter = null;

function renderCards(data) {
  const grid = document.getElementById('grid');
  const countLabel = document.getElementById('countLabel');
  if (countLabel) countLabel.textContent = data.length;

  grid.innerHTML = data.map((pg, i) => `
    <div class="pg-card" onclick="openModal(${pg.id})" style="animation-delay:${i * 0.07}s">
      <div class="card-img">
        <img class="card-img-bg" src="${pg.img}" alt="${pg.name}" loading="lazy"/>
        <div class="card-badge">${pg.gender === 'boys' ? '♂ Boys' : pg.gender === 'girls' ? '♀ Girls' : '⚥ Co-ed'}</div>
        <div class="card-save" onclick="event.stopPropagation();savePG(this)">♡</div>
        <div class="card-dist">📍 ${pg.dist} km</div>
      </div>
      <div class="card-body">
        <div class="card-name">${pg.name}</div>
        <div class="card-location">📌 ${pg.area}, Guwahati</div>
        <div class="card-tags">${pg.tags.slice(0, 3).map(t => `<span class="tag">${t}</span>`).join('')}</div>
        <div class="card-footer">
          <div class="price">₹${pg.price.toLocaleString()} <span>/month</span></div>
          <div class="rating"><span class="stars">★</span> ${pg.rating} <span style="color:var(--muted)">(${pg.reviews})</span></div>
        </div>
      </div>
    </div>
  `).join('');
}

function getFiltered() {
  let data = [...PGS];
  const q = document.getElementById('searchInput').value.toLowerCase();
  if (q) data = data.filter(p => p.name.toLowerCase().includes(q) || p.area.toLowerCase().includes(q));
  if (activeFilter !== 'all') data = data.filter(p => p.gender === activeFilter);
  if (activePriceFilter === 'budget') data = data.filter(p => p.price < 5000);
  else if (activePriceFilter === 'mid') data = data.filter(p => p.price >= 5000 && p.price <= 8000);
  else if (activePriceFilter === 'premium') data = data.filter(p => p.price > 8000);
  return data;
}

function filterCards() { renderCards(getFiltered()); }

function setFilter(el, val) {
  document.querySelectorAll('.filter-chip').forEach(c => {
    if (['all', 'boys', 'girls', 'co-ed'].includes(c.dataset.val || c.textContent.trim().toLowerCase())) c.classList.remove('active');
  });
  el.classList.add('active');
  activeFilter = val;
  filterCards();
}

function setPriceFilter(el, val) {
  activePriceFilter = activePriceFilter === val ? null : val;
  el.classList.toggle('active');
  filterCards();
}

function sortCards(val) {
  let data = getFiltered();
  if (val === 'price') data.sort((a, b) => a.price - b.price);
  else if (val === 'rating') data.sort((a, b) => b.rating - a.rating);
  else if (val === 'distance') data.sort((a, b) => a.dist - b.dist);
  renderCards(data);
}

function updateRange(el) {
  document.getElementById('rangeVal').textContent = '₹' + parseInt(el.value).toLocaleString();
}
function updateDist(el) {
  document.getElementById('distVal').textContent = parseFloat(el.value).toFixed(1) + ' km';
}

function openModal(id) {
  const pg = PGS.find(p => p.id === id);
  document.getElementById('modalImg').src = pg.img;
  document.getElementById('modalName').textContent = pg.name;
  document.getElementById('modalLoc').textContent = `📌 ${pg.area}, Guwahati — ${pg.dist} km from campus`;
  document.getElementById('modalStats').innerHTML = `
    <div class="modal-stat"><div class="modal-stat-val">₹${pg.price.toLocaleString()}</div><div class="modal-stat-key">Per Month</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.rating} ★</div><div class="modal-stat-key">${pg.reviews} Reviews</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.dist} km</div><div class="modal-stat-key">From Campus</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.gender === 'co-ed' ? 'Co-ed' : pg.gender === 'boys' ? 'Boys' : 'Girls'}</div><div class="modal-stat-key">Type</div></div>
  `;
  document.getElementById('modalAmenities').innerHTML = pg.amenities.map(a => `<div class="amenity">${a}</div>`).join('');
  document.getElementById('modalDesc').textContent = pg.desc;
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(e) {
  if (e.target === document.getElementById('modal')) closeModalDirect();
}
function closeModalDirect() {
  document.getElementById('modal').classList.remove('open');
  document.body.style.overflow = '';
}

function savePG(el) {
  el.textContent = el.textContent === '♡' ? '♥' : '♡';
  el.style.color = el.textContent === '♥' ? '#ff6b4a' : '';
  showToast(el.textContent === '♥' ? '❤️ Added to saved!' : '💔 Removed from saved');
}

let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  document.getElementById('toastMsg').textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2800);
}

// ─── Init ────────────────────────────────────────────────────────
async function loadPGs() {
  try {
    const res = await fetch("https://pg-finder-production.up.railway.app/api/v1/pgs");
    const data = await res.json();
    PGS = data.items.map(pg => ({
      id: pg.id,
      name: pg.name,
      area: pg.area,
      gender: pg.gender_type,
      price: parseFloat(pg.price),

      latitude: pg.latitude,      // ✅ ADD THIS
      longitude: pg.longitude,    // ✅ ADD THIS

      dist: 0.5,
      rating: pg.rating,
      reviews: pg.total_reviews,
      tags: ["WiFi"],
      amenities: [],
      desc: pg.description || "No description",
      img: "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80"
    }));
    renderCards(PGS);
  } catch (err) {
    // fallback to static data silently
    renderCards(PGS);
  }
}

if (document.getElementById("grid")) {
  loadPGs();
}
updateNavbar();

let map;

function showMapView() {
  console.log("MAP CLICKED");

  const listings = document.querySelector(".listings");
  const sidebar = document.querySelector(".sidebar");
  const mapDiv = document.getElementById("map");

  // Hide sidebar + listings
  if (listings) listings.style.display = "none";
  if (sidebar) sidebar.style.display = "none";

  // Show map full width
  mapDiv.style.display = "block";
  mapDiv.style.width = "100%";

  setTimeout(() => {
    if (!map) {
      initMap();
    } else {
      map.invalidateSize();
    }
  }, 100);
}

function showListView() {
  const listings = document.querySelector(".listings");
  const sidebar = document.querySelector(".sidebar");
  const mapDiv = document.getElementById("map");

  if (listings) listings.style.display = "block";
  if (sidebar) sidebar.style.display = "block";

  mapDiv.style.display = "none";
}
function initMap() {
  map = L.map('map').setView([26.1445, 91.7362], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  addMarkers();
}
function addMarkers() {
  if (!PGS || PGS.length === 0) {
    console.warn("No PG data available");
    return;
  }

  PGS.forEach(pg => {
    if (!pg.latitude || !pg.longitude) return;

    L.marker([pg.latitude, pg.longitude])
      .addTo(map)
      .bindPopup(`<b>${pg.name}</b><br>₹${pg.price}`);
  });
}
