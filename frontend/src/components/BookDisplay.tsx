"use client";

import ReactMarkdown from "react-markdown";

interface Props {
  title: string;
  content: string;
  onReset: () => void;
}

export default function BookDisplay({ title, content, onReset }: Props) {
  const handleDownload = () => {
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-5xl mb-4">📗</div>
        <h2 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-2">
          ¡Tu libro está listo!
        </h2>
        <p className="text-zinc-600 dark:text-zinc-400">
          Tu libro de biohacking personalizado ha sido generado.
        </p>
      </div>

      <div className="flex gap-3 mb-8">
        <button
          onClick={handleDownload}
          className="flex-1 py-3 px-6 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition-colors"
        >
          ⬇️ Descargar como Markdown
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
