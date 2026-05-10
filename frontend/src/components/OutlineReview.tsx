"use client";

import { useState } from "react";

interface SubSection {
  title: string;
  focus: string;
}

interface Section {
  title: string;
  subsections: SubSection[];
}

interface Chapter {
  title: string;
  level: number;
  sections: Section[];
}

interface BookOutline {
  title: string;
  chapters: Chapter[];
}

interface Props {
  outline: BookOutline;
  sectionsCount: number;
  onApprove: (feedback?: string) => void;
  onRegenerate: (feedback: string) => void;
  loading: boolean;
}

const FOCUS_ICONS: Record<string, string> = {
  "Acciones concretas": "⚡",
  "Ciencia detrás del hábito": "🔬",
  "Protocolo de implementación": "📋",
};

export default function OutlineReview({
  outline,
  sectionsCount,
  onApprove,
  onRegenerate,
  loading,
}: Props) {
  const [feedback, setFeedback] = useState("");
  const [expanded, setExpanded] = useState<Set<number>>(new Set([0, 1]));

  const toggleChapter = (idx: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
          📚 Revisa tu esquema
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400">
          El Agente Arquitecto ha generado{" "}
          <strong>{sectionsCount} subsecciones</strong> para tu libro. Revísalas
          y aprueba o pide cambios.
        </p>
      </div>

      <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
        <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-50">{outline.title}</h3>
      </div>

      <div className="space-y-3 mb-6">
        {outline.chapters.map((chapter, chIdx) => (
          <div
            key={chIdx}
            className="rounded-xl border border-zinc-200 dark:border-zinc-700 overflow-hidden"
          >
            <button
              onClick={() => toggleChapter(chIdx)}
              className="w-full px-4 py-3 flex items-center justify-between bg-zinc-50 dark:bg-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors text-left"
            >
              <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                {chapter.level > 0 && (
                  <span className="text-green-600 mr-2">Nivel {chapter.level}</span>
                )}
                {chapter.title}
              </span>
              <span className="text-zinc-400">{expanded.has(chIdx) ? "▲" : "▼"}</span>
            </button>

            {expanded.has(chIdx) && (
              <div className="p-4 space-y-3 bg-white dark:bg-zinc-900">
                {chapter.sections.map((section, sIdx) => (
                  <div key={sIdx}>
                    <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-1">
                      📑 {section.title}
                    </p>
                    <div className="ml-4 space-y-1">
                      {section.subsections.map((sub, subIdx) => (
                        <div
                          key={subIdx}
                          className="flex items-start gap-2 text-sm text-zinc-600 dark:text-zinc-400"
                        >
                          <span>{FOCUS_ICONS[sub.focus] ?? "📌"}</span>
                          <span>
                            <strong>{sub.title}</strong>{" "}
                            <span className="text-zinc-400 text-xs">({sub.focus})</span>
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
          Feedback o cambios solicitados{" "}
          <span className="text-zinc-400 font-normal">(opcional)</span>
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
          placeholder="Ej: Añade más énfasis en recuperación deportiva, o incluye una sección sobre gestión del estrés laboral..."
        />
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => onApprove(feedback || undefined)}
          disabled={loading}
          className="flex-1 py-3 px-6 bg-green-600 hover:bg-green-700 disabled:bg-zinc-400 text-white font-semibold rounded-xl transition-colors"
        >
          {loading ? "⚙️ Generando libro..." : "✅ Aprobar y generar libro"}
        </button>
        <button
          onClick={() => onRegenerate(feedback)}
          disabled={loading || !feedback.trim()}
          className="px-6 py-3 border border-zinc-300 dark:border-zinc-600 hover:bg-zinc-50 dark:hover:bg-zinc-800 disabled:opacity-40 text-zinc-700 dark:text-zinc-300 font-semibold rounded-xl transition-colors"
        >
          🔄 Regenerar esquema
        </button>
      </div>
    </div>
  );
}
