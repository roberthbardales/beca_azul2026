import { useState, useMemo } from 'react';
import { Plus, Users, MoreVertical, Eye, Pencil, FileText, Filter } from 'lucide-react';
import type { Page, Employee } from '@/types';
import { employees, departments } from '@/data/mockData';
import { Avatar, EmployeeStatusBadge, CertBadge } from '@/components/ui/Badge';
import { SearchInput, Select, EmptyState } from '@/components/ui/Form';
import { Pagination } from '@/components/ui/Pagination';
import { Dropdown } from '@/components/ui/Dropdown';

const PAGE_SIZE = 6;

export function PersonnelPage({
  onNavigate,
  onOpenCreate,
  onOpenEdit,
}: {
  onNavigate: (p: Page, employeeId?: string) => void;
  onOpenCreate: () => void;
  onOpenEdit: (e: Employee) => void;
}) {
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    return employees.filter((e) => {
      const fullName = `${e.firstName} ${e.lastName}`.toLowerCase();
      const matchesSearch =
        fullName.includes(search.toLowerCase()) ||
        e.email.toLowerCase().includes(search.toLowerCase()) ||
        e.position.toLowerCase().includes(search.toLowerCase());
      const matchesDept = !deptFilter || e.department === deptFilter;
      const matchesStatus = !statusFilter || e.status === statusFilter;
      return matchesSearch && matchesDept && matchesStatus;
    });
  }, [search, deptFilter, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const current = Math.min(page, totalPages);
  const pageData = filtered.slice((current - 1) * PAGE_SIZE, current * PAGE_SIZE);

  const statusOptions = ['active', 'on_leave', 'inactive'];
  const statusLabels: Record<string, string> = { active: 'Activo', on_leave: 'De licencia', inactive: 'Inactivo' };

  return (
    <div className="space-y-5">
      {/* Toolbar */}
      <div className="card">
        <div className="flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center">
            <SearchInput value={search} onChange={(v) => { setSearch(v); setPage(1); }} placeholder="Buscar por nombre, email o cargo..." />
            <div className="flex items-center gap-2">
              <Select
                value={deptFilter}
                onChange={(v) => { setDeptFilter(v); setPage(1); }}
                options={departments}
                allLabel="Todos los departamentos"
                className="w-auto min-w-[180px]"
              />
              <Select
                value={statusFilter}
                onChange={(v) => { setStatusFilter(v); setPage(1); }}
                options={statusOptions.map((s) => statusLabels[s])}
                allLabel="Todos los estados"
                className="w-auto min-w-[140px]"
              />
            </div>
          </div>
          <button onClick={onOpenCreate} className="btn-primary shrink-0">
            <Plus className="h-4 w-4" />
            Nuevo empleado
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        {pageData.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No se encontraron empleados"
            description="Ajusta los filtros de búsqueda o agrega un nuevo empleado al sistema."
            action={
              <button onClick={onOpenCreate} className="btn-primary">
                <Plus className="h-4 w-4" />
                Nuevo empleado
              </button>
            }
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-ink-200 bg-ink-50 text-left">
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Empleado</th>
                    <th className="hidden px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 lg:table-cell">Cargo</th>
                    <th className="hidden px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 md:table-cell">Departamento</th>
                    <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Estado</th>
                    <th className="hidden px-5 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 sm:table-cell">Certificaciones</th>
                    <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-ink-500">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100">
                  {pageData.map((e) => (
                    <tr
                      key={e.id}
                      onClick={() => onNavigate('profile', e.id)}
                      className="table-row-hover cursor-pointer"
                    >
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <Avatar name={`${e.firstName} ${e.lastName}`} color={e.avatarColor} />
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-ink-900">{e.firstName} {e.lastName}</p>
                            <p className="truncate text-xs text-ink-400">{e.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="hidden px-5 py-3.5 lg:table-cell">
                        <span className="text-sm text-ink-700">{e.position}</span>
                      </td>
                      <td className="hidden px-5 py-3.5 md:table-cell">
                        <span className="text-sm text-ink-600">{e.department}</span>
                      </td>
                      <td className="px-5 py-3.5">
                        <EmployeeStatusBadge status={e.status} />
                      </td>
                      <td className="hidden px-5 py-3.5 sm:table-cell">
                        <div className="flex items-center gap-1.5">
                          <span className="text-sm font-medium text-ink-700">{e.certifications.length}</span>
                          {e.certifications.some((c) => c.status === 'vencida') && (
                            <span className="h-1.5 w-1.5 rounded-full bg-danger-500" title="Tiene certificaciones vencidas" />
                          )}
                          {e.certifications.some((c) => c.status === 'proxima') && !e.certifications.some((c) => c.status === 'vencida') && (
                            <span className="h-1.5 w-1.5 rounded-full bg-warning-500" title="Tiene certificaciones próximas a vencer" />
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={(ev) => { ev.stopPropagation(); onNavigate('profile', e.id); }}
                            className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 transition-colors"
                            title="Ver perfil"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={(ev) => { ev.stopPropagation(); onOpenEdit(e); }}
                            className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 transition-colors"
                            title="Editar"
                          >
                            <Pencil className="h-4 w-4" />
                          </button>
                          <Dropdown
                            trigger={<MoreVertical className="h-4 w-4" />}
                            items={[
                              { label: 'Ver perfil', icon: Eye, onClick: () => onNavigate('profile', e.id) },
                              { label: 'Editar', icon: Pencil, onClick: () => onOpenEdit(e) },
                              { label: 'Documentos', icon: FileText, onClick: () => onNavigate('profile', e.id) },
                            ]}
                          />
                        </div>
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
