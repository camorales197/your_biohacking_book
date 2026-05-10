"use client";

import ReactMarkdown from "react-markdown";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

interface Props {
  threadId: string;
  title: string;
  content: string;
  emailSent: boolean;
  userEmail: string;
  onReset: () => void;
}

export default function BookDisplay({
  threadId,
  title,
  content,
  emailSent,
  userEmail,
  onReset,
}: Props) {
  const handleDownloadMd = () => {
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadPdf = () => {
    window.open(`${BACKEND_URL}/api/book/${threadId}/pdf`, "_blank");
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-6">
        <div className="text-5xl mb-4">📗</div>
        <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
          ¡Tu libro está listo!
        </h2>
      </div>

      {emailSent ? (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl flex items-start gap-3">
          <span className="text-2xl">✉️</span>
          <div>
            <p className="font-semibold text-green-800 dark:text-green-300">
              Libro enviado a <strong>{userEmail}</strong>
            </p>
            <p className="text-sm text-green-700 dark:text-green-400 mt-0.5">
              Revisa tu bandeja de entrada (y carpeta de spam). Adjuntos: PDF + Markdown.
            </p>
          </div>
        </div>
      ) : (
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl flex items-start gap-3">
          <span className="text-2xl">⚠️</span>
          <p className="text-sm text-amber-700 dark:text-amber-300">
            El envío por email no está configurado. Descarga el libro desde aquí.
          </p>
        </div>
      )}

      <div className="flex flex-wrap gap-3 mb-8">
        <button
          onClick={handleDownloadPdf}
          className="flex-1 py-3 px-6 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-colors"
        >
          ⬇️ Descargar PDF
        </button>
        <button
          onClick={handleDownloadMd}
          className="flex-1 py-3 px-6 bg-zinc-700 hover:bg-zinc-800 text-white font-semibold rounded-xl transition-colors"
        >
          ⬇️ Descargar Markdown
        </button>
        <button
          onClick={onReset}
          className="px-6 py-3 border border-zinc-300 dark:border-zinc-600 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-xl transition-colors"
        >
          🔄 Generar otro libro
        </button>
      </div>

      <div className="prose prose-zinc dark:prose-invert max-w-none bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-700 p-8">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}
