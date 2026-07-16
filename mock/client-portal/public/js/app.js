/* Nexus Client Portal — Full Interactive Mock */
/* Hallmark · P4 H5 E5 S4 R5 V4 */

let searchQuery = '';
let statusFilter = 'all';

function render(view) {
  const app = document.getElementById('app');
  if (view === 'login') return renderLogin(app);
  app.innerHTML = renderShell() + '<div id="toastContainer" class="toast-container"></div>';
  document.querySelector('#cp-content').innerHTML = renderContent(view);
  setupSidebar();
}

/* ── Shell ── */
function renderShell() {
  const nav = [
    ['dashboard','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>','Dashboard'],
    ['appointments','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>','Programari'],
    ['invoices','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>','Facturi'],
    ['chat','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>','Mesaje'],
    ['loyalty','<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>','Loialitate'],
  ];
  const links = nav.map(([id,icon,label]) => `<li><a href="#${id}" class="${currentView===id?'active':''}" data-nav="${id}">${icon}${label}</a></li>`).join('');
  return `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar-brand">
          <h2>${BUSINESS.name}</h2>
          <div class="user-info">Portal Client · ${CUSTOMER.name}</div>
        </div>
        <ul class="sidebar-nav" style="list-style:none">${links}</ul>
      </aside>
      <div class="main">
        <div class="topbar"><h1>Portal Client</h1><span style="font-size:.8rem;color:var(--color-muted)">${CUSTOMER.name}</span></div>
        <div class="page-content" id="cp-content"></div>
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
    case 'appointments': return renderAppointments();
    case 'invoices': return renderInvoices();
    case 'chat': return renderChat();
    case 'loyalty': return renderLoyalty();
    default: return '<div class="empty-state"><p>Pagina nu a fost gasita</p></div>';
  }
}

/* ── Login ── */
function renderLogin(appEl) {
  appEl.innerHTML = `
    <div class="login-page">
      <div class="login-card">
        <div class="login-avatar">${CUSTOMER.name.charAt(0)}</div>
        <h1>Portal Client</h1>
        <p class="subtitle">${BUSINESS.name}</p>
        <div class="form-group"><label>Email</label><input class="form-input" id="loginEmail" value="${CUSTOMER.email}" readonly></div>
        <div class="form-group"><label>Nume</label><input class="form-input" id="loginName" value="${CUSTOMER.name}" readonly></div>
        <button class="btn btn-primary btn-block" onclick="navigate('dashboard')">Intra in cont</button>
        <p style="font-size:.7rem;color:var(--color-muted);margin-top:var(--space-md)">Cont demonstrativ — click pentru a intra</p>
      </div>
    </div>`;
}

/* ── Dashboard ── */
function renderDashboard() {
  const upcoming = APPOINTMENTS.filter(a => a.status !== 'done').sort((a,b) => a.date.localeCompare(b.date));
  const next = upcoming[0];
  const unpaid = INVOICES.filter(i => i.status === 'unpaid').reduce((s,i) => s + i.amount, 0);
  const doneCount = APPOINTMENTS.filter(a => a.status === 'done').length;
  return `
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-label">Urmatoarea programare</div><div class="kpi-value" style="font-size:1rem">${next ? next.date + ' ' + next.time : '—'}</div></div>
      <div class="kpi-card"><div class="kpi-label">Facturi neplatite</div><div class="kpi-value">${unpaid} RON</div></div>
      <div class="kpi-card"><div class="kpi-label">Interventii efectuate</div><div class="kpi-value">${doneCount}</div></div>
      <div class="kpi-card"><div class="kpi-label">Puncte loialitate</div><div class="kpi-value">${CUSTOMER.loyaltyPoints}</div></div>
    </div>
    <div class="card" style="margin-bottom:var(--space-lg)">
      <h3>Urmatoarea programare</h3>
      ${next ? `<p style="font-size:.85rem"><strong>${next.date}</strong> la ${next.time} — ${next.service}</p><p style="font-size:.8rem;color:var(--color-muted)">Tehnician: ${next.technician}</p>` : '<p style="color:var(--color-muted)">Nicio programare viitoare</p>'}
    </div>
    <div class="card">
      <h3>Interventii recente</h3>
      ${APPOINTMENTS.filter(a => a.status === 'done').slice(0,3).map(a => `<p style="font-size:.8rem;margin-bottom:4px">${a.date} — ${a.service} (${a.technician})</p>`).join('') || '<p style="color:var(--color-muted)">Nicio interventie efectuata</p>'}
    </div>`;
}

/* ── Appointments ── */
function renderAppointments() {
  const filtered = APPOINTMENTS.filter(a => {
    if (statusFilter === 'upcoming') return a.status !== 'done';
    if (statusFilter === 'past') return a.status === 'done';
    return true;
  });
  return `
    <div class="page-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--space-lg)">
      <h2 style="font-family:var(--font-display);font-size:1.1rem">Programarile mele</h2>
      <button class="btn btn-primary btn-sm" onclick="openBookModal()">+ Programare noua</button>
    </div>
    <div class="search-bar">
      <div class="badge-filters">
        ${['all','upcoming','past'].map(s => `<span class="filter-badge ${statusFilter===s?'active':''}" onclick="statusFilter='${s}';refreshContent()">${s==='all'?'Toate':s==='upcoming'?'Viitoare':'Trecute'}</span>`).join('')}
      </div>
    </div>
    ${filtered.length === 0 ? '<div class="empty-state"><p>Nicio programare gasita</p></div>' : renderTable(
      ['Data','Ora','Serviciu','Tehnician','Status'],
      filtered.map(a => [a.date, a.time, a.service, a.technician, statusBadge(a.status)])
    )}`;
}

function openBookModal() {
  const today = new Date().toISOString().slice(0,10);
  openModal(`
    <h3>Programare noua</h3>
    <div class="form-group"><label>Serviciu</label><select class="form-input" id="mservice">${SERVICES.map(s => `<option>${s}</option>`).join('')}</select></div>
    <div class="form-group"><label>Data</label><input type="date" class="form-input" id="mdate" value="${today}" min="${today}"></div>
    <div class="form-group"><label>Ora</label><select class="form-input" id="mtime">${['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00'].map(t => `<option>${t}</option>`).join('')}</select></div>
    <div class="form-group"><label>Observatii</label><textarea class="form-input" id="mnotes" rows="2" placeholder="Optional..."></textarea></div>
    <div class="modal-actions" style="display:flex;gap:8px;justify-content:flex-end;margin-top:var(--space-md)">
      <button class="btn btn-outline btn-sm" onclick="closeModal()">Anuleaza</button>
      <button class="btn btn-primary btn-sm" onclick="bookAppointment()">Confirma</button>
    </div>
  `);
}

function bookAppointment() {
  const date = document.getElementById('mdate').value;
  const time = document.getElementById('mtime').value;
  const service = document.getElementById('mservice').value;
  if (!date || !time) { toast('Selectati data si ora', 'error'); return; }
  APPOINTMENTS.push({
    id: 'apt-' + Date.now(), date, time, service,
    technician: 'Alocat automat', status: 'pending',
    notes: document.getElementById('mnotes')?.value || ''
  });
  saveAppointments(); closeModal(); toast('Programare creata!'); navigate('appointments');
}

/* ── Invoices ── */
function renderInvoices() {
  const total = INVOICES.reduce((s,i) => s + i.amount, 0);
  const unpaid = INVOICES.filter(i => i.status === 'unpaid').reduce((s,i) => s + i.amount, 0);
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Facturile mele</h2>
    <div class="kpi-grid" style="grid-template-columns:1fr 1fr">
      <div class="kpi-card"><div class="kpi-label">Total facturi</div><div class="kpi-value">${total} RON</div></div>
      <div class="kpi-card"><div class="kpi-label">De plata</div><div class="kpi-value" style="color:${unpaid>0?'var(--color-anchor)':'var(--color-anchor-2)'}">${unpaid} RON</div></div>
    </div>
    ${INVOICES.length === 0 ? '<div class="empty-state"><p>Nicio factura</p></div>' : renderTable(
      ['Numar','Data','Serviciu','Valoare','Status',''],
      INVOICES.map(i => [i.number, i.date, i.service, i.amount + ' RON', statusBadge(i.status),
        i.status === 'unpaid' ? `<button class="btn btn-primary btn-sm" onclick="payInvoice('${i.id}')">Plateste</button>` : '<span style="font-size:.7rem;color:var(--color-muted)">Achitata</span>'
      ])
    )}`;
}

