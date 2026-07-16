/* Nexus Mock App — Full Interactive Flows */
function render(view) {
  const app = document.getElementById('app');
  if (view === 'login') return renderLogin(app);
  app.innerHTML = renderShell() + '<div id="toastContainer" class="toast-container"></div><div id="modalOverlay" class="modal-overlay"></div>';
  document.querySelector('#app-content').innerHTML = renderContent(view);
  setupSidebar();
  setupBranchSwitch();
}

/* ── Shell ── */
function renderShell() {
  const nav = [
    ['dashboard','📊','Dashboard'],
    ['appointments','📅','Programari'],
    ['jobs','🔧','Interventii'],
    ['customers','👥','Clienti'],
    ['invoices','📄','Facturi'],
  ];
  const links = nav.map(([id,icon,label]) => `<li><a href="#${id}" class="${currentView===id?'active':''}" data-nav="${id}"><span class="icon">${icon}</span>${label}</a></li>`).join('');
  const branchOpts = currentBranch.isInstitution
    ? '<option value="'+currentBranch.id+'">'+currentBranch.name+' (Toate)</option>' +
      currentBranch.children.map(id => '<option value="'+id+'">'+BRANCHES[id].name+'</option>').join('')
    : '<option value="'+currentBranch.id+'">'+currentBranch.name+'</option>';
  return `
    <div class="app-shell" id="appShell">
      <aside class="sidebar">
        <div class="sidebar-logo">Nex<span>u</span>s</div>
        <ul class="sidebar-nav">${links}</ul>
      </aside>
      <div class="main">
        <header class="topbar">
          <div class="topbar-left">
            <select class="branch-select" id="branchSwitch">${branchOpts}</select>
            <span class="branch-label" style="font-size:.8rem;color:var(--text-secondary)">${currentUser.role === 'Tehnician' ? 'Interventiile mele' : currentBranch.isInstitution ? 'Toate locatiile' : currentBranch.name}</span>
          </div>
          <div class="topbar-right">
            <span style="font-size:.8rem;color:var(--text-secondary)">${currentUser.role}</span>
            <div class="user-badge" style="cursor:pointer" onclick="showUserMenu()"><div class="avatar">${currentUser.initials}</div>${currentUser.name}</div>
          </div>
        </header>
        <div class="content" id="app-content"></div>
      </div>
    </div>`;
}

function setupSidebar() {
  document.querySelectorAll('[data-nav]').forEach(link => {
    link.addEventListener('click', function(e) { e.preventDefault(); navigate(this.dataset.nav); });
  });
}
function setupBranchSwitch() {
  const sel = document.getElementById('branchSwitch');
  if (sel) sel.addEventListener('change', function() { currentBranch = BRANCHES[this.value]; navigate(currentView); });
}

/* ── Login ── */
function renderLogin(app) {
  app.innerHTML = `
    <div class="login-page">
      <div class="login-card">
        <h1>Nexus</h1>
        <p class="subtitle">Business Management Platform</p>
        <form id="loginForm" onsubmit="handleLogin(event)">
          <div class="form-group">
            <label>Email</label>
            <input class="form-input" type="email" id="loginEmail" value="demo@nexus.local" required>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input class="form-input" type="password" id="loginPass" value="password" required>
          </div>
          <div class="form-group">
            <label>Login as</label>
            <select class="form-input" id="loginRole">
              <option value="owner">Andrei Popescu — Admin (vede tot)</option>
              <option value="manager">Maria Ionescu — Manager (sucursala)</option>
              <option value="tech">Ion Vasilescu — Tehnician (job-urile mele)</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:8px">Sign In</button>
        </form>
        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border);font-size:.75rem;color:var(--text-secondary);text-align:center">
          Mock Preview — ADR-0012 · Toate datele sunt simulate
        </div>
      </div>
    </div>`;
}
function handleLogin(e) {
  e.preventDefault();
  const role = document.getElementById('loginRole').value;
  currentUser = USERS[role];
  currentBranch = BRANCHES[role === 'tech' ? 'branch-1' : 'inst-1'];
  navigate('dashboard');
  toast('Bun venit, ' + currentUser.name + '!');
}

