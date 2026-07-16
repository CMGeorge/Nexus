/* Mock data — realistic Romanian service business */
/* ── Branches (ADR-0010) ── */
const BRANCHES = {
  'inst-1': { id:'inst-1', name:'Instalatii Bucuresti', isInstitution:true, children:['branch-1','branch-2'] },
  'branch-1': { id:'branch-1', name:'Sediu Central', parentId:'inst-1', isInstitution:false },
  'branch-2': { id:'branch-2', name:'Sector 3', parentId:'inst-1', isInstitution:false },
};

/* ── Users (3 personas) ── */
const USERS = {
  owner:   { name:'Andrei Popescu',  role:'Admin',      initials:'AP', branch:'inst-1' },
  manager: { name:'Maria Ionescu',   role:'Manager',    initials:'MI', branch:'branch-1' },
  tech:    { name:'Ion Vasilescu',   role:'Tehnician',  initials:'IV', branch:'branch-1' },
};

/* ── Technicians ── */
const TECHNICIANS = [
  { name:'Ion Vasilescu',   phone:'0721 123 456', specialty:'Instalatii sanitare' },
  { name:'George Radu',     phone:'0722 234 567', specialty:'Aer conditionat' },
  { name:'Mihai Dobre',     phone:'0723 345 678', specialty:'Instalatii electrice' },
  { name:'Cristian Popa',   phone:'0724 456 789', specialty:'Centrale termice' },
  { name:'Alexandru Stoica',phone:'0725 567 890', specialty:'Reparatii urgente' },
];

/* ── Services ── */
const SERVICES = [
  'Reparatie boiler', 'Instalare aer conditionat', 'Verificare instalatie sanitara',
  'Montaj centrala termica', 'Desfundare teava', 'Revizie anuala',
  'Instalare panouri solare', 'Reparatie scurgere', 'Inlocuire calorifer',
  'Montaj cada dus', 'Instalare pompa caldura', 'Verificare instalatie electrica',
];

/* ── Customers ── */
var CUSTOMERS = JSON.parse(localStorage.getItem('nexus_customers')) || null;
if (!CUSTOMERS) {
  CUSTOMERS = [
    { id:'c1', name:'Alina Dumitrescu',  phone:'0722 111 222', email:'alina@email.ro',      address:'Str. Lipscani 12, Bucuresti',      totalJobs:7,  lastJob:'2026-07-16', createdAt:'2026-01-15', notes:'Client fidel, plata prompta' },
    { id:'c2', name:'Mihai Georgescu',   phone:'0733 222 333', email:'mihai@email.ro',       address:'Bd. Unirii 45, Bucuresti',         totalJobs:3,  lastJob:'2026-07-10', createdAt:'2026-03-20', notes:'Prefera programari dimineata' },
    { id:'c3', name:'Elena Stancu',      phone:'0744 333 444', email:'elena@email.ro',        address:'Str. Dorobanti 78, Bucuresti',     totalJobs:12, lastJob:'2026-07-16', createdAt:'2025-11-01', notes:'Contract service anual' },
    { id:'c4', name:'SC Construct SRL',  phone:'0755 444 555', email:'office@construct.ro',   address:'Splaiul Independentei 90',          totalJobs:5,  lastJob:'2026-07-14', createdAt:'2025-09-10', notes:'Firma constructii, comenzi regulate' },
    { id:'c5', name:'Andrei Munteanu',   phone:'0766 555 666', email:'andrei.m@email.ro',     address:'Calea Mosilor 200',                 totalJobs:1,  lastJob:'2026-07-17', createdAt:'2026-07-01', notes:'Client nou' },
    { id:'c6', name:'Ana Popa',          phone:'0777 666 777', email:'ana.popa@email.ro',     address:'Str. Mihai Bravu 55, Bucuresti',    totalJobs:4,  lastJob:'2026-07-08', createdAt:'2026-02-10', notes:'' },
    { id:'c7', name:'SC Tehno Instal SRL',phone:'0788 777 888',email:'contact@tehnoinstal.ro',address:'Sos. Oltenitei 120',                 totalJobs:9,  lastJob:'2026-07-12', createdAt:'2025-08-15', notes:'Partener colaborare' },
    { id:'c8', name:'Daniel Radu',       phone:'0799 888 999', email:'daniel.radu@email.ro',   address:'Str. Libertatii 33, Bucuresti',     totalJobs:2,  lastJob:'2026-07-05', createdAt:'2026-04-20', notes:'' },
  ];
  localStorage.setItem('nexus_customers', JSON.stringify(CUSTOMERS));
}

