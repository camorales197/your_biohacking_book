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
  sleep_hours: number;
  exercise_frequency: string;
  diet_type: string;
  stress_level: string;
  energy_level: string;
}

interface Props {
  onSubmit: (data: UserFormData) => void;
  loading: boolean;
}

const inputCls =
  "w-full px-3 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-green-500";

const labelCls = "block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1";

export default function UserInputForm({ onSubmit, loading }: Props) {
  const [email, setEmail] = useState("");
  const [age, setAge] = useState<number | "">("");
  const [sex, setSex] = useState("");
  const [location, setLocation] = useState("");
  const [healthIssues, setHealthIssues] = useState("");
  const [lifestyle, setLifestyle] = useState("");
  const [goals, setGoals] = useState("");
  const [otherInfo, setOtherInfo] = useState("");
  const [sleepHours, setSleepHours] = useState<number | "">(7);
  const [exerciseFrequency, setExerciseFrequency] = useState("3-4x/semana");
  const [dietType, setDietType] = useState("omnívoro");
  const [stressLevel, setStressLevel] = useState("moderado");
  const [energyLevel, setEnergyLevel] = useState("moderado");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !age || !sex || !location || !lifestyle || !goals) return;
    onSubmit({
      email,
      age: Number(age),
      sex,
      location,
      health_issues: healthIssues.split(",").map((s) => s.trim()).filter(Boolean),
      lifestyle,
      goals: goals.split(",").map((s) => s.trim()).filter(Boolean),
      other_info: otherInfo,
      sleep_hours: Number(sleepHours) || 7,
      exercise_frequency: exerciseFrequency,
      diet_type: dietType,
      stress_level: stressLevel,
      energy_level: energyLevel,
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
        {/* Email */}
        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
          <label className={labelCls}>📧 Correo electrónico *</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className={inputCls} placeholder="tu@email.com" />
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Te enviaremos el libro en PDF y Markdown cuando esté listo.
          </p>
        </div>

        {/* Age + Sex */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Edad *</label>
            <input type="number" min={10} max={120} value={age} onChange={(e) => setAge(e.target.value ? Number(e.target.value) : "")} required className={inputCls} placeholder="35" />
          </div>
          <div>
            <label className={labelCls}>Sexo *</label>
            <select value={sex} onChange={(e) => setSex(e.target.value)} required className={inputCls}>
              <option value="">Selecciona...</option>
              <option value="hombre">Hombre</option>
              <option value="mujer">Mujer</option>
              <option value="otro">Otro</option>
            </select>
          </div>
        </div>

        {/* Location */}
        <div>
          <label className={labelCls}>Ubicación *</label>
          <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} required className={inputCls} placeholder="Madrid, España" />
        </div>

        {/* Sleep + Exercise */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Horas de sueño/noche</label>
            <input type="number" min={2} max={12} step={0.5} value={sleepHours} onChange={(e) => setSleepHours(e.target.value ? Number(e.target.value) : "")} className={inputCls} placeholder="7" />
          </div>
          <div>
            <label className={labelCls}>Frecuencia de ejercicio</label>
            <select value={exerciseFrequency} onChange={(e) => setExerciseFrequency(e.target.value)} className={inputCls}>
              <option value="ninguno">Ninguno</option>
              <option value="1-2x/semana">1-2x / semana</option>
              <option value="3-4x/semana">3-4x / semana</option>
              <option value="5+/semana">5+ / semana</option>
            </select>
          </div>
        </div>

        {/* Diet + Stress + Energy */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Dieta</label>
            <select value={dietType} onChange={(e) => setDietType(e.target.value)} className={inputCls}>
              <option value="omnívoro">Omnívoro</option>
              <option value="mediterráneo">Mediterránea</option>
              <option value="vegetariano">Vegetariano</option>
              <option value="vegano">Vegano</option>
              <option value="keto">Keto</option>
              <option value="otro">Otro</option>
            </select>
          </div>
          <div>
            <label className={labelCls}>Nivel de estrés</label>
            <select value={stressLevel} onChange={(e) => setStressLevel(e.target.value)} className={inputCls}>
              <option value="bajo">Bajo</option>
              <option value="moderado">Moderado</option>
              <option value="alto">Alto</option>
              <option value="muy alto">Muy alto</option>
            </select>
          </div>
          <div>
            <label className={labelCls}>Nivel de energía</label>
            <select value={energyLevel} onChange={(e) => setEnergyLevel(e.target.value)} className={inputCls}>
              <option value="bajo">Bajo</option>
              <option value="moderado">Moderado</option>
              <option value="alto">Alto</option>
            </select>
          </div>
        </div>

        {/* Health issues */}
        <div>
          <label className={labelCls}>Problemas de salud <span className="font-normal text-zinc-400">(separados por comas)</span></label>
          <input type="text" value={healthIssues} onChange={(e) => setHealthIssues(e.target.value)} className={inputCls} placeholder="resistencia a la insulina, insomnio leve, estrés crónico" />
        </div>

        {/* Lifestyle */}
        <div>
          <label className={labelCls}>Estilo de vida actual *</label>
          <textarea value={lifestyle} onChange={(e) => setLifestyle(e.target.value)} required rows={3} className={`${inputCls} resize-none`} placeholder="Trabajo de oficina 8h, sedentario, como fuera con frecuencia, viajo mucho..." />
        </div>

        {/* Goals */}
        <div>
          <label className={labelCls}>Objetivos * <span className="font-normal text-zinc-400">(separados por comas)</span></label>
          <input type="text" value={goals} onChange={(e) => setGoals(e.target.value)} required className={inputCls} placeholder="más energía, perder grasa, mejorar concentración, dormir mejor" />
        </div>

        {/* Other info */}
        <div>
          <label className={labelCls}>Información adicional</label>
          <textarea value={otherInfo} onChange={(e) => setOtherInfo(e.target.value)} rows={2} className={`${inputCls} resize-none`} placeholder="Medicación, restricciones alimentarias, lesiones, nivel fitness actual..." />
        </div>

        <button type="submit" disabled={loading} className="w-full py-3 px-6 bg-green-600 hover:bg-green-700 disabled:bg-zinc-400 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2">
          {loading ? <><span className="animate-spin">⚙️</span> Generando esquema...</> : <>🚀 Generar mi libro de biohacking</>}
        </button>
      </form>
    </div>
  );
}