/* ── Routing ── */
function renderContent(view) {
  switch(view) {
    case 'dashboard': return renderDashboard();
    case 'appointments': return renderAppointments();
    case 'jobs': return renderJobs();
    case 'customers': return renderCustomers();
    case 'invoices': return renderInvoices();
    default: return '<div class="empty-state"><div class="icon">🔍</div><p>Pagina nu a fost gasita</p></div>';
  }
}

/* ════════════════════════════════════════════
   DASHBOARD
   ════════════════════════════════════════════ */
function renderDashboard() {
  const filtered = getFilteredAppts();
  const today = filtered.filter(a => a.date === '2026-07-16');
  const totalRevenue = INVOICES.filter(i => i.status === 'paid').reduce((s,i) => s+i.amount, 0);
  const unpaid = INVOICES.filter(i => i.status === 'unpaid').reduce((s,i) => s+i.amount, 0);
  const todayCount = today.length;
  const todayRevenue = today.reduce((s,a) => s+a.price, 0);

  return `
    <div class="page-header">
      <h2>Dashboard</h2>
      <span style="color:var(--text-secondary)">${new Date().toLocaleDateString('ro-RO',{weekday:'long',day:'numeric',month:'long',year:'numeric'})}</span>
    </div>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Programari azi</div>
        <div class="kpi-value">${todayCount}</div>
        <div class="kpi-sub" style="color:${todayCount > 2 ? 'var(--success)' : 'var(--error)'}">Valoare: ${todayRevenue} RON</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Venituri luna</div>
        <div class="kpi-value">${(totalRevenue/1000).toFixed(0)}k RON</div>
        <div class="kpi-sub">+12% vs luna trecuta</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Facturi neincasate</div>
        <div class="kpi-value">${(unpaid/1000).toFixed(1)}k RON</div>
        <div class="kpi-sub" style="color:var(--error)">${INVOICES.filter(i=>i.status==='unpaid').length} facturi</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Clienti activi</div>
        <div class="kpi-value">${CUSTOMERS.length}</div>
        <div class="kpi-sub">+${CUSTOMERS.filter(c=>c.createdAt>'2026-06-01').length} luna aceasta</div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">
      <div class="kpi-card">
        <div class="kpi-label">eFactura — azi</div>
        <div class="kpi-value" style="font-size:1.2rem">${INVOICES.filter(i=>i.eFactura==='transmisa').length} transmise</div>
        <div class="kpi-sub" style="color:var(--warning)">${INVOICES.filter(i=>i.eFactura==='neinviata').length} neinviate</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Programari saptamana</div>
        <div class="kpi-value" style="font-size:1.2rem">${filtered.length}</div>
        <div class="kpi-sub">${filtered.filter(a=>a.status==='done').length} finalizate</div>
      </div>
    </div>
    <h3 style="margin-bottom:12px">Programari Azi</h3>
    ${today.length === 0 ? '<div class="empty-state"><p>Nicio programare pentru azi</p></div>' : renderTable(
      ['Client','Serviciu','Ora','Tehnician','Status','Pret'],
      today.map(a => [`<strong onclick="showApptDetail('${a.id}')" style="cursor:pointer;color:var(--primary)">${a.customer}</strong>`, a.service, a.time, a.tech, statusBadge(a.status), a.price+' RON'])
    )}`;
}

/* ════════════════════════════════════════════
   APPOINTMENTS — Full CRUD + Search + Filter
   ════════════════════════════════════════════ */