function payInvoice(id) {
  const i = INVOICES.find(x => x.id === id);
  if (i) { i.status = 'paid'; saveInvoices(); toast('Factura platita!'); navigate('invoices'); }
}

/* ── Chat ── */
function renderChat() {
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Mesaje cu ${BUSINESS.name}</h2>
    <div class="chat-layout" style="height:calc(100vh - 240px)">
      <div class="chat-main" style="flex:1">
        <div class="chat-messages">${renderChatMessages()}</div>
        <div class="chat-input">
          <input class="form-input" type="text" id="chatMsgInput" placeholder="Scrie un mesaj..." onkeypress="if(event.key==='Enter')sendChatMessage()">
          <button class="btn btn-primary btn-sm" onclick="sendChatMessage()">Trimite</button>
        </div>
      </div>
    </div>`;
}

function renderChatMessages() {
  if (CHAT_MESSAGES.length === 0) return '<div class="empty-state"><p>Niciun mesaj. Scrie primul mesaj!</p></div>';
  return CHAT_MESSAGES.map(m => `
    <div class="chat-msg ${m.from === CUSTOMER.name ? 'own' : ''}">
      <div class="chat-msg-sender">${m.from}</div>
      <div class="chat-msg-text">${m.text}</div>
      <div class="chat-msg-time">${m.time}</div>
    </div>
  `).join('');
}

function sendChatMessage() {
  const input = document.getElementById('chatMsgInput');
  if (!input || !input.value.trim()) return;
  CHAT_MESSAGES.push({
    id: 'msg-' + Date.now(),
    from: CUSTOMER.name,
    text: input.value.trim(),
    time: new Date().toLocaleTimeString('ro-RO', {hour:'2-digit',minute:'2-digit'})
  });
  saveChatMessages(); refreshContent();
}

/* ── Loyalty ── */
function renderLoyalty() {
  const nextRedemption = REDEMPTIONS.find(r => r.points > CUSTOMER.loyaltyPoints) || REDEMPTIONS[REDEMPTIONS.length-1];
  return `
    <h2 style="font-family:var(--font-display);font-size:1.1rem;margin-bottom:var(--space-lg)">Loialitate &amp; Recompense</h2>
    <div class="loyalty-card" style="margin-bottom:var(--space-lg)">
      <div class="points">${CUSTOMER.loyaltyPoints}</div>
      <div class="label">puncte acumulate</div>
      <div style="margin-top:var(--space-sm);font-size:.75rem;opacity:.8">Urmatoarea recompensa: ${nextRedemption.reward} (${nextRedemption.points} puncte)</div>
    </div>
    <div class="card" style="margin-bottom:var(--space-lg)">
      <h3>Recompense disponibile</h3>
      ${REDEMPTIONS.map(r => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--color-rule)">
          <span style="font-size:.8rem">${r.reward}</span>
          <button class="btn btn-sm ${CUSTOMER.loyaltyPoints >= r.points ? 'btn-primary' : 'btn-outline'}" ${CUSTOMER.loyaltyPoints >= r.points ? `onclick="redeemPoints(${r.points},'${r.reward}')"` : 'disabled'}>${r.points} pct</button>
        </div>
      `).join('')}
    </div>
    <div class="card">
      <h3>Invita prieteni — castiga puncte</h3>
      <div class="referral-box">
        <span class="link">${REFERRAL.link}</span>
        <button class="btn btn-primary btn-sm" onclick="copyReferral()">Copiaza</button>
      </div>
      <p style="font-size:.75rem;color:var(--color-muted);margin-top:var(--space-sm)">${REFERRAL.totalReferred} prieteni invitati · ${REFERRAL.pointsEarned} puncte castigate</p>
    </div>
    <div class="card" style="margin-top:var(--space-lg)">
      <h3>Istoric puncte</h3>
      ${LOYALTY_HISTORY.map(l => `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--color-rule);font-size:.8rem"><span>${l.date} — ${l.description}</span><span style="font-weight:600;color:var(--color-anchor-2)">+${l.points}</span></div>`).join('')}
    </div>`;
}

function redeemPoints(points, reward) {
  if (CUSTOMER.loyaltyPoints >= points) {
    CUSTOMER.loyaltyPoints -= points;
    LOYALTY_HISTORY.push({ id:'loy-'+Date.now(), date:new Date().toISOString().slice(0,10), description:'Rascumparare: ' + reward, points: -points });
    saveLoyalty(); refreshContent(); toast('Recompensa activata!');
  }
}

function copyReferral() { navigator.clipboard?.writeText(REFERRAL.link); toast('Link copiat!'); }

/* ── Helpers ── */
function statusBadge(status) {
  const colors = { pending:'badge-pending', confirmed:'badge-confirmed', done:'badge-done', paid:'badge-paid', unpaid:'badge-unpaid' };
  return `<span class="badge ${colors[status]||'badge-pending'}">${status}</span>`;
}

function renderTable(headers, rows) {
  return `<table class="data-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function refreshContent() {
  const c = document.getElementById('cp-content');
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
  modalOverlayEl.innerHTML = `<div class="modal" style="background:#fff;border-radius:var(--radius-lg);padding:var(--space-xl);width:100%;max-width:480px;max-height:80vh;overflow-y:auto;box-shadow:0 20px 60px oklch(0% 0 0 / 20%)"><button style="float:right;background:none;border:none;font-size:1.25rem;cursor:pointer;color:var(--color-muted)" onclick="closeModal()">✕</button>${html}</div>`;
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