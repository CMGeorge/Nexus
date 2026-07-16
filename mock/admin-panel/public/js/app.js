/* Nexus Admin Panel — Full Interactive Mock */
/* Hallmark · P4 H5 E5 S4 R5 V4 */

let searchQuery = '';
let statusFilter = 'all';
let auditSearch = '';

function render(view) {
  const app = document.getElementById('app');
  if (view === 'login') return renderLogin(app);
  app.innerHTML = renderShell() + '<div id="toastContainer" class="toast-container"></div>';
  document.querySelector('#ap-content').innerHTML = renderContent(view);
  setupSidebar();
}

/* ── Shell ── */
function renderShell() {
  const nav = [
    ['dashboard','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>','Dashboard'],
    ['companies','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>','Companii'],
    ['audit','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>','Audit'],
    ['settings','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>','Setari'],
  ];
  const links = nav.map(([id,icon,label]) => `<li><a href="#${id}" class="${currentView===id?'active':''}" data-nav="${id}">${icon}${label}</a></li>`).join('');
  return `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <h2>Nexus Admin</h2>
          <span class="admin-tag">WeSell</span>
        </div>
        <ul class="sidebar-nav" style="list-style:none">${links}</ul>
        <div style="padding:var(--space-md);border-top:1px solid oklch(100% 0 0 / 10%);font-size:.7rem;color:oklch(100% 0 0 / 40%)">${ADMIN.name}</div>
      </aside>
      <div class="main">
        <div class="topbar"><h1>Admin Panel</h1><span style="font-size:.8rem;color:var(--color-muted)">${ADMIN.name} · Platform Admin</span></div>
        <div class="page-content" id="ap-content"></div>
      </div>
    </div>`;
}

function setupSidebar() {
  document.querySelectorAll('[data-nav]').forEach(a => {
    a.addEventListener('click', e => { e.preventDefault(); navigate(a.dataset.nav); });
  });
}

/* ── Content Router ── */
function renderContent(view) {
  switch(view) {
    case 'dashboard': return renderDashboard();
    case 'companies': return renderCompanies();
    case 'audit': return renderAudit();
    case 'settings': return renderSettings();
    default: return '<div class="empty-state"><p>Pagina nu a fost gasita</p></div>';
  }
}

/* ── Login ── */
function renderLogin(appEl) {
  appEl.innerHTML = `
    <div class="login-page">
      <div class="login-card">
        <span class="login-badge">WeSell Admin</span>
        <h1>Nexus Admin Panel</h1>
        <p class="subtitle">Platform management</p>
        <div class="form-group"><label>Email</label><input class="form-input" value="${ADMIN.email}" readonly></div>
        <div class="form-group"><label>Nume</label><input class="form-input" value="${ADMIN.name}" readonly></div>
        <button class="btn btn-primary btn-block" onclick="navigate('dashboard')">Autentificare</button>
        <p style="font-size:.7rem;color:var(--color-muted);margin-top:var(--space-md)">Cont demonstrativ — click pentru a intra</p>
      </div>
    </div>`;
}