function renderAppointments() {
  const filtered = getFilteredAppts();
  const filteredBySearch = filterData(filtered);
  return `
    <div class="page-header"><h2>Programari</h2><button class="btn btn-primary btn-sm" onclick="showApptForm()">+ Programare noua</button></div>
    <div class="search-bar">
      <input class="form-input" type="text" placeholder="Cauta client, serviciu, tehnician..." value="${searchQuery}" oninput="searchQuery=this.value;refreshContent()" id="apptSearch">
      <div class="badge-filters">
        ${['all','pending','confirmed','done'].map(s => `<span class="filter-badge ${statusFilter===s?'active':''}" onclick="statusFilter='${s}';document.getElementById('apptSearch').focus();refreshContent()">${s==='all'?'Toate':s}</span>`).join('')}
      </div>
    </div>
    ${filteredBySearch.length === 0 ? '<div class="empty-state"><div class="icon">📅</div><p>Nicio programare gasita</p></div>' : renderTable(
      ['Client','Serviciu','Data','Ora','Tehnician','Status','Pret',''],
      filteredBySearch.map(a => [`<strong onclick="showApptDetail('${a.id}')" style="cursor:pointer;color:var(--primary)">${a.customer}</strong>`, a.service, a.date, a.time, a.tech, statusBadge(a.status), a.price+' RON',
        `<button class="btn btn-sm btn-outline" onclick="showApptDetail('${a.id}')">👁</button>`])
    )}`;
}

function showApptDetail(id) {
  const a = APPOINTMENTS.find(x => x.id === id);
  if (!a) return;
  const cust = CUSTOMERS.find(c => c.id === a.customerId);
  openModal(`
    <h3>Detalii Programare</h3>
    <div class="detail-grid">
      <div class="detail-field"><label>Client</label><span>${a.customer}</span></div>
      <div class="detail-field"><label>Status</label><span>${statusBadge(a.status)}</span></div>
      <div class="detail-field"><label>Serviciu</label><span>${a.service}</span></div>
      <div class="detail-field"><label>Tehnician</label><span>${a.tech}</span></div>
      <div class="detail-field"><label>Data</label><span>${a.date}</span></div>
      <div class="detail-field"><label>Ora</label><span>${a.time} (${a.duration})</span></div>
      <div class="detail-field"><label>Pret</label><span>${a.price} RON</span></div>
      <div class="detail-field"><label>Locatie</label><span>${cust ? cust.address : '-'}</span></div>
      <div class="detail-field" style="grid-column:1/-1"><label>Telefon client</label><span>${cust ? cust.phone : '-'}</span></div>
      <div class="detail-field" style="grid-column:1/-1"><label>Note</label><span>${a.notes || '—'}</span></div>
    </div>
    <div class="modal-actions">
      ${a.status !== 'done' ? `<button class="btn btn-primary btn-sm" onclick="completeAppt('${a.id}')">✓ Finalizat</button>` : ''}
      ${a.status === 'pending' ? `<button class="btn btn-outline btn-sm" onclick="confirmAppt('${a.id}')">✓ Confirma</button>` : ''}
      ${a.status === 'confirmed' ? `<button class="btn btn-outline btn-sm" onclick="changeTech('${a.id}')">🔄 Schimba tehnician</button>` : ''}
      <button class="btn btn-outline btn-sm" onclick="showApptForm('${a.id}')">✏️ Editeaza</button>
      <button class="btn btn-outline btn-sm" onclick="closeModal(); deleteAppt('${a.id}')">🗑️ Sterge</button>
    </div>
  `);
}

function showApptForm(id) {
  const a = id ? APPOINTMENTS.find(x => x.id === id) : null;
  const isEdit = !!a;
  openModal(`
    <h3>${isEdit ? 'Editeaza' : 'Programare Noua'}</h3>
    <form onsubmit="saveAppt(event, '${id||''}')">
      <div class="form-group"><label>Client</label>
        <select class="form-input" id="f_customer" required>
          ${CUSTOMERS.map(c => `<option value="${c.id}" ${isEdit&&a.customerId===c.id?'selected':''}>${c.name}</option>`).join('')}
        </select></div>
      <div class="form-group"><label>Serviciu</label>
        <select class="form-input" id="f_service" required>
          ${SERVICES.map(s => `<option value="${s}" ${isEdit&&a.service===s?'selected':''}>${s}</option>`).join('')}
        </select></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div class="form-group"><label>Data</label><input class="form-input" type="date" id="f_date" value="${isEdit?a.date:''}" required></div>
        <div class="form-group"><label>Ora</label><input class="form-input" type="time" id="f_time" value="${isEdit?a.time:'09:00'}" required></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div class="form-group"><label>Durata</label>
          <select class="form-input" id="f_duration">
            ${['1h','2h','3h','4h','6h','8h'].map(d => `<option value="${d}" ${isEdit&&a.duration===d?'selected':''}>${d}</option>`).join('')}
        </select></div>
        <div class="form-group"><label>Pret (RON)</label><input class="form-input" type="number" id="f_price" value="${isEdit?a.price:''}" required></div>
      </div>
      <div class="form-group"><label>Tehnician</label>
        <select class="form-input" id="f_tech" required>
          ${TECHNICIANS.map(t => `<option value="${t.name}" ${isEdit&&a.tech===t.name?'selected':''}>${t.name} — ${t.specialty}</option>`).join('')}
        </select></div>
      <div class="form-group"><label>Note</label><textarea class="form-input" id="f_notes" rows="2">${isEdit?a.notes||'':''}</textarea></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">Anuleaza</button>
        <button type="submit" class="btn btn-primary">${isEdit?'Salveaza':'Creeaza'}</button>
      </div>
    </form>
  `);
}