var APPOINTMENTS = JSON.parse(localStorage.getItem('nexus_appointments')) || null;
if (!APPOINTMENTS) {
  APPOINTMENTS = [
    { id:'a1', customerId:'c1', customer:'Alina Dumitrescu',  service:'Reparatie boiler',             date:'2026-07-16', time:'09:00', duration:'2h',  tech:'Ion Vasilescu',   branch:'branch-1', status:'confirmed', price:450,  notes:'' },
    { id:'a2', customerId:'c2', customer:'Mihai Georgescu',   service:'Instalare aer conditionat',     date:'2026-07-16', time:'11:00', duration:'4h',  tech:'George Radu',     branch:'branch-1', status:'confirmed', price:2800, notes:'Montaj la etajul 3' },
    { id:'a3', customerId:'c3', customer:'Elena Stancu',      service:'Verificare instalatie sanitara',date:'2026-07-16', time:'14:00', duration:'1h',  tech:'Ion Vasilescu',   branch:'branch-2', status:'done',     price:200,  notes:'Verificare periodica' },
    { id:'a4', customerId:'c4', customer:'SC Construct SRL',  service:'Montaj centrala termica',        date:'2026-07-17', time:'08:00', duration:'8h',  tech:'George Radu',     branch:'branch-2', status:'confirmed', price:6500, notes:'Centrala Viessmann 35kW' },
    { id:'a5', customerId:'c5', customer:'Andrei Munteanu',   service:'Desfundare teava',              date:'2026-07-17', time:'10:00', duration:'1h',  tech:'Ion Vasilescu',   branch:'branch-1', status:'confirmed', price:150,  notes:'' },
    { id:'a6', customerId:'c1', customer:'Alina Dumitrescu',  service:'Revizie anuala',                date:'2026-07-18', time:'09:00', duration:'2h',  tech:'Ion Vasilescu',   branch:'branch-1', status:'pending',  price:300,  notes:'' },
    { id:'a7', customerId:'c6', customer:'Ana Popa',          service:'Inlocuire calorifer',            date:'2026-07-18', time:'14:00', duration:'3h',  tech:'Mihai Dobre',     branch:'branch-1', status:'confirmed', price:850,  notes:'Aluminiu 10 elementi' },
    { id:'a8', customerId:'c7', customer:'SC Tehno Instal SRL',service:'Instalare pompa caldura',      date:'2026-07-19', time:'09:00', duration:'6h',  tech:'George Radu',     branch:'branch-2', status:'pending',  price:4500, notes:'Pompa Nibe 12kW' },
    { id:'a9', customerId:'c8', customer:'Daniel Radu',       service:'Reparatie scurgere',            date:'2026-07-19', time:'11:00', duration:'1h',  tech:'Ion Vasilescu',   branch:'branch-1', status:'pending',  price:180,  notes:'' },
    { id:'a10',customerId:'c2', customer:'Mihai Georgescu',   service:'Verificare instalatie electrica',date:'2026-07-20', time:'10:00', duration:'2h',  tech:'Mihai Dobre',     branch:'branch-1', status:'pending',  price:350,  notes:'Verificare dupa renovare' },
  ];
  localStorage.setItem('nexus_appointments', JSON.stringify(APPOINTMENTS));
}

var INVOICES = JSON.parse(localStorage.getItem('nexus_invoices')) || null;
if (!INVOICES) {
  INVOICES = [
    { id:'i1', number:'INV-2026-001', customer:'Alina Dumitrescu',  date:'2026-07-10', dueDate:'2026-07-25', amount:450,  status:'paid',   eFactura:'transmisa', apptId:'a1' },
    { id:'i2', number:'INV-2026-002', customer:'Elena Stancu',      date:'2026-07-15', dueDate:'2026-07-30', amount:200,  status:'unpaid', eFactura:'acceptata', apptId:'a3' },
    { id:'i3', number:'INV-2026-003', customer:'SC Construct SRL',  date:'2026-07-14', dueDate:'2026-07-29', amount:6500, status:'unpaid', eFactura:'neinviata', apptId:'a4' },
    { id:'i4', number:'INV-2026-004', customer:'Mihai Georgescu',   date:'2026-07-12', dueDate:'2026-07-27', amount:2800, status:'paid',   eFactura:'descarcata', apptId:'a2' },
    { id:'i5', number:'INV-2026-005', customer:'Andrei Munteanu',   date:'2026-07-08', dueDate:'2026-07-23', amount:150,  status:'paid',   eFactura:'transmisa', apptId:'a5' },
    { id:'i6', number:'INV-2026-006', customer:'Alina Dumitrescu',  date:'2026-07-16', dueDate:'2026-07-31', amount:300,  status:'unpaid', eFactura:'neinviata', apptId:'a6' },
  ];
  localStorage.setItem('nexus_invoices', JSON.stringify(INVOICES));
}

