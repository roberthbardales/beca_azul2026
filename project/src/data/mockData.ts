import type { Employee, ActivityItem, CertStatus, Certification } from '../types';

export const departments = [
  'Tecnología de la Información',
  'Recursos Humanos',
  'Operaciones',
  'Finanzas',
  'Seguridad y Cumplimiento',
  'Logística',
  'Marketing',
  'Ventas',
];

export const positions = [
  'Analista de Sistemas',
  'Gerente de Proyecto',
  'Desarrollador Senior',
  'Especialista en Seguridad',
  'Coordinador de RRHH',
  'Inspector de Calidad',
  'Técnico de Campo',
  'Supervisor de Operaciones',
  'Contador',
  'Analista Financiero',
];

export const certTypes = [
  'ISO 9001',
  'ISO 27001',
  'PMP',
  'ITIL Foundation',
  'AWS Solutions Architect',
  'Scrum Master',
  'OHSAS 18001',
  'Six Sigma Green Belt',
  'CISM',
  'CISSP',
];

function calcStatus(expiry: string): CertStatus {
  const now = new Date('2026-09-18');
  const exp = new Date(expiry);
  const days = Math.floor((exp.getTime() - now.getTime()) / 86400000);
  if (days < 0) return 'vencida';
  if (days <= 30) return 'proxima';
  return 'vigente';
}