function saveAppt(e, id) {
  e.preventDefault();
  const cust = CUSTOMERS.find(c => c.id === document.getElementById('f_customer').value);
  const data = {
    customer: cust.name, customerId: cust.id, branch: currentBranch.isInstitution ? currentBranch.children[0] : currentBranch.id,
    service: document.getElementById('f_service').value,
    date: document.getElementById('f_date').value,
    time: document.getElementById('f_time').value,
    duration: document.getElementById('f_duration').value,
    price: parseInt(document.getElementById('f_price').value),
    tech: document.getElementById('f_tech').value,
    notes: document.getElementById('f_notes').value,
    status: 'pending',
  };
  if (id) {
    const idx = APPOINTMENTS.findIndex(a => a.id === id);
    if (idx >= 0) { APPOINTMENTS[idx] = {...APPOINTMENTS[idx], ...data}; }
    toast('Programare actualizata!');
  } else {
    data.id = getNextId('appt');
    APPOINTMENTS.push(data);
    toast('Programare creata!');
  }
  saveAppointments();
  closeModal();
  navigate('appointments');
}

function completeAppt(id) {
  const a = APPOINTMENTS.find(x => x.id === id);
  if (a) { a.status = 'done'; saveAppointments();
    if (!INVOICES.find(i => i.apptId === id)) {
      const inv = { id:getNextId('inv'), number:'INV-2026-'+String(++nextInvId).padStart(3,'0'), customer:a.customer, date:new Date().toISOString().slice(0,10), dueDate:new Date(Date.now()+15*86400000).toISOString().slice(0,10), amount:a.price, status:'unpaid', eFactura:'neinviata', apptId:id };
      INVOICES.push(inv);
      saveInvoices();
      toast('Factura generata: ' + inv.number);
    }
    closeModal(); toast('Interventie finalizata!'); navigate(currentView); }
}

function confirmAppt(id) {
  const a = APPOINTMENTS.find(x => x.id === id);
  if (a) { a.status = 'confirmed'; saveAppointments(); closeModal(); toast('Programare confirmata!'); navigate(currentView); }
}

function changeTech(id) {
  const a = APPOINTMENTS.find(x => x.id === id);
  if (!a) return;
  const nextTech = TECHNICIANS.find(t => t.name !== a.tech);
  if (nextTech) { a.tech = nextTech.name; saveAppointments(); closeModal(); toast('Tehnician schimbat: ' + nextTech.name); navigate(currentView); }
}

function deleteAppt(id) {
  if (!confirm('Stergeti aceasta programare?')) return;
  APPOINTMENTS = APPOINTMENTS.filter(a => a.id !== id);
  saveAppointments();
  toast('Programare stearsa');
  navigate(currentView);
}

/* ════════════════════════════════════════════
   JOBS (Technician View + Manager view)
   ════════════════════════════════════════════ */
