import { Search, X } from 'lucide-react';

export function SearchInput({
  value,
  onChange,
  placeholder = 'Buscar...',
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input-base pl-9 pr-9 w-64"
      />
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded p-0.5 text-ink-400 hover:bg-ink-100 hover:text-ink-600"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}

export function Select({
  value,
  onChange,
  options,
  placeholder,
  allLabel,
  className = '',
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
  placeholder?: string;
  allLabel?: string;
  className?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`input-base cursor-pointer pr-8 ${className}`}
    >
      {allLabel && <option value="">{allLabel}</option>}
      {options.map((o) => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
      {placeholder && !allLabel && <option value="">{placeholder}</option>}
    </select>
  );
}

export function Field({
  label,
  children,
  required,
  hint,
}: {
  label: string;
  children: React.ReactNode;
  required?: boolean;
  hint?: string;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-ink-700">
        {label}
        {required && <span className="ml-0.5 text-danger-500">*</span>}
      </label>
      {children}
      {hint && <p className="mt-1 text-xs text-ink-400">{hint}</p>}
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-ink-100">
        <Icon className="h-7 w-7 text-ink-400" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-ink-900">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-ink-500">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function Spinner() {
  return (
    <div className="flex items-center justify-center px-6 py-16">
      <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-ink-200 border-t-primary-500" />
    </div>
  );
}
