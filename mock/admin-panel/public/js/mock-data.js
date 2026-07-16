/* Nexus Admin Panel — Mock Data (platform-level) */

/* ── Platform Admin ── */
const ADMIN = { name: 'Catalin Georgescu', role: 'Platform Admin', email: 'catalin@wesell.ro' };

/* ── Companies (tenants) ── */
let COMPANIES = [
  { id:'comp-1', name:'Instalatii Bucuresti', domain:'instalatiibucuresti.nexus.ro', plan:'Professional', status:'active', users:12, revenue:45800, joinedAt:'2025-01-10' },
  { id:'comp-2', name:'CrisClima HVAC', domain:'crisclima.nexus.ro', plan:'Business', status:'active', users:8, revenue:32400, joinedAt:'2025-02-20' },
  { id:'comp-3', name:'ElectroService TM', domain:'electroservice.nexus.ro', plan:'Starter', status:'suspended', users:3, revenue:8900, joinedAt:'2025-04-05' },
  { id:'comp-4', name:'TermoPlus Iasi', domain:'termoplus.nexus.ro', plan:'Professional', status:'pending', users:1, revenue:0, joinedAt:'2026-07-14' },
];

/* ── Platform KPIs ── */
const KPIS = {
  totalBusinesses: 4, totalBusinessesChange: '+1 luna aceasta',
  activeUsers: 24, activeUsersChange: '+3 luna aceasta',
  totalRevenue: 87100, totalRevenueChange: '+12% vs luna trecuta',
  appointmentsToday: 8, appointmentsTodayChange: '+2 fata de ieri',
};

/* ── Revenue Chart (last 6 months) ── */
const REVENUE_CHART = [
  { month:'Feb', value:12000 }, { month:'Mar', value:14500 },
  { month:'Apr', value:13800 }, { month:'Mai', value:16200 },
  { month:'Iun', value:15100 }, { month:'Iul', value:15500 },
];

/* ── User Growth Chart ── */
const USER_GROWTH = [
  { month:'Feb', value:14 }, { month:'Mar', value:16 },
  { month:'Apr', value:18 }, { month:'Mai', value:20 },
  { month:'Iun', value:22 }, { month:'Iul', value:24 },
];

/* ── Audit Logs ── */
let AUDIT_LOGS = [
  { id:'log-1', time:'10:45', company:'Instalatii Bucuresti', user:'Andrei Popescu', action:'factura.creata', detail:'Factura INV-2026-045 — 350 RON' },
  { id:'log-2', time:'10:30', company:'CrisClima HVAC', user:'Maria Ionescu', action:'programare.confirmata', detail:'Programare #234 — Verificare AC' },
  { id:'log-3', time:'10:15', company:'Instalatii Bucuresti', user:'Ion Vasilescu', action:'interventie.finalizata', detail:'Interventie #112 — Desfundare teava' },
  { id:'log-4', time:'09:50', company:'ElectroService TM', user:'Admin', action:'companie.suspendata', detail:'Suspendat pentru neplata — 45 zile' },
  { id:'log-5', time:'09:30', company:'Instalatii Bucuresti', user:'Andrei Popescu', action:'client.adaugat', detail:'Client nou: Elena Dumitrescu' },
  { id:'log-6', time:'09:00', company:'TermoPlus Iasi', user:'Sorin Munteanu', action:'cont.creat', detail:'Inregistrare companie noua — plan Professional' },
  { id:'log-7', time:'08:45', company:'Instalatii Bucuresti', user:'Maria Ionescu', action:'task.asignat', detail:'Task "Verificare stoc" → Ion Vasilescu' },
  { id:'log-8', time:'08:30', company:'CrisClima HVAC', user:'Admin', action:'rol.modificat', detail:'User promovat la Manager' },
];

/* ── Pricing Tiers ── */
let PRICING_TIERS = [
  { id:'tier-1', name:'Starter', price:99, period:'luna', features:['Pana la 3 utilizatori','Pana la 100 clienti','Programari','Facturi','Suport email'], active:true },
  { id:'tier-2', name:'Professional', price:249, period:'luna', features:['Pana la 10 utilizatori','Clienti nelimitati','Programari + Taskuri','Facturi + eFactura','Chat intern','Suport prioritar'], active:true },
  { id:'tier-3', name:'Business', price:499, period:'luna', features:['Pana la 25 utilizatori','Toate functionalitatile','Portal client','Loialitate & Referral','Website booking','Suport 24/7'], active:true },
];

/* ── Feature Flags ── */
let FEATURE_FLAGS = [
  { id:'ff-1', name:'eFactura Automat', description:'Generare automata XML CIUS-RO la fiecare factura', tiers:['Professional','Business'], enabled:true },
  { id:'ff-2', name:'Chat Clienti', description:'Mesagerie directa intre client si business', tiers:['Business'], enabled:true },
  { id:'ff-3', name:'Website Booking', description:'Generator pagini booking pentru clienti', tiers:['Business'], enabled:false },
  { id:'ff-4', name:'Loyalty Program', description:'Puncte de loialitate si program referral', tiers:['Business'], enabled:true },
  { id:'ff-5', name:'API Access', description:'Acces REST API pentru integrari externe', tiers:['Professional','Business'], enabled:false },
];

/* ── Email Templates ── */
const EMAIL_TEMPLATES = [
  { id:'tpl-1', name:'Confirmare programare', subject:'Programarea ta la {{business}}', updatedAt:'2026-06-15' },
  { id:'tpl-2', name:'Factura generata', subject:'Factura {{number}} — {{business}}', updatedAt:'2026-06-10' },
  { id:'tpl-3', name:'Bun venit client nou', subject:'Bine ai venit la {{business}}!', updatedAt:'2026-05-20' },
  { id:'tpl-4', name:'Resetare parola', subject:'Resetare parola — {{business}}', updatedAt:'2026-04-01' },
];

/* ── Persistence ── */
function saveCompanies() { localStorage.setItem('ap_companies', JSON.stringify(COMPANIES)); }
function saveAuditLogs() { localStorage.setItem('ap_auditLogs', JSON.stringify(AUDIT_LOGS)); }
function savePricingTiers() { localStorage.setItem('ap_pricingTiers', JSON.stringify(PRICING_TIERS)); }
function saveFeatureFlags() { localStorage.setItem('ap_featureFlags', JSON.stringify(FEATURE_FLAGS)); }

(function loadPersisted() {
  try {
    const c = localStorage.getItem('ap_companies'); if (c) COMPANIES = JSON.parse(c);
    const a = localStorage.getItem('ap_auditLogs'); if (a) AUDIT_LOGS = JSON.parse(a);
    const p = localStorage.getItem('ap_pricingTiers'); if (p) PRICING_TIERS = JSON.parse(p);
    const f = localStorage.getItem('ap_featureFlags'); if (f) FEATURE_FLAGS = JSON.parse(f);
  } catch(e) {}
})();