function renderJobs() {
  const filtered = getFilteredAppts();

  if (currentUser.role === 'Tehnician') {
    const myJobs = filtered.filter(a => a.tech === currentUser.name);
    const todayJobs = myJobs.filter(a => a.date === '2026-07-16');
    const upcoming = myJobs.filter(a => a.date !== '2026-07-16');
    return `
      <div class="page-header"><h2>Interventiile Mele</h2></div>
      <h3 style="margin-bottom:12px">Azi (${todayJobs.length})</h3>
      ${todayJobs.length === 0 ? '<div class="empty-state"><div class="icon">✅</div><p>Nicio interventie azi. Relax! 🎉</p></div>' : ''}
      ${todayJobs.map(j => jobCard(j)).join('')}
      ${upcoming.length > 0 ? `<h3 style="margin:20px 0 12px">Urmatoarele (${upcoming.length})</h3>` + upcoming.map(j => jobCard(j)).join('') : ''}
      ${myJobs.length === 0 && todayJobs.length === 0 ? '<div class="empty-state"><div class="icon">🔧</div><p>Nu ai interventii asignate</p></div>' : ''}`;
  }

  const pending = filtered.filter(a => a.status !== 'done');
  return `
    <div class="page-header"><h2>Toate Interventiile</h2><span style="color:var(--text-secondary)">${pending.length} active</span></div>
    ${filtered.length === 0 ? '<div class="empty-state"><div class="icon">🔧</div><p>Nicio interventie in aceasta locatie</p></div>' : renderTable(
      ['Client','Serviciu','Data','Tehnician','Status','Pret','Actiuni'],
      filtered.map(j => [j.customer, j.service, j.date+' '+j.time, j.tech, statusBadge(j.status), j.price+' RON',
        j.status !== 'done' ? `<button class="btn btn-sm btn-primary" onclick="completeAppt('${j.id}')">✓ Finalizat</button>` : '—'])
    )}`;
}

function jobCard(j) {
  const cust = CUSTOMERS.find(c => c.id === j.customerId);
  return `<div class="kpi-card" style="margin-bottom:12px;${j.status==='done'?'opacity:.6':''}">
    <div style="display:flex;justify-content:space-between;align-items:start">
      <div><strong>${j.time}</strong> — ${j.service}</div>
      ${statusBadge(j.status)}
    </div>
    <div style="color:var(--text-secondary);margin-top:4px;font-size:.85rem">
      <strong>${j.customer}</strong> · ${cust?cust.address:'-'} · ${cust?cust.phone:'-'}
    </div>
    <div style="margin-top:12px;display:flex;gap:8px">
      ${j.status === 'done'
        ? `<span style="font-size:.8rem;color:var(--text-secondary)">✅ Finalizat</span>`
        : `<button class="btn btn-primary btn-sm" onclick="completeAppt('${j.id}')">✓ Finalizat</button>
           <button class="btn btn-outline btn-sm" onclick="addJobNote('${j.id}')">📝 Nota</button>`
      }
      ${j.status !== 'done' ? `<span style="font-size:.8rem;color:var(--text-secondary);margin-left:auto">${j.price} RON</span>` : ''}
    </div>
  </div>`;
}

function addJobNote(id) {
  const a = APPOINTMENTS.find(x => x.id === id);
  if (!a) return;
  const note = prompt('Adauga nota pentru aceasta interventie:', a.notes || '');
  if (note !== null) { a.notes = note; saveAppointments(); toast('Nota salvata!'); navigate('jobs'); }
}

/* ════════════════════════════════════════════
   CUSTOMERS — Full CRUD + Search
   ════════════════════════════════════════════ */
function renderCustomers() {
  const filtered = filterData(CUSTOMERS);
  return `
    <div class="page-header"><h2>Clienti</h2><button class="btn btn-primary btn-sm" onclick="showCustomerForm()">+ Client nou</button></div>
    <div class="search-bar">
      <input class="form-input" type="text" placeholder="Cauta dupa nume, telefon, email..." value="${searchQuery}" oninput="searchQuery=this.value;refreshContent()">
    </div>
    ${filtered.length === 0 ? '<div class="empty-state"><div class="icon">👥</div><p>Niciun client gasit</p></div>' : renderTable(
      ['Nume','Telefon','Email','Adresa','Interventii','Ultima',''],
      filtered.map(c => [`<strong onclick="showCustomerDetail('${c.id}')" style="cursor:pointer;color:var(--primary)">${c.name}</strong>`, c.phone, c.email, c.address, c.totalJobs, c.lastJob,
        `<button class="btn btn-sm btn-outline" onclick="showCustomerDetail('${c.id}')">👁</button>`])
    )}`;
}

