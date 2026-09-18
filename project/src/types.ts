export type EmployeeStatus = 'active' | 'inactive' | 'on_leave';

export type CertStatus = 'vigente' | 'proxima' | 'vencida';

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  issueDate: string;
  expiryDate: string;
  status: CertStatus;
  credentialId: string;
  documentUrl?: string;
}

export interface DocumentItem {
  id: string;
  name: string;
  type: string;
  uploadedAt: string;
  size: string;
}

export interface HistoryEntry {
  id: string;
  date: string;
  action: string;
  detail: string;
  user: string;
}

export interface Employee {
  id: string;
  firstName: string;
  lastName: string;
  avatarColor: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  status: EmployeeStatus;
  hireDate: string;
  location: string;
  certifications: Certification[];
  documents: DocumentItem[];
  history: HistoryEntry[];
}

export interface ActivityItem {
  id: string;
  type: 'cert_added' | 'cert_expiring' | 'cert_expired' | 'employee_added' | 'employee_updated';
  message: string;
  time: string;
}

export type Page = 'dashboard' | 'personnel' | 'profile' | 'certifications';
