/* Nexus Client Portal — Mock Data */

/* ── Sample Customer ── */
const CUSTOMER = {
  id: 'cust-1', name: 'Elena Dumitrescu', email: 'elena@email.ro', phone: '0723 111 222',
  address: 'Str. Mihai Eminescu 42, Bucuresti',
  joinedAt: '2025-03-15', loyaltyPoints: 340
};

/* ── Business (the company this customer belongs to) ── */
const BUSINESS = {
  name: 'Instalatii Bucuresti', phone: '0721 123 456', email: 'contact@instalatiibucuresti.ro'
};

/* ── Appointments (customer's) ── */
let APPOINTMENTS = [
  { id:'apt-1', date:'2026-07-16', time:'10:00', service:'Verificare instalatie sanitara', technician:'Ion Vasilescu', status:'confirmed', notes:'' },
  { id:'apt-2', date:'2026-08-02', time:'14:00', service:'Revizie anuala centrala', technician:'Cristian Popa', status:'pending', notes:'Clientul a cerut programare dupa-amiaza' },
  { id:'apt-3', date:'2026-06-10', time:'09:00', service:'Desfundare teava bucatarie', technician:'Alexandru Stoica', status:'done', notes:'Rezolvat in 45 min' },
  { id:'apt-4', date:'2026-05-20', time:'11:00', service:'Montaj cada dus', technician:'George Radu', status:'done', notes:'' },
];

/* ── Invoices (customer's) ── */
let INVOICES = [
  { id:'inv-1', number:'INV-2026-045', date:'2026-06-10', dueDate:'2026-06-25', amount:350, status:'paid', service:'Desfundare teava bucatarie' },
  { id:'inv-2', number:'INV-2026-038', date:'2026-05-20', dueDate:'2026-06-04', amount:1200, status:'paid', service:'Montaj cada dus' },
  { id:'inv-3', number:'INV-2026-052', date:'2026-07-16', dueDate:'2026-07-31', amount:200, status:'unpaid', service:'Verificare instalatie sanitara' },
];

/* ── Loyalty History ── */
let LOYALTY_HISTORY = [
  { id:'loy-1', date:'2026-07-16', description:'Programare — Verificare instalatie', points: 50 },
  { id:'loy-2', date:'2026-06-10', description:'Programare — Desfundare teava', points: 50 },
  { id:'loy-3', date:'2026-05-20', description:'Programare — Montaj cada dus', points: 100 },
  { id:'loy-4', date:'2026-04-15', description:'Referral — prieten inscris', points: 80 },
  { id:'loy-5', date:'2026-03-20', description:'Bonus inscriere', points: 60 },
];

/* ── Redemption Options ── */
const REDEMPTIONS = [
  { points: 100, reward: '10% reducere la urmatoarea programare' },
  { points: 250, reward: '25% reducere la urmatoarea programare' },
  { points: 500, reward: 'O verificare gratuita' },
  { points: 1000, reward: 'O interventie gratuita (pana la 500 RON)' },
];

/* ── Referral ── */
const REFERRAL = { code: 'ELENA25', link: 'https://instalatiibucuresti.nexus.ro/ref/ELENA25', totalReferred: 3, pointsEarned: 240 };

/* ── Services (for booking) ── */
const SERVICES = [
  'Reparatie boiler', 'Instalare aer conditionat', 'Verificare instalatie sanitara',
  'Montaj centrala termica', 'Desfundare teava', 'Revizie anuala',
  'Inlocuire calorifer', 'Montaj cada dus', 'Verificare instalatie electrica',
];

/* ── Chat ── */
let CHAT_MESSAGES = [
  { id:'msg-1', from:'Elena Dumitrescu', text:'Buna ziua! As dori sa reprogramez interventia de maine.', time:'09:15' },
  { id:'msg-2', from:'Instalatii Bucuresti', text:'Buna ziua! Sigur, cand ati dori sa reprogramam?', time:'09:20' },
  { id:'msg-3', from:'Elena Dumitrescu', text:'Miercuri dupa-amiaza, daca se poate.', time:'09:22' },
  { id:'msg-4', from:'Instalatii Bucuresti', text:'Perfect. Avem disponibil miercuri la ora 15:00. Confirmati?', time:'09:25' },
];

/* ── Persistence ── */
function saveAppointments() { localStorage.setItem('cp_appointments', JSON.stringify(APPOINTMENTS)); }
function saveInvoices() { localStorage.setItem('cp_invoices', JSON.stringify(INVOICES)); }
function saveChatMessages() { localStorage.setItem('cp_chatMessages', JSON.stringify(CHAT_MESSAGES)); }
function saveLoyalty() { localStorage.setItem('cp_loyalty', JSON.stringify(LOYALTY_HISTORY)); }

(function loadPersisted() {
  try {
    const a = localStorage.getItem('cp_appointments'); if (a) APPOINTMENTS = JSON.parse(a);
    const i = localStorage.getItem('cp_invoices'); if (i) INVOICES = JSON.parse(i);
    const c = localStorage.getItem('cp_chatMessages'); if (c) CHAT_MESSAGES = JSON.parse(c);
    const l = localStorage.getItem('cp_loyalty'); if (l) LOYALTY_HISTORY = JSON.parse(l);
  } catch(e) {}
})();