function showCustomerDetail(id) {
  const c = CUSTOMERS.find(x => x.id === id);
  if (!c) return;
  const appts = APPOINTMENTS.filter(a => a.customerId === id);
  openModal(`
    <h3>${c.name}</h3>
    <div class="detail-grid">
      <div class="detail-field"><label>Telefon</label><span>${c.phone}</span></div>
      <div class="detail-field"><label>Email</label><span>${c.email}</span></div>
      <div class="detail-field" style="grid-column:1/-1"><label>Adresa</label><span>${c.address}</span></div>
      <div class="detail-field"><label>Total interventii</label><span>${c.totalJobs}</span></div>
      <div class="detail-field"><label>Ultima interventie</label><span>${c.lastJob}</span></div>
      <div class="detail-field" style="grid-column:1/-1"><label>Note</label><span>${c.notes || '—'}</span></div>
    </div>
    ${appts.length > 0 ? `<h4 style="margin-bottom:8px">Istoric Interventii</h4>${renderTable(['Serviciu','Data','Status','Pret'], appts.slice(-5).map(a => [a.service, a.date, statusBadge(a.status), a.price+' RON']))}` : ''}
    <div class="modal-actions">
      <button class="btn btn-outline btn-sm" onclick="showCustomerForm('${c.id}')">✏️ Editeaza</button>
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Inchide</button>
    </div>
  `);
}

function showCustomerForm(id) {
  const c = id ? CUSTOMERS.find(x => x.id === id) : null;
  const isEdit = !!c;
  openModal(`
    <h3>${isEdit ? 'Editeaza' : 'Client Nou'}</h3>
    <form onsubmit="saveCustomer(event, '${id||''}')">
      <div class="form-group"><label>Nume</label><input class="form-input" id="cf_name" value="${isEdit?c.name:''}" required></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div class="form-group"><label>Telefon</label><input class="form-input" id="cf_phone" value="${isEdit?c.phone:''}" required></div>
        <div class="form-group"><label>Email</label><input class="form-input" type="email" id="cf_email" value="${isEdit?c.email:''}" required></div>
      </div>
      <div class="form-group"><label>Adresa</label><input class="form-input" id="cf_address" value="${isEdit?c.address:''}" required></div>
      <div class="form-group"><label>Note</label><textarea class="form-input" id="cf_notes" rows="2">${isEdit?c.notes||'':''}</textarea></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">Anuleaza</button>
        <button type="submit" class="btn btn-primary">${isEdit?'Salveaza':'Adauga'}</button>
      </div>
    </form>
  `);
}

function saveCustomer(e, id) {
  e.preventDefault();
  const data = {
    name: document.getElementById('cf_name').value,
    phone: document.getElementById('cf_phone').value,
    email: document.getElementById('cf_email').value,
    address: document.getElementById('cf_address').value,
    notes: document.getElementById('cf_notes').value,
  };
  if (id) {
    const idx = CUSTOMERS.findIndex(c => c.id === id);
    if (idx >= 0) { CUSTOMERS[idx] = {...CUSTOMERS[idx], ...data}; toast('Client actualizat!'); }
  } else {
    data.id = getNextId('cust');
    data.totalJobs = 0; data.lastJob = '-'; data.createdAt = new Date().toISOString().slice(0,10);
    CUSTOMERS.push(data);
    toast('Client adaugat!');
  }
  saveCustomers();
  closeModal();
  navigate('customers');
}

/* ════════════════════════════════════════════
   INVOICES + eFactura
   ════════════════════════════════════════════ */
