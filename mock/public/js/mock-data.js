/* Mock data — realistic Romanian service business */
const BRANCHES = {
  'inst-1': {
    id:'inst-1', name:'Instalatii Bucuresti', isInstitution:true,
    children:['branch-1','branch-2']
  },
  'branch-1': { id:'branch-1', name:'Sediu Central', parentId:'inst-1', isInstitution:false },
  'branch-2': { id:'branch-2', name:'Sector 3', parentId:'inst-1', isInstitution:false },
};

const USERS = {
  owner: { name:'Andrei Popescu', role:'Admin', initials:'AP', branch:'inst-1' },
  manager: { name:'Maria Ionescu', role:'Manager', initials:'MI', branch:'branch-1' },
  tech: { name:'Ion Vasilescu', role:'Tehnician', initials:'IV', branch:'branch-1' },
};

const CUSTOMERS = [
  { id:'c1', name:'Alina Dumitrescu', phone:'0722 111 222', email:'alina@email.ro', address:'Str. Lipscani 12, Bucuresti', totalJobs:7 },
  { id:'c2', name:'Mihai Georgescu', phone:'0733 222 333', email:'mihai@email.ro', address:'Bd. Unirii 45, Bucuresti', totalJobs:3 },
  { id:'c3', name:'Elena Stancu', phone:'0744 333 444', email:'elena@email.ro', address:'Str. Dorobanti 78, Bucuresti', totalJobs:12 },
  { id:'c4', name:'SC Construct SRL', phone:'0755 444 555', email:'office@construct.ro', address:'Splaiul Independentei 90', totalJobs:5 },
  { id:'c5', name:'Andrei Munteanu', phone:'0766 555 666', email:'andrei.m@email.ro', address:'Calea Mosilor 200', totalJobs:1 },
];

const APPOINTMENTS = [
  { id:'a1', customerId:'c1', customer:'Alina Dumitrescu', service:'Reparatie boiler', date:'2026-07-16', time:'09:00', duration:'2h', tech:'Ion Vasilescu', branch:'branch-1', status:'confirmed', price:450 },
  { id:'a2', customerId:'c2', customer:'Mihai Georgescu', service:'Instalare aer conditionat', date:'2026-07-16', time:'11:00', duration:'4h', tech:'George Radu', branch:'branch-1', status:'pending', price:2800 },
  { id:'a3', customerId:'c3', customer:'Elena Stancu', service:'Verificare instalatie sanitara', date:'2026-07-16', time:'14:00', duration:'1h', tech:'Ion Vasilescu', branch:'branch-2', status:'done', price:200 },
  { id:'a4', customerId:'c4', customer:'SC Construct SRL', service:'Montaj centrala termica', date:'2026-07-17', time:'08:00', duration:'8h', tech:'George Radu', branch:'branch-2', status:'confirmed', price:6500 },
  { id:'a5', customerId:'c5', customer:'Andrei Munteanu', service:'Desfundare teava', date:'2026-07-17', time:'10:00', duration:'1h', tech:'Ion Vasilescu', branch:'branch-1', status:'confirmed', price:150 },
  { id:'a6', customerId:'c1', customer:'Alina Dumitrescu', service:'Revizie anuala', date:'2026-07-18', time:'09:00', duration:'2h', tech:'Ion Vasilescu', branch:'branch-1', status:'pending', price:300 },
];

const INVOICES = [
  { id:'i1', number:'INV-2026-001', customer:'Alina Dumitrescu', date:'2026-07-10', dueDate:'2026-07-25', amount:450, status:'paid' },
  { id:'i2', number:'INV-2026-002', customer:'Elena Stancu', date:'2026-07-15', dueDate:'2026-07-30', amount:200, status:'unpaid' },
  { id:'i3', number:'INV-2026-003', customer:'SC Construct SRL', date:'2026-07-14', dueDate:'2026-07-29', amount:6500, status:'unpaid' },
  { id:'i4', number:'INV-2026-004', customer:'Mihai Georgescu', date:'2026-07-12', dueDate:'2026-07-27', amount:2800, status:'paid' },
  { id:'i5', number:'INV-2026-005', customer:'Andrei Munteanu', date:'2026-07-08', dueDate:'2026-07-23', amount:150, status:'paid' },
];

let currentUser = USERS.owner;
let currentBranch = BRANCHES['inst-1'];
let currentView = 'dashboard';