/* ── Dashboard ── */
function renderDashboard() {
  const maxRevenue = Math.max(...REVENUE_CHART.map(r => r.value));
  const maxUsers = Math.max(...USER_GROWTH.map(u => u.value));
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Platform Dashboard</h2>
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-label">Companii active</div><div class="kpi-value">${KPIS.totalBusinesses}</div><div class="kpi-change up">${KPIS.totalBusinessesChange}</div></div>
      <div class="kpi-card"><div class="kpi-label">Utilizatori activi</div><div class="kpi-value">${KPIS.activeUsers}</div><div class="kpi-change up">${KPIS.activeUsersChange}</div></div>
      <div class="kpi-card"><div class="kpi-label">Venit total</div><div class="kpi-value">${KPIS.totalRevenue.toLocaleString()} RON</div><div class="kpi-change up">${KPIS.totalRevenueChange}</div></div>
      <div class="kpi-card"><div class="kpi-label">Programari azi</div><div class="kpi-value">${KPIS.appointmentsToday}</div><div class="kpi-change up">${KPIS.appointmentsTodayChange}</div></div>
    </div>
    <div class="card" style="margin-bottom:var(--space-lg)">
      <h3>Venit lunar (RON)</h3>
      <div class="bar-chart">
        ${REVENUE_CHART.map(r => `<div class="bar-col"><div class="bar-value">${(r.value/1000).toFixed(0)}k</div><div class="bar" style="height:${(r.value/maxRevenue)*140}px;background:var(--color-admin)"></div><div class="bar-label">${r.month}</div></div>`).join('')}
      </div>
    </div>
    <div class="card">
      <h3>Utilizatori activi</h3>
      <div class="bar-chart">
        ${USER_GROWTH.map(u => `<div class="bar-col"><div class="bar-value">${u.value}</div><div class="bar" style="height:${(u.value/maxUsers)*140}px;background:var(--color-anchor-2)"></div><div class="bar-label">${u.month}</div></div>`).join('')}
      </div>
    </div>`;
}

/* ── Companies ── */
function renderCompanies() {
  const filtered = COMPANIES.filter(c => {
    if (statusFilter !== 'all') return c.status === statusFilter;
    if (searchQuery) return c.name.toLowerCase().includes(searchQuery.toLowerCase());
    return true;
  });
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Gestiune Companii</h2>
    <div class="search-bar">
      <input class="form-input" type="text" placeholder="Cauta companie..." value="${searchQuery}" oninput="searchQuery=this.value;refreshContent()" style="max-width:300px">
      <div class="badge-filters">
        ${['all','active','suspended','pending'].map(s => `<span class="filter-badge ${statusFilter===s?'active':''}" onclick="statusFilter='${s}';refreshContent()">${s==='all'?'Toate':s==='active'?'Active':s==='suspended'?'Suspendate':'In asteptare'}</span>`).join('')}
      </div>
    </div>
    ${filtered.length === 0 ? '<div class="empty-state"><p>Nicio companie gasita</p></div>' : renderTable(
      ['Companie','Plan','Utilizatori','Venit','Status','Actiuni'],
      filtered.map(c => [c.name, c.plan, c.users, c.revenue.toLocaleString() + ' RON', statusBadge(c.status),
        `<div style="display:flex;gap:4px">
          ${c.status === 'active' ? `<button class="btn btn-danger btn-sm" onclick="suspendCompany('${c.id}')">Suspend</button>` : ''}
          ${c.status === 'suspended' ? `<button class="btn btn-primary btn-sm" onclick="activateCompany('${c.id}')">Activeaza</button>` : ''}
          ${c.status === 'pending' ? `<button class="btn btn-primary btn-sm" onclick="approveCompany('${c.id}')">Aproba</button>` : ''}
          <button class="btn btn-outline btn-sm" onclick="viewCompany('${c.id}')">Detalii</button>
        </div>`])
    )}`;
}

function suspendCompany(id) {
  const c = COMPANIES.find(x => x.id === id);
  if (c) {
    c.status = 'suspended';
    AUDIT_LOGS.unshift({ id:'log-'+Date.now(), time:new Date().toLocaleTimeString('ro-RO',{hour:'2-digit',minute:'2-digit'}), company:c.name, user:ADMIN.name, action:'companie.suspendata', detail:'Suspendat din admin panel' });
    saveCompanies(); saveAuditLogs(); refreshContent(); toast('Companie suspendata!');
  }
}

function activateCompany(id) {
  const c = COMPANIES.find(x => x.id === id);
  if (c) {
    c.status = 'active';
    AUDIT_LOGS.unshift({ id:'log-'+Date.now(), time:new Date().toLocaleTimeString('ro-RO',{hour:'2-digit',minute:'2-digit'}), company:c.name, user:ADMIN.name, action:'companie.activata', detail:'Reactivata din admin panel' });
    saveCompanies(); saveAuditLogs(); refreshContent(); toast('Companie reactivata!');
  }
}

