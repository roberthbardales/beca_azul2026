import { ChevronLeft, ChevronRight } from 'lucide-react';

export function Pagination({
  page,
  totalPages,
  onPageChange,
  total,
  pageSize,
}: {
  page: number;
  totalPages: number;
  onPageChange: (p: number) => void;
  total: number;
  pageSize: number;
}) {
  if (total === 0) return null;
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  return (
    <div className="flex items-center justify-between border-t border-ink-200 px-5 py-3.5">
      <p className="text-sm text-ink-500">
        Mostrando <span className="font-medium text-ink-700">{from}-{to}</span> de{' '}
        <span className="font-medium text-ink-700">{total}</span>
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="btn-ghost px-2 py-1.5 disabled:opacity-40"
          aria-label="Página anterior"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            className={`min-w-[2rem] rounded-lg px-2.5 py-1.5 text-sm font-medium transition-colors ${
              p === page
                ? 'bg-primary-600 text-white'
                : 'text-ink-600 hover:bg-ink-100 hover:text-ink-900'
            }`}
          >
            {p}
          </button>
        ))}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="btn-ghost px-2 py-1.5 disabled:opacity-40"
          aria-label="Página siguiente"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