export const employees: Employee[] = [
  {
    id: '1',
    firstName: 'María',
    lastName: 'González',
    avatarColor: '#3361f1',
    email: 'maria.gonzalez@empresa.com',
    phone: '+34 611 22 33 44',
    position: 'Gerente de Proyecto',
    department: 'Tecnología de la Información',
    status: 'active',
    hireDate: '2021-03-15',
    location: 'Madrid, ES',
    certifications: [
      { id: 'c1', name: 'PMP', issuer: 'PMI', issueDate: '2024-01-10', expiryDate: '2027-01-10', status: 'vigente', credentialId: 'PMP-2024-001' },
      { id: 'c2', name: 'Scrum Master', issuer: 'Scrum Alliance', issueDate: '2025-06-01', expiryDate: '2026-10-05', status: 'proxima', credentialId: 'CSM-2025-882' },
      { id: 'c3', name: 'ITIL Foundation', issuer: 'AXELOS', issueDate: '2022-09-01', expiryDate: '2025-09-01', status: 'vencida', credentialId: 'ITIL-2022-455' },
    ],
    documents: [
      { id: 'd1', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2021-03-16', size: '1.2 MB' },
      { id: 'd2', name: 'Identificación oficial.pdf', type: 'PDF', uploadedAt: '2021-03-16', size: '0.8 MB' },
      { id: 'd3', name: 'Comprobante de domicilio.pdf', type: 'PDF', uploadedAt: '2021-03-18', size: '0.5 MB' },
    ],
    history: [
      { id: 'h1', date: '2025-06-01', action: 'Certificación agregada', detail: 'Scrum Master (Scrum Alliance)', user: 'Carlos Ruiz' },
      { id: 'h2', date: '2024-01-10', action: 'Certificación agregada', detail: 'PMP (PMI)', user: 'Carlos Ruiz' },
      { id: 'h3', date: '2023-08-15', action: 'Cambio de cargo', detail: 'Promovido a Gerente de Proyecto', user: 'Ana Torres' },
    ],
  },
  {
    id: '2',
    firstName: 'Carlos',
    lastName: 'Mendoza',
    avatarColor: '#10b07a',
    email: 'carlos.mendoza@empresa.com',
    phone: '+34 622 33 44 55',
    position: 'Especialista en Seguridad',
    department: 'Seguridad y Cumplimiento',
    status: 'active',
    hireDate: '2020-07-01',
    location: 'Barcelona, ES',
    certifications: [
      { id: 'c4', name: 'CISSP', issuer: 'ISC²', issueDate: '2023-05-20', expiryDate: '2026-05-20', status: 'vigente', credentialId: 'CISSP-2023-77' },
      { id: 'c5', name: 'CISM', issuer: 'ISACA', issueDate: '2024-09-10', expiryDate: '2027-09-10', status: 'vigente', credentialId: 'CISM-2024-12' },
      { id: 'c6', name: 'ISO 27001', issuer: 'ISO', issueDate: '2024-03-01', expiryDate: '2027-03-01', status: 'vigente', credentialId: 'ISO27K-2024-9' },
    ],
    documents: [
      { id: 'd4', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2020-07-02', size: '1.1 MB' },
    ],
    history: [
      { id: 'h4', date: '2024-09-10', action: 'Certificación agregada', detail: 'CISM (ISACA)', user: 'María González' },
      { id: 'h5', date: '2024-03-01', action: 'Certificación agregada', detail: 'ISO 27001 (ISO)', user: 'María González' },
    ],
  },
  {
    id: '3',
    firstName: 'Lucía',
    lastName: 'Fernández',
    avatarColor: '#f29910',
    email: 'lucia.fernandez@empresa.com',
    phone: '+34 633 44 55 66',
    position: 'Coordinador de RRHH',
    department: 'Recursos Humanos',
    status: 'on_leave',
    hireDate: '2019-11-20',
    location: 'Valencia, ES',
    certifications: [
      { id: 'c7', name: 'ISO 9001', issuer: 'ISO', issueDate: '2023-02-15', expiryDate: '2026-02-15', status: 'vigente', credentialId: 'ISO9K-2023-3' },
      { id: 'c8', name: 'Six Sigma Green Belt', issuer: 'ASQ', issueDate: '2024-04-01', expiryDate: '2026-09-25', status: 'proxima', credentialId: 'SSGB-2024-55' },
    ],
    documents: [
      { id: 'd5', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2019-11-21', size: '1.3 MB' },
      { id: 'd6', name: 'Título universitario.pdf', type: 'PDF', uploadedAt: '2019-11-21', size: '2.0 MB' },
    ],
    history: [
      { id: 'h6', date: '2024-04-01', action: 'Certificación agregada', detail: 'Six Sigma Green Belt (ASQ)', user: 'Carlos Ruiz' },
    ],
  },
  {
    id: '4',
    firstName: 'Javier',
    lastName: 'Ruiz',
    avatarColor: '#dc2626',
    email: 'javier.ruiz@empresa.com',
    phone: '+34 644 55 66 77',
    position: 'Desarrollador Senior',
    department: 'Tecnología de la Información',
    status: 'active',
    hireDate: '2022-01-10',
    location: 'Madrid, ES',
    certifications: [
      { id: 'c9', name: 'AWS Solutions Architect', issuer: 'Amazon', issueDate: '2023-08-01', expiryDate: '2026-08-01', status: 'vigente', credentialId: 'AWS-SAA-2023-401' },
      { id: 'c10', name: 'Scrum Master', issuer: 'Scrum Alliance', issueDate: '2022-03-01', expiryDate: '2025-03-01', status: 'vencida', credentialId: 'CSM-2022-110' },
    ],
    documents: [
      { id: 'd7', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2022-01-11', size: '1.0 MB' },
    ],
    history: [
      { id: 'h7', date: '2023-08-01', action: 'Certificación agregada', detail: 'AWS Solutions Architect (Amazon)', user: 'María González' },
    ],
  },
  {
    id: '5',
    firstName: 'Elena',
    lastName: 'Torres',
    avatarColor: '#7c3aed',
    email: 'elena.torres@empresa.com',
    phone: '+34 655 66 77 88',
    position: 'Analista Financiero',
    department: 'Finanzas',
    status: 'inactive',
    hireDate: '2018-05-12',
    location: 'Sevilla, ES',
    certifications: [
      { id: 'c11', name: 'Six Sigma Green Belt', issuer: 'ASQ', issueDate: '2022-06-01', expiryDate: '2025-06-01', status: 'vencida', credentialId: 'SSGB-2022-88' },
    ],
    documents: [
      { id: 'd8', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2018-05-13', size: '1.1 MB' },
    ],
    history: [
      { id: 'h8', date: '2022-06-01', action: 'Certificación agregada', detail: 'Six Sigma Green Belt (ASQ)', user: 'Ana Torres' },
      { id: 'h9', date: '2025-01-15', action: 'Cambio de estado', detail: 'Dado de baja', user: 'Ana Torres' },
    ],
  },
  {
    id: '6',
    firstName: 'Diego',
    lastName: 'Sánchez',
    avatarColor: '#0891b2',
    email: 'diego.sanchez@empresa.com',
    phone: '+34 666 77 88 99',
    position: 'Técnico de Campo',
    department: 'Operaciones',
    status: 'active',
    hireDate: '2023-02-01',
    location: 'Bilbao, ES',
    certifications: [
      { id: 'c12', name: 'OHSAS 18001', issuer: 'BSI', issueDate: '2024-01-15', expiryDate: '2027-01-15', status: 'vigente', credentialId: 'OHSAS-2024-7' },
      { id: 'c13', name: 'ISO 9001', issuer: 'ISO', issueDate: '2024-06-01', expiryDate: '2027-06-01', status: 'vigente', credentialId: 'ISO9K-2024-21' },
    ],
    documents: [
      { id: 'd9', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2023-02-02', size: '1.2 MB' },
    ],
    history: [
      { id: 'h10', date: '2024-06-01', action: 'Certificación agregada', detail: 'ISO 9001 (ISO)', user: 'Carlos Ruiz' },
    ],
  },
  {
    id: '7',
    firstName: 'Sofía',
    lastName: 'Ramírez',
    avatarColor: '#db2777',
    email: 'sofia.ramirez@empresa.com',
    phone: '+34 677 88 99 00',
    position: 'Supervisor de Operaciones',
    department: 'Logística',
    status: 'active',
    hireDate: '2021-09-05',
    location: 'Madrid, ES',
    certifications: [
      { id: 'c14', name: 'PMP', issuer: 'PMI', issueDate: '2023-04-10', expiryDate: '2026-04-10', status: 'vigente', credentialId: 'PMP-2023-055' },
      { id: 'c15', name: 'ITIL Foundation', issuer: 'AXELOS', issueDate: '2024-02-01', expiryDate: '2026-10-01', status: 'proxima', credentialId: 'ITIL-2024-300' },
    ],
    documents: [
      { id: 'd10', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2021-09-06', size: '1.0 MB' },
    ],
    history: [
      { id: 'h11', date: '2024-02-01', action: 'Certificación agregada', detail: 'ITIL Foundation (AXELOS)', user: 'María González' },
    ],
  },
  {
    id: '8',
    firstName: 'Pablo',
    lastName: 'Castro',
    avatarColor: '#16a34a',
    email: 'pablo.castro@empresa.com',
    phone: '+34 688 99 00 11',
    position: 'Inspector de Calidad',
    department: 'Operaciones',
    status: 'active',
    hireDate: '2022-06-15',
    location: 'Zaragoza, ES',
    certifications: [
      { id: 'c16', name: 'ISO 9001', issuer: 'ISO', issueDate: '2023-03-01', expiryDate: '2026-03-01', status: 'vigente', credentialId: 'ISO9K-2023-12' },
      { id: 'c17', name: 'Six Sigma Green Belt', issuer: 'ASQ', issueDate: '2023-09-01', expiryDate: '2026-09-01', status: 'vencida', credentialId: 'SSGB-2023-44' },
    ],
    documents: [
      { id: 'd11', name: 'Contrato laboral.pdf', type: 'PDF', uploadedAt: '2022-06-16', size: '1.1 MB' },
    ],
    history: [
      { id: 'h12', date: '2023-09-01', action: 'Certificación agregada', detail: 'Six Sigma Green Belt (ASQ)', user: 'Carlos Ruiz' },
    ],
  },
];

// Recalc statuses from dates to keep consistency
for (const e of employees) {
  for (const c of e.certifications) {
    c.status = calcStatus(c.expiryDate);
  }
}

export const activityFeed: ActivityItem[] = [
  { id: 'a1', type: 'cert_expiring', message: 'La certificación "Scrum Master" de María González vence en 17 días', time: 'Hace 2 horas' },
  { id: 'a2', type: 'cert_added', message: 'Carlos Mendoza agregó la certificación "CISM"', time: 'Hace 1 día' },
  { id: 'a3', type: 'cert_expired', message: 'La certificación "ITIL Foundation" de Javier Ruiz ha vencido', time: 'Hace 2 días' },
  { id: 'a4', type: 'employee_updated', message: 'Se actualizó la información de Lucía Fernández', time: 'Hace 3 días' },
  { id: 'a5', type: 'cert_expiring', message: 'La certificación "ITIL Foundation" de Sofía Ramírez vence en 13 días', time: 'Hace 4 días' },
  { id: 'a6', type: 'employee_added', message: 'Se registró a Pablo Castro en el sistema', time: 'Hace 5 días' },
];

export function allCertifications() {
  const list: { cert: Certification; employee: Employee }[] = [];
  for (const e of employees) {
    for (const c of e.certifications) {
      list.push({ cert: c, employee: e });
    }
  }
  return list;
}