function approveCompany(id) {
  const c = COMPANIES.find(x => x.id === id);
  if (c) {
    c.status = 'active';
    AUDIT_LOGS.unshift({ id:'log-'+Date.now(), time:new Date().toLocaleTimeString('ro-RO',{hour:'2-digit',minute:'2-digit'}), company:c.name, user:ADMIN.name, action:'companie.aprobata', detail:'Aprobata din admin panel' });
    saveCompanies(); saveAuditLogs(); refreshContent(); toast('Companie aprobata!');
  }
}

function viewCompany(id) {
  const c = COMPANIES.find(x => x.id === id);
  if (!c) return;
  openModal(`
    <h3>${c.name}</h3>
    <div class="detail-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-md);margin-bottom:var(--space-md)">
      <div><label style="font-size:.7rem;color:var(--color-muted)">Domeniu</label><p style="font-size:.85rem">${c.domain}</p></div>
      <div><label style="font-size:.7rem;color:var(--color-muted)">Plan</label><p style="font-size:.85rem">${c.plan}</p></div>
      <div><label style="font-size:.7rem;color:var(--color-muted)">Utilizatori</label><p style="font-size:.85rem">${c.users}</p></div>
      <div><label style="font-size:.7rem;color:var(--color-muted)">Venit</label><p style="font-size:.85rem">${c.revenue.toLocaleString()} RON</p></div>
      <div><label style="font-size:.7rem;color:var(--color-muted)">Status</label><p>${statusBadge(c.status)}</p></div>
      <div><label style="font-size:.7rem;color:var(--color-muted)">Inregistrat</label><p style="font-size:.85rem">${c.joinedAt}</p></div>
    </div>
    <div style="display:flex;gap:8px;justify-content:flex-end">
      ${c.status === 'active' ? `<button class="btn btn-danger btn-sm" onclick="suspendCompany('${c.id}')">Suspend</button>` : ''}
      ${c.status === 'suspended' ? `<button class="btn btn-primary btn-sm" onclick="activateCompany('${c.id}')">Activeaza</button>` : ''}
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Inchide</button>
    </div>
  `);
}

/* ── Audit Logs ── */
function renderAudit() {
  const filtered = AUDIT_LOGS.filter(l => {
    if (auditSearch) return l.company.toLowerCase().includes(auditSearch.toLowerCase()) || l.user.toLowerCase().includes(auditSearch.toLowerCase()) || l.action.toLowerCase().includes(auditSearch.toLowerCase());
    return true;
  });
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Audit Logs</h2>
    <div class="search-bar">
      <input class="form-input" type="text" placeholder="Cauta in log-uri..." value="${auditSearch}" oninput="auditSearch=this.value;refreshContent()" style="max-width:400px">
    </div>
    <div class="card" style="padding:0">
      ${filtered.length === 0 ? '<div class="empty-state"><p>Niciun log gasit</p></div>' :
        filtered.map(l => `
          <div class="audit-entry">
            <span class="audit-time">${l.time}</span>
            <span class="audit-user">${l.user}</span>
            <span class="audit-action">${l.action}</span>
            <span class="audit-detail">${l.detail}</span>
          </div>
        `).join('')}
    </div>`;
}

/* ── Settings ── */
function renderSettings() {
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Setari Platforma</h2>
    <div class="card" style="margin-bottom:var(--space-lg)">
      <h3>Planuri tarifare</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:var(--space-md)">
        ${PRICING_TIERS.map(t => `
          <div class="tier-card ${t.name==='Professional'?'featured':''}">
            <div class="tier-name">${t.name}</div>
            <div class="tier-price">${t.price} <span>RON/${t.period}</span></div>
            <ul class="tier-features">
              ${t.features.map(f => `<li>✓ ${f}</li>`).join('')}
            </ul>
            <button class="btn btn-outline btn-sm btn-block" onclick="editTier('${t.id}')">Editeaza</button>
          </div>
        `).join('')}
      </div>
    </div>
    <div class="card" style="margin-bottom:var(--space-lg)">
      <h3>Feature Flags</h3>
      ${FEATURE_FLAGS.map(f => `
        <div class="feature-row">
          <div><div class="feature-name">${f.name}</div><div class="feature-desc">${f.description} · ${f.tiers.join(', ')}</div></div>
          <label class="toggle"><input type="checkbox" ${f.enabled?'checked':''} onchange="toggleFeature('${f.id}')"><span class="toggle-slider"></span></label>
        </div>
      `).join('')}
    </div>
    <div class="card">
      <h3>Template-uri email</h3>
      ${EMAIL_TEMPLATES.map(t => `
        <div class="feature-row">
          <div><div class="feature-name">${t.name}</div><div class="feature-desc">Subiect: ${t.subject} · ${t.updatedAt}</div></div>
          <button class="btn btn-outline btn-sm">Previzualizeaza</button>
        </div>
      `).join('')}
    </div>`;
}

