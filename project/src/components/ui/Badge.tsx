import type { CertStatus, EmployeeStatus } from '@/types';

export function CertBadge({ status }: { status: CertStatus }) {
  if (status === 'vigente') return <span className="badge-success"><Dot /> Vigente</span>;
  if (status === 'proxima') return <span className="badge-warning"><Dot /> Próxima a vencer</span>;
  return <span className="badge-danger"><Dot /> Vencida</span>;
}

export function EmployeeStatusBadge({ status }: { status: EmployeeStatus }) {
  if (status === 'active') return <span className="badge-success"><Dot /> Activo</span>;
  if (status === 'on_leave') return <span className="badge-warning"><Dot /> De licencia</span>;
  return <span className="badge-neutral"><Dot /> Inactivo</span>;
}

function Dot() {
  return <span className="h-1.5 w-1.5 rounded-full bg-current" />;
}

export function Avatar({
  name,
  color,
  size = 'md',
}: {
  name: string;
  color: string;
  size?: 'sm' | 'md' | 'lg';
}) {
  const initials = name
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-16 w-16 text-lg',
  };
  return (
    <div
      className={`${sizes[size]} flex shrink-0 items-center justify-center rounded-full font-semibold text-white`}
      style={{ backgroundColor: color }}
    >
      {initials}
    </div>
  );
}
