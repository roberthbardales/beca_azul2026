import { useState, useMemo } from 'react';
import { Plus, Award, MoreVertical, Pencil, Trash2, Download, Calendar } from 'lucide-react';
import type { Page, Employee, Certification } from '@/types';
import { employees, allCertifications, certTypes } from '@/data/mockData';
import { Avatar, CertBadge } from '@/components/ui/Badge';
import { SearchInput, Select, EmptyState } from '@/components/ui/Form';
import { Pagination } from '@/components/ui/Pagination';
import { Dropdown } from '@/components/ui/Dropdown';

const PAGE_SIZE = 8;

export function CertificationsPage({
  onNavigate,
  onOpenAddCert,
  onOpenEditCert,
}: {
  onNavigate: (p: Page, employeeId?: string) => void;
  onOpenAddCert: () => void;
  onOpenEditCert: (e: Employee, c: Certification) => void;
}) {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);

  const allCerts = allCertifications();

  const filtered = useMemo(() => {
    return allCerts.filter(({ cert, employee }) => {
      const fullName = `${employee.firstName} ${employee.lastName}`.toLowerCase();
      const matchesSearch =
        cert.name.toLowerCase().includes(search.toLowerCase()) ||
        cert.issuer.toLowerCase().includes(search.toLowerCase()) ||
        fullName.includes(search.toLowerCase());
      const matchesType = !typeFilter || cert.name === typeFilter;
      const matchesStatus = !statusFilter || cert.status === statusFilter;
      return matchesSearch && matchesType && matchesStatus;
    });
  }, [allCerts, search, typeFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const current = Math.min(page, totalPages);
  const pageData = filtered.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE);

  const statusOptions = [
    { value: 'vigente', label: 'Vigente' },
    { value: 'proxima', label: 'Próxima a vencer' },
    { value: 'vencida', label: 'Vencida' },
  ];

  return (
    <div className="space-y-5">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SummaryCard label="Vigentes" value={allCerts.filter((c) => c.cert.status === 'vigente').length} variant="success" icon={Award} />
        <SummaryCard label="Próximas a vencer" value={allCerts.filter((c) => c.cert.status === 'proxima').length} variant="warning" icon={Calendar} />
        <SummaryCard label="Vencidas" value={allCerts.filter((c) => c.cert.status === 'vencida').length} variant="danger" icon={Calendar} />
      </div>

      {/* Toolbar */}
      <div className="card">
        <div className="flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center">
            <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Buscar certificación o empleado..." />
            <Select
              value={typeFilter}
              onChange={(v) => { setTypeFilter(v); setPage(1); }}
              options={certTypes}
              allLabel="Todos los tipos"
              className="w-auto min-w-[160px]"
            />
            <Select
              value={statusFilter}
              onChange={(v) => { setStatusFilter(v); setPage(1); }}
              options={statusOptions.map((s) => s.label)}
              allLabel="Todos los estados"
              className="w-auto min-w-[140px]"
            />
          </div>
          <button onClick={onOpenAddCert} className="btn-primary shrink-0">
            <Plus className="h-4 w-4" />
            Agregar certificación
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {pageData.length === 0 ? (
          <EmptyState
            icon={Award}
            title="No se encontraron certificaciones"
            description="Ajusta los filtros o agrega una nueva certificación al sistema."
            action={
              <button onClick={onOpenAddCert} className="btn-primary">
                <Plus className="h-4 w-4" />
                Agregar certificación
              </button>
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-ink-200 bg-ink-50 text-left">
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Certificación</th>
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Empleado</th>
                    <th className="hidden px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 md:table-cell">Emisión</th>
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Vencimiento</th>
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Estado</th>
                    <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-ink-500">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100">
                  {pageData.map(({ cert, employee }) => (
                    <tr key={cert.id} className="table-row-hover">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
                            <Award className="h-4.5 w-4.5" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-ink-900">{cert.name}</p>
                            <p className="text-xs text-ink-400">{cert.issuer}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <button
                          onClick={() => onNavigate('profile', employee.id)}
                          className="flex items-center gap-2 hover:opacity-80"
                        >
                          <Avatar name={`${employee.firstName} ${employee.lastName}`} color={employee.avatarColor} size="sm" />
                          <span className="text-sm text-ink-700 hover:text-primary-600">{employee.firstName} {employee.lastName}</span>
                        </button>
                      </td>
                      <td className="hidden px-5 py-3.5 md:table-cell">
                        <span className="text-sm text-ink-600">{formatDate(cert.issueDate)}</span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="text-sm text-ink-600">{formatDate(cert.expiryDate)}</span>
                      </td>
                      <td className="px-5 py-3.5">
                        <CertBadge status={cert.status} />
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <Dropdown
                          trigger={<MoreVertical className="h-4 w-4" />}
                          items={[
                            { label: 'Ver empleado', icon: Award, onClick: () => onNavigate('profile', employee.id) },
                            { label: 'Editar', icon: Pencil, onClick: () => onOpenEditCert(employee, cert) },
                            { label: 'Descargar', icon: Download, onClick: () => {} },
                            { label: 'Eliminar', icon: Trash2, onClick: () => {}, danger: true },
                          ]}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              page={current}
              totalPages={totalPages}
              onPageChange={setPage}
              total={filtered.length}
              pageSize={PAGE_SIZE}
            />
          </>
        )}
      </div>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  variant,
  icon: Icon,
}: {
  label: string;
  value: number;
  variant: 'success' | 'warning' | 'danger';
  icon: React.ComponentType<{ className?: string }>;
}) {
  const colors = {
    success: 'bg-success-50 text-success-600',
    warning: 'bg-warning-50 text-warning-600',
    danger: 'bg-danger-50 text-danger-600',
  };
  return (
    <div className="card card-pad flex items-center gap-4">
      <div className={`flex h-11 w-11 items-center justify-center rounded-xl2 ${colors[variant]}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="text-2xl font-bold text-ink-900">{value}</p>
        <p className="text-sm text-ink-500">{label}</p>
      </div>
    </div>
  );
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
}
