import { Menu, Bell, Search, ChevronRight } from 'lucide-react';
import type { Page } from '@/types';

const pageTitles: Record<Page, { title: string; subtitle: string }> = {
  dashboard: { title: 'Dashboard', subtitle: 'Resumen general del sistema' },
  personnel: { title: 'Personal', subtitle: 'Gestión de empleados' },
  profile: { title: 'Perfil del empleado', subtitle: 'Información detallada' },
  certifications: { title: 'Certificaciones', subtitle: 'Gestión de certificaciones' },
};

export function Header({
  current,
  onOpenMobile,
  onNavigate,
  profileName,
}: {
  current: Page;
  onOpenMobile: () => void;
  onNavigate: (p: Page) => void;
  profileName?: string;
}) {
  const { title, subtitle } = pageTitles[current];

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-ink-200 bg-white/90 px-4 backdrop-blur-md lg:px-6">
      <button onClick={onOpenMobile} className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 lg:hidden">
        <Menu className="h-5 w-5" />
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5 text-sm">
          <button
            onClick={() => onNavigate('dashboard')}
            className="text-ink-400 hover:text-ink-600"
          >
            Inicio
          </button>
          {current !== 'dashboard' && (
            <>
              <ChevronRight className="h-3.5 w-3.5 text-ink-300" />
              <button
                onClick={() => onNavigate(current === 'profile' ? 'personnel' : current)}
                className="text-ink-400 hover:text-ink-600"
              >
                {current === 'profile' ? 'Personal' : title}
              </button>
            </>
          )}
          {current === 'profile' && (
            <>
              <ChevronRight className="h-3.5 w-3.5 text-ink-300" />
              <span className="font-medium text-ink-700 truncate">{profileName}</span>
            </>
          )}
        </div>
        <h1 className="text-lg font-semibold text-ink-900 leading-tight">
          {current === 'profile' ? 'Perfil del empleado' : title}
        </h1>
      </div>

      {/* Search */}
      <div className="relative hidden md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Buscar..."
          className="w-56 rounded-lg border border-ink-200 bg-ink-50 px-9 py-2 text-sm text-ink-900 placeholder:text-ink-400 transition-colors focus:border-primary-500 focus:bg-white focus:ring-2 focus:ring-primary-100"
        />
      </div>

      {/* Notifications */}
      <button className="relative rounded-lg p-2 text-ink-500 hover:bg-ink-100 transition-colors">
        <Bell className="h-5 w-5" />
        <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-danger-500 ring-2 ring-white" />
      </button>

      {/* User */}
      <div className="flex items-center gap-2.5 border-l border-ink-200 pl-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-sm font-semibold text-white">
          CR
        </div>
        <div className="hidden lg:block">
          <p className="text-sm font-medium text-ink-900 leading-tight">Carlos Ruiz</p>
          <p className="text-xs text-ink-400 leading-tight">Administrador</p>
        </div>
      </div>
    </header>
  );
}