/* ── Helpers ── */
let nextApptId = 11;
let nextCustId = 9;
let nextInvId = 7;

function getNextId(prefix) {
  const map = { appt:nextApptId++, cust:nextCustId++, inv:nextInvId++ };
  return prefix + map[prefix];
}

function saveAppointments() { localStorage.setItem('nexus_appointments', JSON.stringify(APPOINTMENTS)); }
function saveCustomers() { localStorage.setItem('nexus_customers', JSON.stringify(CUSTOMERS)); }
function saveInvoices() { localStorage.setItem('nexus_invoices', JSON.stringify(INVOICES)); }
function saveTasks() { localStorage.setItem('nexus_tasks', JSON.stringify(TASKS)); }
function saveChatData() { localStorage.setItem('nexus_chatMessages', JSON.stringify(CHAT_MESSAGES)); localStorage.setItem('nexus_chatChannels', JSON.stringify(CHAT_CHANNELS)); }

/* ── Tasks (internal) ── */
let TASKS = [
  { id:'tsk-1', title:'Verificare stoc piese', assignedTo:'Ion Vasilescu', priority:'high',    dueDate:'2026-07-17', status:'in-progress', createdBy:'Maria Ionescu' },
  { id:'tsk-2', title:'Curatenie depozit',   assignedTo:'George Radu',   priority:'medium',  dueDate:'2026-07-20', status:'todo',        createdBy:'Maria Ionescu' },
  { id:'tsk-3', title:'Actualizare preturi', assignedTo:'Maria Ionescu', priority:'low',     dueDate:'2026-07-25', status:'todo',        createdBy:'Andrei Popescu' },
  { id:'tsk-4', title:'Scos gunoi reciclabil',assignedTo:'Alexandru Stoica',priority:'low',  dueDate:'2026-07-16', status:'done',        createdBy:'Maria Ionescu' },
];

/* ── Chat (internal team) ── */
let activeChannel = 'ch-1';
let CHAT_CHANNELS = [
  { id:'ch-1', name:'Echipa',       lastMsg:'Am terminat interventia', time:'10:45' },
  { id:'ch-2', name:'Urgente',      lastMsg:'Cine poate prelua?',      time:'09:30' },
  { id:'ch-3', name:'Sediu Central',lastMsg:'Sedinta la 14:00',        time:'08:00' },
];
let CHAT_MESSAGES = [
  { id:'msg-1', channelId:'ch-1', from:'Ion Vasilescu',   text:'Am terminat interventia',   time:'10:45' },
  { id:'msg-2', channelId:'ch-1', from:'Maria Ionescu',   text:'Super, ai trimis factura?', time:'10:46' },
  { id:'msg-3', channelId:'ch-1', from:'Ion Vasilescu',   text:'Da, am facut-o acum.',      time:'10:47' },
  { id:'msg-4', channelId:'ch-2', from:'George Radu',     text:'Cine poate prelua o urgenta in Militari?', time:'09:30' },
  { id:'msg-5', channelId:'ch-3', from:'Andrei Popescu',  text:'Sedinta la 14:00',          time:'08:00' },
];

(function loadPersisted() {
  try {
    const a = localStorage.getItem('nexus_appointments');
    if (a) APPOINTMENTS = JSON.parse(a);
    const c = localStorage.getItem('nexus_customers');
    if (c) CUSTOMERS = JSON.parse(c);
    const i = localStorage.getItem('nexus_invoices');
    if (i) INVOICES = JSON.parse(i);
    const t = localStorage.getItem('nexus_tasks');
    if (t) TASKS = JSON.parse(t);
    const cm = localStorage.getItem('nexus_chatMessages');
    if (cm) CHAT_MESSAGES = JSON.parse(cm);
    const cc = localStorage.getItem('nexus_chatChannels');
    if (cc) CHAT_CHANNELS = JSON.parse(cc);
  } catch(e) { /* ignore corrupt localStorage */ }
})();

function toast(msg, type) {
  const c = document.getElementById('toastContainer');
  if (!c) return;
  const t = document.createElement('div');
  t.className = 'toast toast-' + (type||'success');
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity='0'; t.style.transition='opacity .3s'; setTimeout(()=>t.remove(),300); }, 3000);
}

/* ── State ── */
var currentUser = USERS.owner;
var currentBranch = BRANCHES['inst-1'];
var currentView = 'dashboard';
var searchQuery = '';
var statusFilter = 'all';