function toggleFeature(id) {
  const f = FEATURE_FLAGS.find(x => x.id === id);
  if (f) {
    f.enabled = !f.enabled;
    saveFeatureFlags(); toast(f.name + ': ' + (f.enabled ? 'Activat' : 'Dezactivat'));
  }
}

function editTier(id) {
  const t = PRICING_TIERS.find(x => x.id === id);
  if (!t) return;
  openModal(`
    <h3>Editeaza plan: ${t.name}</h3>
    <div class="form-group"><label>Pret (RON/luna)</label><input class="form-input" id="mtierPrice" type="number" value="${t.price}"></div>
    <div class="form-group"><label>Functionalitati (una pe linie)</label><textarea class="form-input" id="mtierFeats" rows="6">${t.features.join('\n')}</textarea></div>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:var(--space-md)">
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Anuleaza</button>
      <button class="btn btn-primary btn-sm" onclick="saveTier('${t.id}')">Salveaza</button>
    </div>
  `);
}

function saveTier(id) {
  const t = PRICING_TIERS.find(x => x.id === id);
  if (t) {
    t.price = parseInt(document.getElementById('mtierPrice').value) || t.price;
    t.features = document.getElementById('mtierFeats').value.split('\n').filter(f => f.trim());
    savePricingTiers(); closeModal(); toast('Plan salvat!'); refreshContent();
  }
}

/* ── Helpers ── */
function statusBadge(status) {
  const colors = { active:'badge-active', suspended:'badge-suspended', pending:'badge-pending',
    paid:'badge-active', unpaid:'badge-suspended', done:'badge-active', confirmed:'badge-active' };
  return `<span class="badge ${colors[status]||'badge-pending'}">${status}</span>`;
}

function renderTable(headers, rows) {
  return `<table class="data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function refreshContent() {
  const c = document.getElementById('ap-content');
  if (c) c.innerHTML = renderContent(currentView);
}

/* ── Modal ── */
let modalOverlayEl = null;
function openModal(html) {
  if (!modalOverlayEl) {
    modalOverlayEl = document.createElement('div');
    modalOverlayEl.className = 'modal-overlay';
    modalOverlayEl.style.cssText = 'display:none;position:fixed;inset:0;background:oklch(0% 0 0 / 35%);z-index:1000;align-items:center;justify-content:center';
    modalOverlayEl.addEventListener('click', e => { if (e.target === modalOverlayEl) closeModal(); });
    document.body.appendChild(modalOverlayEl);
  }
  modalOverlayEl.innerHTML = `<div class="modal" style="background:#fff;border-radius:var(--radius-lg);padding:var(--space-xl);width:100%;max-width:520px;max-height:80vh;overflow-y:auto;box-shadow:0 20px 60px oklch(0% 0 0 / 20%)"><button style="float:right;background:none;border:none;font-size:1.25rem;cursor:pointer;color:var(--color-muted)" onclick="closeModal()">✕</button>${html}</div>`;
  modalOverlayEl.style.display = 'flex';
}
function closeModal() { if (modalOverlayEl) modalOverlayEl.style.display = 'none'; }

/* ── Toast ── */
function toast(msg, type) {
  const c = document.getElementById('toastContainer');
  if (!c) return;
  const el = document.createElement('div');
  el.className = 'toast ' + (type || '');
  el.textContent = msg;
  c.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}