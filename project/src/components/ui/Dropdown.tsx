import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export interface DropdownItem {
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
  onClick: () => void;
  danger?: boolean;
}

export function Dropdown({ items, trigger }: { items: DropdownItem[]; trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setOpen((o) => !o);
        }}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 transition-colors"
      >
        {trigger}
      </button>
      {open && (
        <div className="absolute right-0 z-20 mt-1 w-44 overflow-hidden rounded-xl2 border border-ink-200 bg-white py-1 shadow-pop animate-scale-in">
          {items.map((item, i) => (
            <button
              key={i}
              onMouseDown={(e) => {
                e.preventDefault();
                item.onClick();
                setOpen(false);
              }}
              className={`flex w-full items-center gap-2.5 px-3 py-2 text-sm transition-colors hover:bg-ink-50 ${
                item.danger ? 'text-danger-600 hover:bg-danger-50' : 'text-ink-700'
              }`}
            >
              {item.icon && <item.icon className="h-4 w-4" />}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export function DropdownTrigger() {
  return <ChevronDown className="h-4 w-4" />;
}
