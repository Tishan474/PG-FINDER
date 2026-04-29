const API = "https://pg-finder-production.up.railway.app";
 
// ─── Auth ────────────────────────────────────────────────────────
async function loginUser(email, password) {
  try {
    const res  = await fetch(`${API}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.status === 200) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      alert("Login successful");
      window.location.href = "index.html";
    } else {
      alert("Login failed: " + JSON.stringify(data));
    }
  } catch (err) { console.error("Login error:", err); alert("Server error"); }
}
 
function handleLogin() {
  const email    = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  if (!email || !password) { alert("Enter email and password"); return; }
  loginUser(email, password);
}
 
function handleRegister() {
  const name     = document.getElementById("name").value.trim();
  const email    = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  if (!name || !email || !password) { alert("Fill all fields"); return; }
  registerUser(name, email, password);
}
 
async function registerUser(name, email, password) {
  try {
    const res  = await fetch(`${API}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password, role: "user" })
    });
    const data = await res.json();
    if (res.status === 200 || res.status === 201) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      alert("Signup successful");
      window.location.href = "index.html";
    } else {
      alert("Signup failed: " + JSON.stringify(data));
    }
  } catch (error) { console.error("Signup error:", error); alert("Server error"); }
}
 
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "index.html";
}
 
// ─── Navbar ──────────────────────────────────────────────────────
function updateNavbar() {
  const nav = document.getElementById("nav-auth");
  if (!nav) return;
  const user = (() => { try { return JSON.parse(localStorage.getItem("user")); } catch { return null; } })();
  if (user) {
    const initial = (user.name || user.email || "U")[0].toUpperCase();
    nav.innerHTML = `
      <div class="nav-user">
        <div class="nav-avatar">${initial}</div>
        <span class="nav-username">${user.name || user.email}</span>
        <button class="btn-nav btn-logout" onclick="logout()">Logout</button>
      </div>`;
  } else {
    nav.innerHTML = `
      <a href="login.html" class="btn-nav-ghost">Login</a>
      <a href="signup.html" class="btn-nav">Sign Up</a>`;
  }
}
 
// ─── PG Data ─────────────────────────────────────────────────────
let PGS = [];
 
const FALLBACK_PGS = [
  { id:1, name:"Sunrise PG Home", area:"Kahilipara", gender:"girls", price:4500, dist:0.6, rating:4.7, reviews:32, latitude:26.1234, longitude:91.7456, tags:["WiFi","Food","AC"], amenities:["🌐 WiFi","🍽️ 3 Meals/Day","❄️ AC","🔒 24/7 Security"], desc:"A cozy, women-only PG with home-cooked food and excellent security.", img:"https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80" },
  { id:2, name:"Lotus Boys Hostel", area:"Six Mile", gender:"boys", price:3800, dist:1.2, rating:4.3, reviews:18, latitude:26.1320, longitude:91.7520, tags:["WiFi","Parking"], amenities:["🌐 WiFi","🏍️ Parking","🔒 Security"], desc:"Budget-friendly boys hostel near Six Mile.", img:"https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&q=80" },
  { id:3, name:"Urban Nest Co-Living", area:"Zoo Road", gender:"co-ed", price:7200, dist:0.9, rating:4.8, reviews:56, latitude:26.1500, longitude:91.7600, tags:["WiFi","AC","Food","Gym"], amenities:["🌐 WiFi","❄️ AC","🍽️ Food","🏋️ Gym"], desc:"Modern co-living space with premium amenities.", img:"https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=800&q=80" },
  { id:4, name:"Green Valley PG", area:"Beltola", gender:"girls", price:5000, dist:1.8, rating:4.5, reviews:24, latitude:26.1180, longitude:91.7380, tags:["WiFi","Laundry","Food"], amenities:["🌐 WiFi","🍽️ 2 Meals/Day","🧺 Laundry"], desc:"Peaceful PG with a beautiful garden.", img:"https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80" },
  { id:5, name:"Metro Boys PG", area:"Khanapara", gender:"boys", price:3200, dist:2.1, rating:4.0, reviews:12, latitude:26.1100, longitude:91.7700, tags:["WiFi","Security"], amenities:["🌐 WiFi","🔒 Security"], desc:"Most affordable PG option near Khanapara.", img:"https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80" },
  { id:6, name:"The Scholar's Den", area:"Panjabari", gender:"co-ed", price:6500, dist:0.4, rating:4.9, reviews:41, latitude:26.1600, longitude:91.7450, tags:["WiFi","AC","Study Hall"], amenities:["🌐 WiFi","❄️ AC","📚 Study Hall"], desc:"Designed for serious students with a 24/7 study hall.", img:"https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80" },
  { id:7, name:"HomeAway Residency", area:"RG Baruah Rd", gender:"girls", price:4800, dist:1.5, rating:4.4, reviews:29, latitude:26.1400, longitude:91.7300, tags:["WiFi","AC","Laundry"], amenities:["🌐 WiFi","❄️ AC","🧺 Laundry"], desc:"Safe and comfortable accommodation for girls.", img:"https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&q=80" },
  { id:8, name:"Campus Edge PG", area:"Geetanagar", gender:"boys", price:5500, dist:0.7, rating:4.6, reviews:35, latitude:26.1350, longitude:91.7480, tags:["WiFi","Food","AC","Parking"], amenities:["🌐 WiFi","🍽️ 2 Meals/Day","❄️ AC","🏍️ Parking"], desc:"Premium boys PG right next to campus.", img:"https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80" }
];
 
