"use client";

import { useState, useEffect, useCallback } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

import UserInputForm, { UserFormData } from "@/components/UserInputForm";
import OutlineReview from "@/components/OutlineReview";
import GenerationProgress from "@/components/GenerationProgress";
import BookDisplay from "@/components/BookDisplay";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

type AppStep = "form" | "outline" | "writing" | "done" | "error";

interface StatusPayload {
  status: string;
  outline?: {
    title: string;
    chapters: {
      title: string;
      level: number;
      sections: {
        title: string;
        subsections: { title: string; focus: string }[];
      }[];
    }[];
  };
  sections_count?: number;
  written_count?: number;
}

export default function Home() {
  const [step, setStep] = useState<AppStep>("form");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [statusData, setStatusData] = useState<StatusPayload | null>(null);
  const [bookTitle, setBookTitle] = useState("");
  const [bookContent, setBookContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Polling ───────────────────────────────────────────────────────────────
  const pollStatus = useCallback(async (tid: string) => {
    const res = await fetch(`${BACKEND_URL}/api/status/${tid}`);
    if (!res.ok) return;
    const data: StatusPayload = await res.json();
    setStatusData(data);
    return data;
  }, []);

  useEffect(() => {
    if (!threadId || step !== "writing") return;

    const interval = setInterval(async () => {
      const data = await pollStatus(threadId);
      if (!data) return;

      if (data.status === "done") {
        clearInterval(interval);
        const bookRes = await fetch(`${BACKEND_URL}/api/book/${threadId}`);
        if (bookRes.ok) {
          const book = await bookRes.json();
          setBookTitle(book.title);
          setBookContent(book.content);
          setStep("done");
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [threadId, step, pollStatus]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleFormSubmit = async (data: UserFormData) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`Error ${res.status}: ${await res.text()}`);
      const { thread_id } = await res.json();
      setThreadId(thread_id);

      // Poll until architect finishes and interrupt pauses
      let attempts = 0;
      const waitForOutline = setInterval(async () => {
        attempts++;
        const d = await pollStatus(thread_id);
        if (d?.status === "awaiting_approval" || d?.outline) {
          clearInterval(waitForOutline);
          setStep("outline");
          setLoading(false);
        }
        if (attempts > 60) {
          clearInterval(waitForOutline);
          setError("Tiempo de espera agotado. Intenta de nuevo.");
          setLoading(false);
        }
      }, 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido");
      setLoading(false);
    }
  };

  const handleApprove = async (feedback?: string) => {
    if (!threadId) return;
    setLoading(true);
    try {
      await fetch(`${BACKEND_URL}/api/approve/${threadId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved: true, feedback: feedback ?? "" }),
      });
      setStep("writing");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al aprobar");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (feedback: string) => {
    if (!threadId) return;
    setLoading(true);
    try {
      await fetch(`${BACKEND_URL}/api/approve/${threadId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved: false, feedback }),
      });

      // Poll again until new outline arrives
      let attempts = 0;
      const waitForOutline = setInterval(async () => {
        attempts++;
        const d = await pollStatus(threadId);
        if (d?.status === "awaiting_approval") {
          clearInterval(waitForOutline);
          setLoading(false);
        }
        if (attempts > 60) {
          clearInterval(waitForOutline);
          setError("Tiempo de espera agotado.");
          setLoading(false);
        }
      }, 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al regenerar");
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStep("form");
    setThreadId(null);
    setStatusData(null);
    setBookTitle("");
    setBookContent("");
    setError(null);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300">
              ⚠️ {error}
              <button onClick={() => setError(null)} className="ml-4 underline text-sm">
                Cerrar
              </button>
            </div>
          )}

          {step === "form" && (
            <UserInputForm onSubmit={handleFormSubmit} loading={loading} />
          )}

          {step === "outline" && statusData?.outline && (
            <OutlineReview
              outline={statusData.outline}
              sectionsCount={statusData.sections_count ?? 0}
              onApprove={handleApprove}
              onRegenerate={handleRegenerate}
              loading={loading}
            />
          )}

          {step === "writing" && (
            <GenerationProgress
              writtenCount={statusData?.written_count ?? 0}
              totalCount={statusData?.sections_count ?? 0}
            />
          )}

          {step === "done" && (
            <BookDisplay
              title={bookTitle}
              content={bookContent}
              onReset={handleReset}
            />
          )}
        </div>
      </div>

      <CopilotSidebar
        defaultOpen={false}
        labels={{
          title: "Asistente de Biohacking",
          initial: "¡Hola! Soy tu asistente de biohacking. Puedo ayudarte a entender los conceptos de tu libro o responder preguntas sobre biohacking.",
        }}
      />
    </CopilotKit>
  );
}
