"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

import UserInputForm, { UserFormData } from "@/components/UserInputForm";
import OutlineReview from "@/components/OutlineReview";
import GenerationProgress from "@/components/GenerationProgress";
import BookDisplay from "@/components/BookDisplay";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

type AppStep = "form" | "outline" | "writing" | "done" | "error";

interface StatusPayload {
  status: string;
  outline?: {
    title: string;
    chapters: {
      title: string;
      level: number;
      sections: { title: string; subsections: { title: string; focus: string }[] }[];
    }[];
  };
  sections_count?: number;
  written_count?: number;
  email_sent?: boolean;
}

interface SessionState {
  threadId: string;
  token: string;
}

// Thin authenticated fetch wrapper
async function apiFetch(url: string, token: string, init?: RequestInit) {
  return fetch(url, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Session-Token": token, ...(init?.headers ?? {}) },
  });
}

export default function Home() {
  const [step, setStep] = useState<AppStep>("form");
  const [session, setSession] = useState<SessionState | null>(null);
  const [outline, setOutline] = useState<StatusPayload["outline"] | null>(null);
  const [sectionsCount, setSectionsCount] = useState(0);
  const [writtenCount, setWrittenCount] = useState(0);
  const [bookTitle, setBookTitle] = useState("");
  const [bookContent, setBookContent] = useState("");
  const [emailSent, setEmailSent] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  // ── SSE for writing phase ─────────────────────────────────────────────────
  const startSSE = useCallback((threadId: string, token: string) => {
    esRef.current?.close();
    const url = `${BACKEND}/api/stream/${threadId}?x_session_token=${token}`;
    // Note: EventSource doesn't support custom headers, so token sent as query param
    // The backend reads it from either header or query param
    const es = new EventSource(url);
    esRef.current = es;

    es.onmessage = async (e) => {
      const data = JSON.parse(e.data);
      setWrittenCount(data.written_count ?? 0);
      setSectionsCount(data.total_count ?? 0);

      if (data.status === "done") {
        es.close();
        const res = await apiFetch(`${BACKEND}/api/book/${threadId}`, token);
        if (res.ok) {
          const book = await res.json();
          setBookTitle(book.title);
          setBookContent(book.content);
          setEmailSent(book.email_sent ?? false);
          setStep("done");
        }
      }
    };

    es.onerror = () => {
      es.close();
      setError("Se perdió la conexión con el servidor. Recarga la página para ver si el libro está listo.");
    };
  }, []);

  useEffect(() => () => esRef.current?.close(), []);

  // ── Polling for outline phase ────────────────────────────────────────────
  const pollForOutline = useCallback(async (threadId: string, token: string) => {
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      const res = await apiFetch(`${BACKEND}/api/status/${threadId}`, token);
      if (!res.ok) return;
      const data: StatusPayload = await res.json();
      if (data.status === "awaiting_approval" && data.outline) {
        clearInterval(interval);
        setOutline(data.outline);
        setSectionsCount(data.sections_count ?? 0);
        setStep("outline");
        setLoading(false);
      }
      if (attempts > 90) {
        clearInterval(interval);
        setError("Tiempo de espera agotado generando el esquema. Intenta de nuevo.");
        setLoading(false);
      }
    }, 2000);
  }, []);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleFormSubmit = async (data: UserFormData) => {
    setLoading(true);
    setError(null);
    setUserEmail(data.email);
    try {
      const res = await fetch(`${BACKEND}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error(`Error ${res.status}: ${await res.text()}`);
      const { thread_id, session_token } = await res.json();
      setSession({ threadId: thread_id, token: session_token });
      pollForOutline(thread_id, session_token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error desconocido");
      setLoading(false);
    }
  };

  const handleApprove = async (feedback?: string) => {
    if (!session) return;
    setLoading(true);
    try {
      const res = await apiFetch(`${BACKEND}/api/approve/${session.threadId}`, session.token, {
        method: "POST",
        body: JSON.stringify({ approved: true, feedback: feedback ?? "" }),
      });
      if (!res.ok) throw new Error(await res.text());
      setStep("writing");
      startSSE(session.threadId, session.token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al aprobar");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (feedback: string) => {
    if (!session) return;
    setLoading(true);
    try {
      await apiFetch(`${BACKEND}/api/approve/${session.threadId}`, session.token, {
        method: "POST",
        body: JSON.stringify({ approved: false, feedback }),
      });
      pollForOutline(session.threadId, session.token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al regenerar");
      setLoading(false);
    }
  };

  const handleReset = () => {
    esRef.current?.close();
    setStep("form");
    setSession(null);
    setOutline(null);
    setSectionsCount(0);
    setWrittenCount(0);
    setBookTitle("");
    setBookContent("");
    setEmailSent(false);
    setUserEmail("");
    setError(null);
    setLoading(false);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-300 flex items-start justify-between gap-4">
              <span>⚠️ {error}</span>
              <button onClick={() => setError(null)} className="underline text-sm shrink-0">Cerrar</button>
            </div>
          )}

          {step === "form" && <UserInputForm onSubmit={handleFormSubmit} loading={loading} />}

          {step === "outline" && outline && (
            <OutlineReview
              outline={outline}
              sectionsCount={sectionsCount}
              onApprove={handleApprove}
              onRegenerate={handleRegenerate}
              loading={loading}
            />
          )}

          {step === "writing" && (
            <GenerationProgress writtenCount={writtenCount} totalCount={sectionsCount} />
          )}

          {step === "done" && session && (
            <BookDisplay
              threadId={session.threadId}
              sessionToken={session.token}
              title={bookTitle}
              content={bookContent}
              emailSent={emailSent}
              userEmail={userEmail}
              onReset={handleReset}
            />
          )}
        </div>
      </div>

      <CopilotSidebar
        defaultOpen={false}
        labels={{
          title: "Asistente de Biohacking",
          initial: "¡Hola! Puedo ayudarte a entender los conceptos del libro o responder preguntas sobre biohacking.",
        }}
      />
    </CopilotKit>
  );
}