// ─── Load PGs from backend ────────────────────────────────────────
async function loadPGs() {
  try {
    const res  = await fetch(`${API}/api/v1/pgs`, { cache: 'no-store' });
    const data = await res.json();

    if (!data.items || data.items.length === 0) {
      PGS = FALLBACK_PGS;
      renderCards(PGS);

      // ✅ ADD THIS
      if (map) addMarkers();

      return;
    }

    PGS = data.items.map(pg => ({
      id:        pg.id,
      name:      pg.name,
      area:      pg.area,
      gender:    pg.gender_type,
      price:     parseFloat(pg.price) || 0,
      dist:      pg.distance_km || 0.5,
      rating:    parseFloat(pg.rating) || 0,
      reviews:   pg.total_reviews || 0,

      // ✅ KEEP THIS (GOOD)
      latitude:  Number(pg.latitude),
      longitude: Number(pg.longitude),

      phone:     pg.phone || '',
      tags:      pg.amenities?.map(a => a.name).slice(0, 4) || ["WiFi"],
      amenities: pg.amenities?.map(a => `🏠 ${a.name}`) || [],
      desc:      pg.description || "No description provided.",
      img: (pg.photos && pg.photos.length > 0)
           ? pg.photos[0]
           : "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80"
    }));

    renderCards(PGS);

    // ✅ ADD THIS (MOST IMPORTANT LINE)
    if (map) addMarkers();

  } catch (err) {
    console.warn("Backend unavailable, using sample data:", err);
    PGS = FALLBACK_PGS;
    renderCards(PGS);

    // ✅ ADD THIS
    if (map) addMarkers();
  }
}
 
// ─── Render cards ─────────────────────────────────────────────────
function renderCards(data) {
  const grid       = document.getElementById('grid');
  const countLabel = document.getElementById('countLabel');
  if (!grid) return;
  if (countLabel) countLabel.textContent = data.length;
 
  if (data.length === 0) {
    grid.innerHTML = `<div style="color:var(--muted);padding:40px;text-align:center;grid-column:1/-1;">No PGs found.</div>`;
    return;
  }
 
  grid.innerHTML = data.map((pg, i) => `
    <div class="pg-card" onclick="openModal(${pg.id})" style="animation-delay:${i * 0.07}s">
      <div class="card-img">
        <img class="card-img-bg" src="${pg.img}" alt="${pg.name}" loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80'"/>
        <div class="card-badge">${pg.gender === 'boys' ? '♂ Boys' : pg.gender === 'girls' ? '♀ Girls' : '⚥ Co-ed'}</div>
        <div class="card-save" onclick="event.stopPropagation();savePG(this)">♡</div>
        <div class="card-dist">📍 ${pg.dist} km</div>
      </div>
      <div class="card-body">
        <div class="card-name">${pg.name}</div>
        <div class="card-location">📌 ${pg.area}, Guwahati</div>
        <div class="card-tags">${(pg.tags||[]).slice(0,3).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
        <div class="card-footer">
          <div class="price">₹${Number(pg.price).toLocaleString()} <span>/month</span></div>
          <div class="rating"><span class="stars">★</span> ${pg.rating} <span style="color:var(--muted)">(${pg.reviews})</span></div>
        </div>
      </div>
    </div>
  `).join('');
}
 
