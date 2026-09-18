import { useState } from 'react';
import type { Page, Employee, Certification } from '@/types';
import { employees } from '@/data/mockData';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { DashboardPage } from '@/pages/DashboardPage';
import { PersonnelPage } from '@/pages/PersonnelPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { CertificationsPage } from '@/pages/CertificationsPage';
import { EmployeeFormModal } from '@/components/forms/EmployeeFormModal';
import { CertFormModal } from '@/components/forms/CertFormModal';

function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | undefined>();
  const [mobileSidebar, setMobileSidebar] = useState(false);

  // Modal states
  const [employeeModalOpen, setEmployeeModalOpen] = useState(false);
  const [employeeModalMode, setEmployeeModalMode] = useState<'create' | 'edit'>('create');
  const [editingEmployee, setEditingEmployee] = useState<Employee | undefined>();

  const [certModalOpen, setCertModalOpen] = useState(false);
  const [certModalMode, setCertModalMode] = useState<'create' | 'edit'>('create');
  const [certEmployee, setCertEmployee] = useState<Employee | undefined>();
  const [editingCert, setEditingCert] = useState<Certification | undefined>();

  const selectedEmployee = employees.find((e) => e.id === selectedEmployeeId);

  const navigate = (p: Page, employeeId?: string) => {
    setPage(p);
    if (employeeId) setSelectedEmployeeId(employeeId);
    setMobileSidebar(false);
    window.scrollTo(0, 0);
  };

  const openCreateEmployee = () => {
    setEmployeeModalMode('create');
    setEditingEmployee(undefined);
    setEmployeeModalOpen(true);
  };

  const openEditEmployee = (e: Employee) => {
    setEmployeeModalMode('edit');
    setEditingEmployee(e);
    setEmployeeModalOpen(true);
  };

  const openAddCert = (e?: Employee) => {
    setCertModalMode('create');
    setCertEmployee(e);
    setEditingCert(undefined);
    setCertModalOpen(true);
  };

  const openEditCert = (e: Employee, c: Certification) => {
    setCertModalMode('edit');
    setCertEmployee(e);
    setEditingCert(c);
    setCertModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-ink-50">
      <Sidebar
        current={page}
        onNavigate={navigate}
        mobileOpen={mobileSidebar}
        onCloseMobile={() => setMobileSidebar(false)}
      />

      <div className="lg:pl-64">
        <Header
          current={page}
          onOpenMobile={() => setMobileSidebar(true)}
          onNavigate={navigate}
          profileName={selectedEmployee ? `${selectedEmployee.firstName} ${selectedEmployee.lastName}` : undefined}
        />

        <main className="mx-auto max-w-7xl px-4 py-6 lg:px-6">
          {page === 'dashboard' && <DashboardPage onNavigate={navigate} />}
          {page === 'personnel' && (
            <PersonnelPage onNavigate={navigate} onOpenCreate={openCreateEmployee} onOpenEdit={openEditEmployee} />
          )}
          {page === 'profile' && selectedEmployee && (
            <ProfilePage
              employee={selectedEmployee}
              onBack={() => navigate('personnel')}
              onNavigate={navigate}
              onOpenEditEmployee={openEditEmployee}
              onOpenAddCert={openAddCert}
              onOpenEditCert={openEditCert}
            />
          )}
          {page === 'certifications' && (
            <CertificationsPage onNavigate={navigate} onOpenAddCert={() => openAddCert()} onOpenEditCert={openEditCert} />
          )}
        </main>
      </div>

      {/* Modals */}
      <EmployeeFormModal
        open={employeeModalOpen}
        onClose={() => setEmployeeModalOpen(false)}
        employee={editingEmployee}
        mode={employeeModalMode}
      />
      <CertFormModal
        open={certModalOpen}
        onClose={() => setCertModalOpen(false)}
        employee={certEmployee}
        cert={editingCert}
        mode={certModalMode}
      />
    </div>
  );
}

export default App;
