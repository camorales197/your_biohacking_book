"use client";

interface Props {
  writtenCount: number;
  totalCount: number;
}

export default function GenerationProgress({ writtenCount, totalCount }: Props) {
  const pct = totalCount > 0 ? Math.round((writtenCount / totalCount) * 100) : 0;

  return (
    <div className="max-w-xl mx-auto text-center">
      <div className="text-5xl mb-6 animate-pulse">✍️</div>
      <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
        Escribiendo tu libro...
      </h2>
      <p className="text-zinc-600 dark:text-zinc-400 mb-8">
        Los agentes escritores están redactando {totalCount} subsecciones en paralelo.
      </p>

      <div className="bg-zinc-200 dark:bg-zinc-700 rounded-full h-4 mb-3">
        <div
          className="bg-green-500 h-4 rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        {writtenCount} / {totalCount} subsecciones completadas ({pct}%)
      </p>

      <div className="mt-8 grid grid-cols-3 gap-4 text-sm text-zinc-500 dark:text-zinc-400">
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800">
          <div className="text-2xl mb-1">⚡</div>
          <div>Acciones concretas</div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800">
          <div className="text-2xl mb-1">🔬</div>
          <div>Ciencia del hábito</div>
        </div>
        <div className="p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800">
          <div className="text-2xl mb-1">📋</div>
          <div>Protocolos</div>
        </div>
      </div>
    </div>
  );
}