// ─── Filters & Sort ───────────────────────────────────────────────
let activeFilter      = 'all';
let activePriceFilter = null;
 
function getFiltered() {
  let data = [...PGS];
  const q = (document.getElementById('searchInput')?.value || '').toLowerCase();
  if (q) data = data.filter(p => p.name.toLowerCase().includes(q) || p.area.toLowerCase().includes(q));
  if (activeFilter !== 'all') data = data.filter(p => p.gender === activeFilter);
  if (activePriceFilter === 'budget')  data = data.filter(p => p.price < 5000);
  else if (activePriceFilter === 'mid') data = data.filter(p => p.price >= 5000 && p.price <= 8000);
  else if (activePriceFilter === 'premium') data = data.filter(p => p.price > 8000);
  return data;
}
 
function filterCards() { renderCards(getFiltered()); }
 
function setFilter(el, val) {
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
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
  if (val === 'price')    data.sort((a,b) => a.price - b.price);
  else if (val === 'rating')   data.sort((a,b) => b.rating - a.rating);
  else if (val === 'distance') data.sort((a,b) => a.dist - b.dist);
  renderCards(data);
}
 
function updateRange(el) { document.getElementById('rangeVal').textContent = '₹' + parseInt(el.value).toLocaleString(); }
function updateDist(el)  { document.getElementById('distVal').textContent  = parseFloat(el.value).toFixed(1) + ' km'; }
 
// ─── Modal ────────────────────────────────────────────────────────
function openModal(id) {
  const pg = PGS.find(p => p.id === id);
  if (!pg) return;
  document.getElementById('modalImg').src = pg.img;
  document.getElementById('modalName').textContent = pg.name;
  document.getElementById('modalLoc').textContent  = `📌 ${pg.area}, Guwahati — ${pg.dist} km from campus`;
  document.getElementById('modalStats').innerHTML  = `
    <div class="modal-stat"><div class="modal-stat-val">₹${Number(pg.price).toLocaleString()}</div><div class="modal-stat-key">Per Month</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.rating} ★</div><div class="modal-stat-key">${pg.reviews} Reviews</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.dist} km</div><div class="modal-stat-key">From Campus</div></div>
    <div class="modal-stat"><div class="modal-stat-val">${pg.gender === 'co-ed' ? 'Co-ed' : pg.gender === 'boys' ? 'Boys' : 'Girls'}</div><div class="modal-stat-key">Type</div></div>
  `;
  document.getElementById('modalAmenities').innerHTML = (pg.amenities||[]).map(a=>`<div class="amenity">${a}</div>`).join('');
  document.getElementById('modalDesc').textContent = pg.desc;
 
  // ✅ Contact Owner — show phone + WhatsApp button
  const ctaDiv = document.getElementById('modalCta');
  if (ctaDiv) {
    if (pg.phone) {
      const cleanPhone = pg.phone.replace(/[\s\-\+]/g, '');
      const waNumber   = cleanPhone.startsWith('91') ? cleanPhone : '91' + cleanPhone;
      ctaDiv.innerHTML = `
        <div style="
          background:var(--tag-bg);border:1px solid var(--border);
          border-radius:12px;padding:14px 18px;margin-bottom:14px;
          display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
          <div>
            <div style="font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">Owner Contact</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:var(--accent);">📞 ${pg.phone}</div>
          </div>
          <a href="https://wa.me/${waNumber}" target="_blank" style="
            background:#25D366;color:#fff;
            padding:10px 18px;border-radius:10px;
            font-weight:700;font-size:0.88rem;
            text-decoration:none;display:inline-flex;
            align-items:center;gap:6px;transition:opacity 0.2s;"
            onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 0C5.373 0 0 5.373 0 12c0 2.125.555 4.122 1.528 5.855L.057 23.882l6.233-1.635A11.945 11.945 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.894a9.86 9.86 0 01-5.031-1.378l-.361-.214-3.741.981.999-3.648-.235-.374A9.861 9.861 0 012.106 12C2.106 6.58 6.58 2.106 12 2.106S21.894 6.58 21.894 12 17.42 21.894 12 21.894z"/></svg>
            WhatsApp
          </a>
        </div>
        <button class="btn-secondary" onclick="showToast('❤️ Saved to wishlist!')">Save to Wishlist</button>
      `;
    } else {
      ctaDiv.innerHTML = `
        <button class="btn-primary" onclick="showToast('📞 Contact request sent!')">Contact Owner</button>
        <button class="btn-secondary" onclick="showToast('❤️ Saved to wishlist!')">Save</button>
      `;
    }
  }
 
  document.getElementById('modal').classList.add('open');
  document.body.style.overflow = 'hidden';
}
 