function renderInvoices() {
  const filtered = filterData(INVOICES);
  const total = INVOICES.reduce((s,i) => s+i.amount, 0);
  const unpaidAmount = INVOICES.filter(i => i.status==='unpaid').reduce((s,i) => s+i.amount, 0);
  return `
    <div class="page-header"><h2>Facturi</h2>
      <div style="display:flex;gap:8px">
        <span style="font-size:.8rem;color:var(--text-secondary);padding:6px 0">Total: ${total} RON</span>
        <button class="btn btn-primary btn-sm" onclick="generateBulkInvoices()">📨 eFactura</button>
      </div>
    </div>
    <div class="search-bar">
      <input class="form-input" type="text" placeholder="Cauta factura..." value="${searchQuery}" oninput="searchQuery=this.value;refreshContent()">
      <div class="badge-filters">
        ${['all','paid','unpaid'].map(s => `<span class="filter-badge ${statusFilter===s?'active':''}" onclick="statusFilter='${s}';refreshContent()">${s==='all'?'Toate':s==='paid'?'Platite':'Neplatite'}</span>`).join('')}
      </div>
    </div>
    ${filtered.length === 0 ? '<div class="empty-state"><div class="icon">📄</div><p>Nicio factura gasita</p></div>' : renderTable(
      ['Numar','Client','Data emitere','Scadenta','Valoare','Status','eFactura',''],
      filtered.map(i => [i.number, `<strong onclick="showInvoiceDetail('${i.id}')" style="cursor:pointer;color:var(--primary)">${i.customer}</strong>`, i.date, i.dueDate, i.amount+' RON', statusBadge(i.status), eFacturaBadge(i.eFactura),
        `<div style="display:flex;gap:4px">
          ${i.status === 'unpaid' ? `<button class="btn btn-sm btn-primary" onclick="markPaid('${i.id}')">💰 Plateste</button>` : ''}
          ${i.eFactura === 'neinviata' ? `<button class="btn btn-sm btn-outline" onclick="sendEfactura('${i.id}')">📨 Trimite</button>` : ''}
          <button class="btn btn-sm btn-outline" onclick="showInvoiceDetail('${i.id}')">👁</button>
        </div>`])
    )}`;
}

function showInvoiceDetail(id) {
  const i = INVOICES.find(x => x.id === id);
  if (!i) return;
  openModal(`
    <h3>Factura ${i.number}</h3>
    <div class="detail-grid">
      <div class="detail-field"><label>Client</label><span>${i.customer}</span></div>
      <div class="detail-field"><label>Status</label><span>${statusBadge(i.status)}</span></div>
      <div class="detail-field"><label>Data emitere</label><span>${i.date}</span></div>
      <div class="detail-field"><label>Scadenta</label><span>${i.dueDate}</span></div>
      <div class="detail-field"><label>Valoare</label><span style="font-size:1.1rem;font-weight:700">${i.amount} RON</span></div>
      <div class="detail-field"><label>eFactura</label><span>${eFacturaBadge(i.eFactura)}</span></div>
    </div>
    <div style="background:var(--bg);padding:16px;border-radius:var(--radius-sm);margin-bottom:16px">
      <h4 style="font-size:.85rem;margin-bottom:8px">eFactura — SPV (Spatiul Privat Virtual)</h4>
      <p style="font-size:.8rem;color:var(--text-secondary)">
        ${i.eFactura === 'neinviata' ? 'Factura nu a fost inca transmisa catre ANAF. Apasati "Trimite eFactura" pentru a o transmite.' :
          i.eFactura === 'transmisa' ? 'Factura a fost transmisa catre ANAF. Asteptati confirmarea.' :
          i.eFactura === 'acceptata' ? 'Factura a fost acceptata de ANAF si este disponibila in SPV.' :
          'Factura a fost descarcata de cumparator.'}
      </p>
    </div>
    <div class="modal-actions">
      ${i.status === 'unpaid' ? `<button class="btn btn-primary btn-sm" onclick="markPaid('${i.id}')">💰 Marcheaza ca platita</button>` : ''}
      ${i.eFactura === 'neinviata' ? `<button class="btn btn-outline btn-sm" onclick="sendEfactura('${i.id}')">📨 Trimite eFactura</button>` : ''}
      <button class="btn btn-outline btn-sm" onclick="downloadPdf(i)">📄 PDF</button>
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Inchide</button>
    </div>
  `);
}
function downloadPdf() { toast('PDF generat: factura-export.pdf', 'success'); }

