/* Nexus Mock App — Screen rendering */
function render(view) {
  const app = document.getElementById('app');
  if (view === 'login') return renderLogin(app);
  app.innerHTML = renderShell();
  document.querySelector('#app-content').innerHTML = renderContent(view);
  setupSidebar();
  setupBranchSwitch();
}

/* ── Shell (sidebar + topbar) ── */
function renderShell() {
  const nav = [
    ['dashboard','📊','Dashboard'],
    ['appointments','📅','Programari'],
    ['jobs','🔧','Interventii'],
    ['customers','👥','Clienti'],
    ['invoices','📄','Facturi'],
  ];
  const links = nav.map(([id,icon,label]) =>
    `<li><a href="#${id}" class="${currentView===id?'active':''}" data-nav="${id}"><span class="icon">${icon}</span>${label}</a></li>`
  ).join('');

  const branchOpts = currentBranch.isInstitution
    ? '<option value="'+currentBranch.id+'">'+currentBranch.name+' (Toate)</option>' +
      currentBranch.children.map(id => '<option value="'+id+'">'+BRANCHES[id].name+'</option>').join('')
    : '<option value="'+currentBranch.id+'">'+currentBranch.name+'</option>';

  return `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar-logo">Nex<span>u</span>s</div>
        <ul class="sidebar-nav">${links}</ul>
      </aside>
      <div class="main">
        <header class="topbar">
          <div class="topbar-left">
            <select class="branch-select" id="branchSwitch">${branchOpts}</select>
          </div>
          <div class="topbar-right">
            <span style="font-size:.8rem;color:var(--text-secondary)">${currentUser.role}</span>
            <div class="user-badge"><div class="avatar">${currentUser.initials}</div>${currentUser.name}</div>
          </div>
        </header>
        <div class="content" id="app-content"></div>
      </div>
    </div>`;
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
            <select class="form-input" id="loginRole" onchange="handleRoleSwitch()">
              <option value="owner">Andrei Popescu (Admin)</option>
              <option value="manager">Maria Ionescu (Manager)</option>
              <option value="tech">Ion Vasilescu (Tehnician)</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:8px">Sign In</button>
        </form>
      </div>
    </div>`;
}

function handleLogin(e) { e.preventDefault(); const role=document.getElementById('loginRole').value; currentUser=USERS[role]; currentBranch=BRANCHES[role==='tech'?'branch-1':'inst-1']; navigate('dashboard'); }
function handleRoleSwitch() { /* preview only */ }

/* ── Content views ── */
function renderContent(view) {
  switch(view) {
    case 'dashboard': return renderDashboard();
    case 'appointments': return renderAppointments();
    case 'jobs': return renderJobs();
    case 'customers': return renderCustomers();
    case 'invoices': return renderInvoices();
    default: return '<p>Page not found</p>';
  }
}

/* ── Dashboard ── */
function renderDashboard() {
  const todayApps = APPOINTMENTS.filter(a => a.date==='2026-07-16');
  const totalRevenue = INVOICES.filter(i => i.status==='paid').reduce((s,i) => s+i.amount, 0);
  const unpaid = INVOICES.filter(i => i.status==='unpaid').reduce((s,i) => s+i.amount, 0);
  return `
    <div class="page-header"><h2>Dashboard</h2><span style="color:var(--text-secondary)">${new Date().toLocaleDateString('ro-RO',{weekday:'long',day:'numeric',month:'long'})}</span></div>
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-label">Programari azi</div><div class="kpi-value">${todayApps.length}</div><div class="kpi-sub">↑ 2 fata de ieri</div></div>
      <div class="kpi-card"><div class="kpi-label">Venituri luna</div><div class="kpi-value">${(totalRevenue/1000).toFixed(0)}k RON</div><div class="kpi-sub">+12% vs luna trecuta</div></div>
      <div class="kpi-card"><div class="kpi-label">Facturi neincasate</div><div class="kpi-value">${(unpaid/1000).toFixed(1)}k RON</div><div class="kpi-sub" style="color:var(--error)">${INVOICES.filter(i=>i.status==='unpaid').length} facturi</div></div>
      <div class="kpi-card"><div class="kpi-label">Clienti activi</div><div class="kpi-value">${CUSTOMERS.length}</div><div class="kpi-sub">+1 luna aceasta</div></div>
    </div>
    <h3 style="margin-bottom:12px">Programari Recente</h3>
    <table class="data-table"><thead><tr><th>Client</th><th>Serviciu</th><th>Data</th><th>Tehnician</th><th>Status</th><th>Valoare</th></tr></thead><tbody>
      ${APPOINTMENTS.slice(0,5).map(a => `
        <tr><td><strong>${a.customer}</strong></td><td>${a.service}</td><td>${a.date} ${a.time}</td><td>${a.tech}</td><td><span class="badge badge-${a.status}">${a.status}</span></td><td>${a.price} RON</td></tr>
      `).join('')}
    </tbody></table>`;
}

/* ── Appointments ── */
function renderAppointments() {
  return `
    <div class="page-header"><h2>Programari</h2><button class="btn btn-primary btn-sm" onclick="alert('Mock: formular programare noua')">+ Programare noua</button></div>
    <table class="data-table"><thead><tr><th>Client</th><th>Serviciu</th><th>Data</th><th>Ora</th><th>Durata</th><th>Tehnician</th><th>Status</th><th>Pret</th></tr></thead><tbody>
      ${APPOINTMENTS.map(a => `
        <tr onclick="alert('Detalii: ${a.service}\\nClient: ${a.customer}\\nData: ${a.date} ${a.time}\\nTehnician: ${a.tech}\\nPret: ${a.price} RON')" style="cursor:pointer">
          <td><strong>${a.customer}</strong></td><td>${a.service}</td><td>${a.date}</td><td>${a.time}</td><td>${a.duration}</td><td>${a.tech}</td><td><span class="badge badge-${a.status}">${a.status}</span></td><td>${a.price} RON</td></tr>
      `).join('')}
    </tbody></table>`;
}

/* ── Jobs (Technician view) ── */
function renderJobs() {
  if (currentUser.role === 'Tehnician') {
    const myJobs = APPOINTMENTS.filter(a => a.tech === currentUser.name && a.date === '2026-07-16');
    return `<div class="page-header"><h2>Interventiile Mele Azi</h2></div>
      ${myJobs.length === 0 ? '<p style="color:var(--text-secondary)">Nicio interventie programata azi</p>' : ''}
      ${myJobs.map(j => `
        <div class="kpi-card" style="margin-bottom:12px;cursor:pointer" onclick="alert('Interventie: ${j.service}\\nClient: ${j.customer}\\nAdresa: ${CUSTOMERS.find(c=>c.id===j.customerId).address}\\nOra: ${j.time}\\nPret: ${j.price} RON')">
          <div style="display:flex;justify-content:space-between;align-items:start">
            <div><strong>${j.time}</strong> — ${j.service}</div>
            <span class="badge badge-${j.status}">${j.status}</span>
          </div>
          <div style="color:var(--text-secondary);margin-top:4px">${j.customer} · ${CUSTOMERS.find(c=>c.id===j.customerId).address}</div>
          <div style="margin-top:12px;display:flex;gap:8px">
            <button class="btn btn-primary btn-sm" onclick="event.stopPropagation();completeJob('${j.id}')">✓ Finalizat</button>
            <button class="btn btn-outline btn-sm" onclick="event.stopPropagation();alert('Adauga nota: ...')">📝 Nota</button>
          </div>
        </div>
      `).join('')}`;
  }
  return `<div class="page-header"><h2>Toate Interventiile</h2></div><p style="color:var(--text-secondary)">Vezi toate job-urile active. Filtreaza dupa tehnician sau status.</p>`;
}

function completeJob(id) {
  const app = APPOINTMENTS.find(a => a.id === id);
  if (app) { app.status = 'done'; navigate('jobs'); }
}

/* ── Customers ── */
function renderCustomers() {
  return `
    <div class="page-header"><h2>Clienti</h2><button class="btn btn-primary btn-sm" onclick="alert('Mock: adauga client nou')">+ Client nou</button></div>
    <table class="data-table"><thead><tr><th>Nume</th><th>Telefon</th><th>Email</th><th>Adresa</th><th>Interventii</th></tr></thead><tbody>
      ${CUSTOMERS.map(c => `
        <tr onclick="alert('Client: ${c.name}\\nTel: ${c.phone}\\nEmail: ${c.email}\\nAdresa: ${c.address}\\nInterventii: ${c.totalJobs}')" style="cursor:pointer">
          <td><strong>${c.name}</strong></td><td>${c.phone}</td><td>${c.email}</td><td>${c.address}</td><td>${c.totalJobs}</td></tr>
      `).join('')}
    </tbody></table>`;
}

/* ── Invoices ── */
function renderInvoices() {
  return `
    <div class="page-header"><h2>Facturi</h2><button class="btn btn-primary btn-sm" onclick="alert('Mock: genereaza factura')">+ Factura noua</button></div>
    <table class="data-table"><thead><tr><th>Numar</th><th>Client</th><th>Data emitere</th><th>Scadenta</th><th>Valoare</th><th>Status</th></tr></thead><tbody>
      ${INVOICES.map(i => `
        <tr><td>${i.number}</td><td><strong>${i.customer}</strong></td><td>${i.date}</td><td>${i.dueDate}</td><td>${i.amount} RON</td><td><span class="badge badge-${i.status}">${i.status}</span></td></tr>
      `).join('')}
    </tbody></table>`;
}

/* ── Sidebar Navigation ── */
function setupSidebar() {
  document.querySelectorAll('[data-nav]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      navigate(this.dataset.nav);
    });
  });
}

function setupBranchSwitch() {
  const sel = document.getElementById('branchSwitch');
  if (sel) {
    sel.addEventListener('change', function() {
      currentBranch = BRANCHES[this.value];
      navigate(currentView);
    });
  }
}