function closeModal(e)   { if (e.target === document.getElementById('modal')) closeModalDirect(); }
function closeModalDirect() { document.getElementById('modal').classList.remove('open'); document.body.style.overflow = ''; }
 
// ─── Save ─────────────────────────────────────────────────────────
function savePG(el) {
  el.textContent = el.textContent === '♡' ? '♥' : '♡';
  el.style.color = el.textContent === '♥' ? '#ff6b4a' : '';
  showToast(el.textContent === '♥' ? '❤️ Added to saved!' : '💔 Removed from saved');
}
 
// ─── Toast ────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  document.getElementById('toastMsg').textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2800);
}
 
// ─── Map View ─────────────────────────────────────────────────────
let mapInstance = null;
let mapMarkers  = [];
 
function showMapView() {
  document.getElementById('heroSection') .style.display = 'none';
  document.getElementById('statsSection').style.display = 'none';
  document.getElementById('mainSection') .style.display = 'none';
  document.getElementById('map')         .style.display = 'block';
 
  setTimeout(() => {
    if (!mapInstance) {
      mapInstance = L.map('map').setView([26.1445, 91.7362], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(mapInstance);
    } else {
      mapInstance.invalidateSize();
    }
    loadMapMarkers();
  }, 100);
}
 
function showListView() {
  document.getElementById('heroSection') .style.display = '';
  document.getElementById('statsSection').style.display = '';
  document.getElementById('mainSection') .style.display = '';
  document.getElementById('map')         .style.display = 'none';
}
 
async function loadMapMarkers() {
  mapMarkers.forEach(m => m.remove());
  mapMarkers = [];

  let pgs = [];

  try {
    // ❌ REMOVE /map endpoint
    const res  = await fetch(`${API}/api/v1/pgs`, { cache: 'no-store' });
    const data = await res.json();

    pgs = data.items || [];

  } catch (err) {
    console.warn("API failed, using local PGS:", err);
    pgs = PGS;
  }

  if (!pgs || pgs.length === 0) {
    showToast('⚠️ No PGs found on map.');
    return;
  }

  const bounds = [];

  pgs.forEach(pg => {
    const lat = Number(pg.latitude);
    const lng = Number(pg.longitude);

    if (isNaN(lat) || isNaN(lng)) return;

    const marker = L.marker([lat, lng])
      .addTo(mapInstance)
      .bindPopup(`<b>${pg.name}</b><br>₹${parseInt(pg.price).toLocaleString()}`);

    mapMarkers.push(marker);
    bounds.push([lat, lng]);
  });

  if (bounds.length > 0) {
    mapInstance.fitBounds(bounds, { padding: [40, 40] });
  }
}
 
  const bounds = [];
 
  pgs.forEach(pg => {
    if (!pg.latitude || !pg.longitude) return;
 
    const colour = pg.gender_type === 'boys'  ? '#4a90e2'
                 : pg.gender_type === 'girls' ? '#e24a7a'
                 : '#f7c753';
 
    const icon = L.divIcon({
      className: '',
      html: `
        <div style="background:${colour};color:#0d0f14;font-family:'Syne',sans-serif;
          font-weight:800;font-size:11px;padding:5px 9px;border-radius:20px;
          white-space:nowrap;box-shadow:0 3px 12px rgba(0,0,0,0.4);
          border:2px solid rgba(255,255,255,0.2);">
          ₹${parseInt(pg.price).toLocaleString()}
        </div>
        <div style="width:0;height:0;border-left:6px solid transparent;
          border-right:6px solid transparent;border-top:8px solid ${colour};
          margin:0 auto;"></div>`,
      iconAnchor:  [30, 38],
      popupAnchor: [0, -38],
    });
 
    const photoHtml = pg.cover_photo
      ? `<img src="${pg.cover_photo}" style="width:100%;height:100px;object-fit:cover;border-radius:8px;margin-bottom:8px;" onerror="this.style.display='none'"/>`
      : '';
 
    const genderLabel = pg.gender_type === 'boys' ? '♂ Boys'
                      : pg.gender_type === 'girls' ? '♀ Girls' : '⚥ Co-ed';
 
    const popup = `
      <div style="font-family:'DM Sans',sans-serif;min-width:190px;">
        ${photoHtml}
        <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:13px;margin-bottom:3px;">${pg.name}</div>
        <div style="color:#6b7280;font-size:11px;margin-bottom:8px;">📌 ${pg.area}, ${pg.city}</div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-weight:800;font-size:14px;color:#f7c753;">
            ₹${parseInt(pg.price).toLocaleString()}
            <span style="font-size:10px;font-weight:400;color:#6b7280;">/mo</span>
          </span>
          <span style="font-size:11px;color:#6b7280;">${genderLabel} · ★ ${pg.rating}</span>
        </div>
        <button onclick="showListView()" style="margin-top:10px;width:100%;background:#f7c753;
          color:#0d0f14;border:none;border-radius:8px;padding:7px;font-weight:700;
          font-size:12px;cursor:pointer;">View Listings →</button>
      </div>`;
 
    const marker = L.marker([pg.latitude, pg.longitude], { icon })
      .addTo(mapInstance)
      .bindPopup(popup, { maxWidth: 220 });
 
    mapMarkers.push(marker);
    bounds.push([pg.latitude, pg.longitude]);
  });
 
  if (bounds.length > 0) {
    mapInstance.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    showToast(`🗺️ ${pgs.length} PG${pgs.length !== 1 ? 's' : ''} on map`);
  }
}
 
