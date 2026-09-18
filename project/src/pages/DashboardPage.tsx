import { Users, Award, CheckCircle2, AlertTriangle, XCircle, TrendingUp, FileText, Clock, UserPlus, ArrowRight } from 'lucide-react';
import type { Page, ActivityItem } from '@/types';
import { employees, activityFeed, allCertifications } from '@/data/mockData';
import { Avatar } from '@/components/ui/Badge';

export function DashboardPage({ onNavigate }: { onNavigate: (p: Page) => void }) {
  const total = employees.length;
  const active = employees.filter((e) => e.status === 'active').length;
  const certs = allCertifications();
  const vigente = certs.filter((c) => c.cert.status === 'vigente').length;
  const proxima = certs.filter((c) => c.cert.status === 'proxima').length;
  const vencida = certs.filter((c) => c.cert.status === 'vencida').length;

  const stats = [
    { label: 'Total de personal', value: total, icon: Users, color: 'primary', sub: `${active} activos` },
    { label: 'Certificaciones vigentes', value: vigente, icon: CheckCircle2, color: 'success', sub: 'al día' },
    { label: 'Próximas a vencer', value: proxima, icon: AlertTriangle, color: 'warning', sub: 'en 30 días' },
    { label: 'Certificaciones vencidas', value: vencida, icon: XCircle, color: 'danger', sub: 'requieren atención' },
  ];

  const colorMap: Record<string, { bg: string; text: string; iconBg: string }> = {
    primary: { bg: 'bg-primary-50', text: 'text-primary-700', iconBg: 'bg-primary-600' },
    success: { bg: 'bg-success-50', text: 'text-success-700', iconBg: 'bg-success-500' },
    warning: { bg: 'bg-warning-50', text: 'text-warning-700', iconBg: 'bg-warning-500' },
    danger: { bg: 'bg-danger-50', text: 'text-danger-700', iconBg: 'bg-danger-500' },
  };

  // Simple bar chart data — certs by department
  const deptCounts = new Map<string, number>();
  for (const e of employees) {
    const count = e.certifications.length;
    deptCounts.set(e.department, (deptCounts.get(e.department) ?? 0) + count);
  }
  const deptData = Array.from(deptCounts.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const maxDept = Math.max(...deptData.map((d) => d[1]));

  // Status distribution for donut
  const totalCerts = vigente + proxima + vencida;
  const pctVigente = totalCerts ? (vigente / totalCerts) * 100 : 0;
  const pctProxima = totalCerts ? (proxima / totalCerts) * 100 : 0;
  const pctVencida = totalCerts ? (vencida / totalCerts) * 100 : 0;

  const activityIcons: Record<ActivityItem['type'], { icon: typeof Award; cls: string }> = {
    cert_added: { icon: Award, cls: 'bg-primary-50 text-primary-600' },
    cert_expiring: { icon: AlertTriangle, cls: 'bg-warning-50 text-warning-600' },
    cert_expired: { icon: XCircle, cls: 'bg-danger-50 text-danger-600' },
    employee_added: { icon: UserPlus, cls: 'bg-success-50 text-success-600' },
    employee_updated: { icon: FileText, cls: 'bg-ink-100 text-ink-600' },
  };

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => {
          const c = colorMap[s.color];
          return (
            <div key={s.label} className="card card-pad transition-shadow hover:shadow-card-hover">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-ink-500">{s.label}</p>
                  <p className="mt-2 text-3xl font-bold text-ink-900">{s.value}</p>
                  <p className="mt-1 text-xs text-ink-400">{s.sub}</p>
                </div>
                <div className={`flex h-11 w-11 items-center justify-center rounded-xl2 ${c.iconBg}`}>
                  <s.icon className="h-5.5 w-5.5 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Bar chart */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
            <div>
              <h3 className="text-base font-semibold text-ink-900">Certificaciones por departamento</h3>
              <p className="text-sm text-ink-400">Distribución de certificaciones activas</p>
            </div>
            <TrendingUp className="h-5 w-5 text-ink-300" />
          </div>
          <div className="space-y-4 px-5 py-5">
            {deptData.map(([dept, count]) => (
              <div key={dept}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="font-medium text-ink-700">{dept}</span>
                  <span className="text-ink-500">{count}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-ink-100">
                  <div
                    className="h-full rounded-full bg-primary-500 transition-all"
                    style={{ width: `${(count / maxDept) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Donut / status distribution */}
        <div className="card">
          <div className="border-b border-ink-200 px-5 py-4">
            <h3 className="text-base font-semibold text-ink-900">Estado de certificaciones</h3>
            <p className="text-sm text-ink-400">Resumen general</p>
          </div>
          <div className="px-5 py-5">
            <div className="flex items-center justify-center">
              <div className="relative h-36 w-36">
                <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
                  <circle cx="18" cy="18" r="15.915" fill="none" stroke="#eef0f4" strokeWidth="3.5" />
                  <circle cx="18" cy="18" r="15.915" fill="none" stroke="#16b866" strokeWidth="3.5" strokeDasharray={`${pctVigente} ${100 - pctVigente}`} strokeLinecap="round" />
                  <circle cx="18" cy="18" r="15.915" fill="none" stroke="#f29910" strokeWidth="3.5" strokeDasharray={`${pctProxima} ${100 - pctProxima}`} strokeDashoffset={`-${pctVigente}`} strokeLinecap="round" />
                  <circle cx="18" cy="18" r="15.915" fill="none" stroke="#ef4444" strokeWidth="3.5" strokeDasharray={`${pctVencida} ${100 - pctVencida}`} strokeDashoffset={`-${pctVigente + pctProxima}`} strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold text-ink-900">{totalCerts}</span>
                  <span className="text-xs text-ink-400">Total</span>
                </div>
              </div>
            </div>
            <div className="mt-5 space-y-2.5">
              <Legend color="bg-success-500" label="Vigentes" value={vigente} pct={pctVigente} />
              <Legend color="bg-warning-500" label="Próximas a vencer" value={proxima} pct={pctProxima} />
              <Legend color="bg-danger-500" label="Vencidas" value={vencida} pct={pctVencida} />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom row: activity + expiring certs */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Recent activity */}
        <div className="card">
          <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4.5 w-4.5 text-ink-400" />
              <h3 className="text-base font-semibold text-ink-900">Actividad reciente</h3>
            </div>
          </div>
          <div className="divide-y divide-ink-100">
            {activityFeed.slice(0, 5).map((a) => {
              const { icon: Icon, cls } = activityIcons[a.type];
              return (
                <div key={a.id} className="flex items-start gap-3 px-5 py-3.5">
                  <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${cls}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-ink-700">{a.message}</p>
                    <p className="mt-0.5 text-xs text-ink-400">{a.time}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Expiring soon list */}
        <div className="card">
          <div className="flex items-center justify-between border-b border-ink-200 px-5 py-4">
            <h3 className="text-base font-semibold text-ink-900">Certificaciones por vencer</h3>
            <button
              onClick={() => onNavigate('certifications')}
              className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              Ver todas <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="divide-y divide-ink-100">
            {certs
              .filter((c) => c.cert.status === 'proxima')
              .slice(0, 4)
              .map(({ cert, employee }) => (
                <div key={cert.id} className="flex items-center gap-3 px-5 py-3.5">
                  <Avatar name={`${employee.firstName} ${employee.lastName}`} color={employee.avatarColor} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink-900">{cert.name}</p>
                    <p className="truncate text-xs text-ink-400">
                      {employee.firstName} {employee.lastName} · Vence {formatDate(cert.expiryDate)}
                    </p>
                  </div>
                  <span className="badge-warning shrink-0">
                    <span className="h-1.5 w-1.5 rounded-full bg-current" /> Próxima
                  </span>
                </div>
              ))}
            {certs.filter((c) => c.cert.status === 'proxima').length === 0 && (
              <div className="px-5 py-8 text-center text-sm text-ink-400">No hay certificaciones próximas a vencer</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Legend({ color, label, value, pct }: { color: string; label: string; value: number; pct: number }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <div className="flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
        <span className="text-ink-600">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="font-semibold text-ink-900">{value}</span>
        <span className="text-xs text-ink-400">{pct.toFixed(0)}%</span>
      </div>
    </div>
  );
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
}
