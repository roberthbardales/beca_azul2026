import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export function Alert({
  variant = 'info',
  title,
  children,
  onClose,
}: {
  variant?: 'success' | 'warning' | 'danger' | 'info';
  title: string;
  children?: React.ReactNode;
  onClose?: () => void;
}) {
  const config = {
    success: { icon: CheckCircle2, cls: 'bg-success-50 border-success-200 text-success-800', iconCls: 'text-success-500' },
    warning: { icon: AlertTriangle, cls: 'bg-warning-50 border-warning-200 text-warning-800', iconCls: 'text-warning-500' },
    danger: { icon: XCircle, cls: 'bg-danger-50 border-danger-200 text-danger-800', iconCls: 'text-danger-500' },
    info: { icon: Info, cls: 'bg-primary-50 border-primary-200 text-primary-800', iconCls: 'text-primary-500' },
  };
  const { icon: Icon, cls, iconCls } = config[variant];

  return (
    <div className={`flex items-start gap-3 rounded-xl2 border px-4 py-3 ${cls}`}>
      <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${iconCls}`} />
      <div className="flex-1">
        <p className="text-sm font-semibold">{title}</p>
        {children && <p className="mt-0.5 text-sm opacity-90">{children}</p>}
      </div>
      {onClose && (
        <button onClick={onClose} className="rounded p-0.5 hover:bg-black/5">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