// ─── create-pg.html functions ─────────────────────────────────────
function selectGender(el) {
  document.querySelectorAll('.gender-pill').forEach(p => p.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('gender').value = el.dataset.val;
}
 
(function checkAuth() {
  if (!document.getElementById('authGuard')) return;
  const token = localStorage.getItem('token');
  if (!token) {
    document.getElementById('authGuard').classList.add('show');
    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.disabled = true;
      btn.style.opacity = '0.45';
      btn.style.cursor = 'not-allowed';
      document.getElementById('submitLabel').textContent = 'Login required to publish';
    }
  }
})();
 
function showErr(id, show) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('show', show);
}
 
async function handleSubmitPG(e) {
  e.preventDefault();

  const token = localStorage.getItem('token');
  if (!token) {
    showToast('⚠️ Please log in first.');
    return;
  }

  const name      = document.getElementById('name').value.trim();
  const area      = document.getElementById('area').value.trim();
  const city      = document.getElementById('city').value.trim();
  const phone     = document.getElementById('phone')?.value.trim() || '';
  const price     = parseFloat(document.getElementById('price').value);
  const latitude  = parseFloat(document.getElementById('latitude').value);
  const longitude = parseFloat(document.getElementById('longitude').value);
  const gender    = document.getElementById('gender').value;
  const desc      = document.getElementById('description').value.trim();

  // Basic validation
  if (!name || !area || !city || !price || isNaN(latitude) || isNaN(longitude)) {
    showToast('⚠️ Please fill all required fields correctly.');
    return;
  }

  const btn   = document.getElementById('submitBtn');
  const label = document.getElementById('submitLabel');

  btn.classList.add('loading');
  label.textContent = 'Publishing…';

  // ✅ JSON DATA (FIXES 422 ERROR)
  const data = {
    name: name,
    area: area,
    city: city,
    phone: phone,
    price: price,
    latitude: latitude,
    longitude: longitude,
    gender_type: gender,
    description: desc,

    // ✅ REQUIRED
    amenity_ids: []
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
      showToast('🎉 PG listed successfully!');
      setTimeout(() => window.location.href = 'index.html', 1500);
    } else {
      console.error(result);
      showToast('❌ ' + (result.detail || JSON.stringify(result)));
      btn.classList.remove('loading');
      label.textContent = 'Publish PG Listing →';
    }

  } catch (err) {
    console.error(err);
    showToast('❌ Server error. Try again.');
    btn.classList.remove('loading');
    label.textContent = 'Publish PG Listing →';
  }
}
 
