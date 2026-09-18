import { LayoutDashboard, Users, Award, ShieldCheck, Settings, LifeBuoy, X } from 'lucide-react';
import type { Page } from '@/types';

const navItems: { id: Page; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'personnel', label: 'Personal', icon: Users },
  { id: 'certifications', label: 'Certificaciones', icon: Award },
];

export function Sidebar({
  current,
  onNavigate,
  mobileOpen,
  onCloseMobile,
}: {
  current: Page;
  onNavigate: (p: Page) => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}) {
  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 z-30 bg-ink-950/40 lg:hidden" onClick={onCloseMobile} />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-ink-200 bg-white transition-transform lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="flex h-16 items-center gap-2.5 border-b border-ink-200 px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-ink-900 leading-tight">CertifyPro</p>
            <p className="text-xs text-ink-400 leading-tight">Gestión de Personal</p>
          </div>
          <button onClick={onCloseMobile} className="ml-auto rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-ink-400">Menú principal</p>
          {navItems.map((item) => {
            const active = current === item.id || (current === 'profile' && item.id === 'personnel');
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`sidebar-link w-full ${active ? 'sidebar-link-active' : ''}`}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-ink-200 p-3">
          <button className="sidebar-link w-full">
            <Settings className="h-5 w-5" />
            Configuración
          </button>
          <button className="sidebar-link w-full">
            <LifeBuoy className="h-5 w-5" />
            Ayuda
          </button>
          <div className="mt-3 flex items-center gap-3 rounded-lg bg-ink-50 px-3 py-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 text-xs font-semibold text-white">
              CR
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-ink-900">Carlos Ruiz</p>
              <p className="truncate text-xs text-ink-400">Administrador</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
