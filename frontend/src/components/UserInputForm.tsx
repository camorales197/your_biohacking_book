"use client";

import { useState } from "react";

export interface UserFormData {
  email: string;
  age: number;
  sex: string;
  location: string;
  health_issues: string[];
  lifestyle: string;
  goals: string[];
  other_info: string;
}

interface Props {
  onSubmit: (data: UserFormData) => void;
  loading: boolean;
}

export default function UserInputForm({ onSubmit, loading }: Props) {
  const [email, setEmail] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [sex, setSex] = useState("");
  const [location, setLocation] = useState("");
  const [healthIssues, setHealthIssues] = useState("");
  const [lifestyle, setLifestyle] = useState("");
  const [goals, setGoals] = useState("");
  const [otherInfo, setOtherInfo] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !age || !sex || !location || !lifestyle || !goals) return;

    onSubmit({
      email,
      age: Number(age),
      sex,
      location,
      health_issues: healthIssues
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      lifestyle,
      goals: goals
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      other_info: otherInfo,
    });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
          🧬 Tu Libro de Biohacking
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400 text-lg">
          Genera un libro personalizado de biohacking basado en tu perfil de salud
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            📧 Tu correo electrónico *
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="tu@email.com"
          />
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Te enviaremos el libro generado en PDF y Markdown cuando esté listo.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              Edad *
            </label>
            <input
              type="number"
              min={10}
              max={120}
              value={age}
              onChange={(e) => setAge(e.target.value ? Number(e.target.value) : "")}
              required
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="35"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              Sexo *
            </label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">Selecciona...</option>
              <option value="hombre">Hombre</option>
              <option value="mujer">Mujer</option>
              <option value="otro">Otro</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            Ubicación *
          </label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Madrid, España"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            Problemas de salud{" "}
            <span className="text-zinc-400 font-normal">(separados por comas)</span>
          </label>
          <input
            type="text"
            value={healthIssues}
            onChange={(e) => setHealthIssues(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="resistencia a la insulina, insomnio leve, estrés crónico"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            Estilo de vida actual *
          </label>
          <textarea
            value={lifestyle}
            onChange={(e) => setLifestyle(e.target.value)}
            required
            rows={3}
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
            placeholder="Trabajo de oficina 8h, sedentario, duermo 6h, como fuera con frecuencia..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            Objetivos *{" "}
            <span className="text-zinc-400 font-normal">(separados por comas)</span>
          </label>
          <input
            type="text"
            value={goals}
            onChange={(e) => setGoals(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="más energía, perder grasa, mejorar concentración, dormir mejor"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
            Información adicional
          </label>
          <textarea
            value={otherInfo}
            onChange={(e) => setOtherInfo(e.target.value)}
            rows={2}
            className="w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
            placeholder="Cualquier otra cosa relevante: medicación, restricciones alimentarias, nivel fitness..."
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-6 bg-green-600 hover:bg-green-700 disabled:bg-zinc-400 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⚙️</span> Generando esquema...
            </>
          ) : (
            <>🚀 Generar mi libro de biohacking</>
          )}
        </button>
      </form>
    </div>
  );
}