// ─── Photo upload (create-pg.html) ───────────────────────────────
const MAX_PHOTOS  = 8;
const MAX_SIZE_MB = 5;
let uploadedPhotos = [];
 
function handleDragOver(e)  { e.preventDefault(); document.getElementById('dropZone')?.classList.add('drag-over'); }
function handleDragLeave(e) { document.getElementById('dropZone')?.classList.remove('drag-over'); }
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropZone')?.classList.remove('drag-over');
  processFiles(Array.from(e.dataTransfer.files));
}
function handleFileSelect(e) { processFiles(Array.from(e.target.files)); e.target.value = ''; }
 
function processFiles(files) {
  const allowed   = ['image/jpeg','image/png','image/webp','image/gif'];
  const remaining = MAX_PHOTOS - uploadedPhotos.length;
  if (remaining <= 0) { showToast('⚠️ Maximum 8 photos allowed.'); return; }
 
  files.slice(0, remaining).forEach(file => {
    if (!allowed.includes(file.type)) { showToast('⚠️ Only JPG, PNG, WEBP allowed.'); return; }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) { showToast(`⚠️ "${file.name}" exceeds 5 MB.`); return; }
    const reader = new FileReader();
    reader.onload = (ev) => { uploadedPhotos.push({ file, dataUrl: ev.target.result }); renderPreviews(); };
    reader.readAsDataURL(file);
  });
}
 
function renderPreviews() {
  const grid       = document.getElementById('photoPreviewGrid');
  const countLabel = document.getElementById('photoCountLabel');
  const countNum   = document.getElementById('photoCountNum');
  if (!grid) return;
 
  grid.innerHTML = '';
  uploadedPhotos.forEach((photo, index) => {
    const item = document.createElement('div');
    item.className = 'preview-item';
    item.innerHTML = `
      <img src="${photo.dataUrl}" alt="PG photo ${index + 1}" />
      ${index === 0 ? '<span class="preview-badge">Cover</span>' : ''}
      <button class="preview-remove" onclick="removePhoto(${index})" title="Remove">✕</button>`;
    grid.appendChild(item);
  });
 
  if (countLabel) countLabel.style.display = uploadedPhotos.length > 0 ? 'block' : 'none';
  if (countNum)   countNum.textContent = uploadedPhotos.length;
}
 
function removePhoto(index) {
  uploadedPhotos.splice(index, 1);
  renderPreviews();
  showToast('🗑️ Photo removed.');
}
 
// ─── Init ─────────────────────────────────────────────────────────
if (document.getElementById("grid")) loadPGs();
updateNavbar();

