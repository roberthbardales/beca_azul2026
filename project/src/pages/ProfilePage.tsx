import { useState } from 'react';
import {
  ArrowLeft, Mail, Phone, MapPin, Calendar, Briefcase, Building2, Plus, Pencil,
  FileText, Download, Award, Clock, History, User, Trash2, Upload,
} from 'lucide-react';
import type { Page, Employee, Certification } from '@/types';
import { Avatar, EmployeeStatusBadge, CertBadge } from '@/components/ui/Badge';
import { Tabs } from '@/components/ui/Tabs';
import { EmptyState } from '@/components/ui/Form';
import { Dropdown } from '@/components/ui/Dropdown';

export function ProfilePage({
  employee,
  onBack,
  onNavigate,
  onOpenEditEmployee,
  onOpenAddCert,
  onOpenEditCert,
}: {
  employee: Employee;
  onBack: () => void;
  onNavigate: (p: Page) => void;
  onOpenEditEmployee: (e: Employee) => void;
  onOpenAddCert: (e: Employee) => void;
  onOpenEditCert: (e: Employee, c: Certification) => void;
}) {
  const [tab, setTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Información' },
    { id: 'certifications', label: 'Certificaciones', count: employee.certifications.length },
    { id: 'documents', label: 'Documentos', count: employee.documents.length },
    { id: 'history', label: 'Historial', count: employee.history.length },
  ];

  return (
    <div className="space-y-5">
      {/* Back */}
      <button onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-ink-500 hover:text-ink-800 transition-colors">
        <ArrowLeft className="h-4 w-4" />
        Volver a personal
      </button>

      {/* Profile header card */}
      <div className="card overflow-hidden">
        <div className="h-20 bg-gradient-to-r from-primary-600 to-primary-800" />
        <div className="px-5 pb-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex items-end gap-4 -mt-10">
              <div className="rounded-full ring-4 ring-white">
                <Avatar name={`${employee.firstName} ${employee.lastName}`} color={employee.avatarColor} size="lg" />
              </div>
              <div className="pb-1">
                <h2 className="text-xl font-bold text-ink-900">{employee.firstName} {employee.lastName}</h2>
                <p className="text-sm text-ink-500">{employee.position} · {employee.department}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <EmployeeStatusBadge status={employee.status} />
              <button onClick={() => onOpenEditEmployee(employee)} className="btn-secondary">
                <Pencil className="h-4 w-4" />
                Editar
              </button>
              <Dropdown
                trigger={<MoreVertical />}
                items={[
                  { label: 'Agregar certificación', icon: Plus, onClick: () => onOpenAddCert(employee) },
                  { label: 'Subir documento', icon: Upload, onClick: () => {} },
                ]}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="px-5 pt-2">
          <Tabs tabs={tabs} active={tab} onChange={setTab} />
        </div>

        {/* Overview tab */}
        {tab === 'overview' && (
          <div className="grid grid-cols-1 gap-px bg-ink-100 sm:grid-cols-2">
            <InfoBlock icon={User} label="Nombre completo" value={`${employee.firstName} ${employee.lastName}`} />
            <InfoBlock icon={Mail} label="Correo electrónico" value={employee.email} />
            <InfoBlock icon={Phone} label="Teléfono" value={employee.phone} />
            <InfoBlock icon={MapPin} label="Ubicación" value={employee.location} />
            <InfoBlock icon={Briefcase} label="Cargo" value={employee.position} />
            <InfoBlock icon={Building2} label="Departamento" value={employee.department} />
            <InfoBlock icon={Calendar} label="Fecha de ingreso" value={formatDate(employee.hireDate)} />
            <InfoBlock icon={User} label="Estado" value={statusLabel(employee.status)} />
          </div>
        )}

        {/* Certifications tab */}
        {tab === 'certifications' && (
          <div className="p-5">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-ink-500">{employee.certifications.length} certificación(es) registrada(s)</p>
              <button onClick={() => onOpenAddCert(employee)} className="btn-primary">
                <Plus className="h-4 w-4" />
                Agregar certificación
              </button>
            </div>
            {employee.certifications.length === 0 ? (
              <EmptyState
                icon={Award}
                title="Sin certificaciones"
                description="Este empleado aún no tiene certificaciones registradas."
                action={
                  <button onClick={() => onOpenAddCert(employee)} className="btn-primary">
                    <Plus className="h-4 w-4" />
                    Agregar certificación
                  </button>
                }
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-ink-200 bg-ink-50 text-left">
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Certificación</th>
                      <th className="hidden px-4 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 sm:table-cell">Emisor</th>
                      <th className="hidden px-4 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500 md:table-cell">Emisión</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Vencimiento</th>
                      <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Estado</th>
                      <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-ink-500">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ink-100">
                    {employee.certifications.map((c) => (
                      <tr key={c.id} className="table-row-hover">
                        <td className="px-4 py-3">
                          <p className="text-sm font-medium text-ink-900">{c.name}</p>
                          <p className="text-xs text-ink-400">ID: {c.credentialId}</p>
                        </td>
                        <td className="hidden px-4 py-3 sm:table-cell">
                          <span className="text-sm text-ink-600">{c.issuer}</span>
                        </td>
                        <td className="hidden px-4 py-3 md:table-cell">
                          <span className="text-sm text-ink-600">{formatDate(c.issueDate)}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-sm text-ink-600">{formatDate(c.expiryDate)}</span>
                        </td>
                        <td className="px-4 py-3">
                          <CertBadge status={c.status} />
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <button
                              onClick={() => onOpenEditCert(employee, c)}
                              className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 transition-colors"
                            >
                              <Pencil className="h-4 w-4" />
                            </button>
                            <Dropdown
                              trigger={<MoreVertical className="h-4 w-4" />}
                              items={[
                                { label: 'Editar', icon: Pencil, onClick: () => onOpenEditCert(employee, c) },
                                { label: 'Eliminar', icon: Trash2, onClick: () => {}, danger: true },
                              ]}
                            />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Documents tab */}
        {tab === 'documents' && (
          <div className="p-5">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-ink-500">{employee.documents.length} documento(s)</p>
              <button className="btn-secondary">
                <Upload className="h-4 w-4" />
                Subir documento
              </button>
            </div>
            {employee.documents.length === 0 ? (
              <EmptyState icon={FileText} title="Sin documentos" description="No hay documentos cargados para este empleado." />
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {employee.documents.map((d) => (
                  <div key={d.id} className="flex items-center gap-3 rounded-xl2 border border-ink-200 p-4 transition-shadow hover:shadow-card-hover">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-ink-900">{d.name}</p>
                      <p className="text-xs text-ink-400">{d.type} · {d.size} · {formatDate(d.uploadedAt)}</p>
                    </div>
                    <button className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 transition-colors">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* History tab */}
        {tab === 'history' && (
          <div className="p-5">
            {employee.history.length === 0 ? (
              <EmptyState icon={History} title="Sin historial" description="No se han registrado cambios para este empleado." />
            ) : (
              <div className="relative space-y-5 before:absolute before:left-[18px] before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-ink-200">
                {employee.history.map((h) => (
                  <div key={h.id} className="relative flex gap-4">
                    <div className="z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white ring-2 ring-ink-200">
                      <Clock className="h-4 w-4 text-ink-400" />
                    </div>
                    <div className="flex-1 pb-1">
                      <p className="text-sm font-medium text-ink-900">{h.action}</p>
                      <p className="text-sm text-ink-500">{h.detail}</p>
                      <p className="mt-1 text-xs text-ink-400">{formatDate(h.date)} · por {h.user}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoBlock({ icon: Icon, label, value }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string }) {
  return (
    <div className="bg-white p-5">
      <div className="flex items-center gap-2 text-ink-400">
        <Icon className="h-4 w-4" />
        <p className="text-xs font-medium uppercase tracking-wider">{label}</p>
      </div>
      <p className="mt-1.5 text-sm font-medium text-ink-900">{value}</p>
    </div>
  );
}

function MoreVertical({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="5" r="1" />
      <circle cx="12" cy="12" r="1" />
      <circle cx="12" cy="19" r="1" />
    </svg>
  );
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
}

function statusLabel(s: string) {
  return s === 'active' ? 'Activo' : s === 'on_leave' ? 'De licencia' : 'Inactivo';
}