function markPaid(id) {
  const i = INVOICES.find(x => x.id === id);
  if (i) { i.status = 'paid'; saveInvoices(); closeModal(); toast('Factura marcata ca platita!'); navigate('invoices'); }
}

function sendEfactura(id) {
  const i = INVOICES.find(x => x.id === id);
  if (i) { i.eFactura = 'transmisa'; saveInvoices(); closeModal(); toast('eFactura transmisa catre ANAF!'); navigate('invoices'); }
}

function generateBulkInvoices() {
  const pending = APPOINTMENTS.filter(a => a.status === 'done' && !INVOICES.find(i => i.apptId === a.id));
  if (pending.length === 0) { toast('Toate interventiile finalizate au facturi generate.', 'error'); return; }
  pending.forEach(a => {
    INVOICES.push({
      id: getNextId('inv'),
      number: 'INV-2026-'+String(nextInvId).padStart(3,'0'),
      customer: a.customer, date: new Date().toISOString().slice(0,10),
      dueDate: new Date(Date.now()+15*86400000).toISOString().slice(0,10),
      amount: a.price, status: 'unpaid', eFactura: 'neinviata', apptId: a.id
    });
  });
  saveInvoices();
  toast(pending.length + ' facturi generate si trimise la ANAF via eFactura!');
  navigate('invoices');
}

/* ════════════════════════════════════════════
   MODALS
   ════════════════════════════════════════════ */
function openModal(html) {
  const overlay = document.getElementById('modalOverlay');
  if (overlay) { overlay.innerHTML = '<div class="modal"><button class="modal-close" onclick="closeModal()">✕</button>' + html + '</div>'; overlay.classList.add('open'); }
}
function closeModal() { const o = document.getElementById('modalOverlay'); if (o) o.classList.remove('open'); }

/* ── User menu ── */
function showUserMenu() {
  openModal(`
    <h3>${currentUser.name}</h3>
    <div class="detail-grid">
      <div class="detail-field"><label>Rol</label><span>${currentUser.role}</span></div>
      <div class="detail-field"><label>Locatie</label><span>${currentBranch.name}</span></div>
    </div>
    <div class="modal-actions">
      <button class="btn btn-outline btn-sm" onclick="closeModal();navigate('login')">🚪 Schimba utilizator</button>
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Inchide</button>
    </div>
  `);
}

/* ════════════════════════════════════════════
   HELPERS
   ════════════════════════════════════════════ */
function getFilteredAppts() {
  return APPOINTMENTS.filter(a => {
    if (currentUser.role === 'Tehnician') return a.tech === currentUser.name;
    if (currentBranch.isInstitution) return true;
    return a.branch === currentBranch.id;
  });
}

function filterData(data) {
  let result = [...data];
  if (currentView !== 'dashboard' && currentView !== 'jobs') {
    const q = searchQuery.toLowerCase().trim();
    if (q) {
      result = result.filter(item => {
        const s = JSON.stringify(Object.values(item)).toLowerCase();
        return s.includes(q);
      });
    }
  }
  if (statusFilter && statusFilter !== 'all' && currentView !== 'jobs') {
    result = result.filter(item => item.status === statusFilter);
  }
  return result;
}

function statusBadge(status) {
  const colors = { pending:'badge-pending', confirmed:'badge-confirmed', done:'badge-done', paid:'badge-paid', unpaid:'badge-unpaid' };
  return `<span class="badge ${colors[status]||'badge-pending'}">${status}</span>`;
}

function eFacturaBadge(status) {
  const colors = { transmisa:'badge-confirmed', acceptata:'badge-done', descarcata:'badge-paid', neinviata:'badge-unpaid' };
  return `<span class="badge ${colors[status]||'badge-unpaid'}" style="font-size:.65rem">${status}</span>`;
}

function renderTable(headers, rows) {
  return `<table class="data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

/* ── Refresh content view (called from search/filter inputs) ── */
function refreshContent() {
  const c = document.getElementById('app-content');
  if (c) c.innerHTML = renderContent(currentView);
}

/* ── Bootstrap: start app after all scripts load ── */
document.addEventListener('DOMContentLoaded', () => {
  const view = window.location.hash.slice(1) || 'login';
  currentView = view;
  render(view);
});