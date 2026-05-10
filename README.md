# 🧬 Biohacking Book Generator

A multiagent AI web application that generates a fully personalized biohacking book based on your health profile, goals, and lifestyle. The book arrives in your inbox as a **PDF** and **Markdown** file.

---

## How it works

1. **Fill the form** — age, sex, location, health issues, goals, lifestyle, and your email
2. **Architect Agent** (Claude Opus 4.7) designs a personalized 5-level book outline
3. **You review** the outline and approve it or request changes
4. **Writer Agents** (Claude Sonnet 4.6) write all subsections in parallel
5. **Book delivered** to your email as PDF + Markdown

### The 5 biohacking levels

| Level | Name | Examples |
|-------|------|---------|
| 1 | Fundamentos | Drink 2L water, sleep 8h, avoid ultra-processed foods |
| 2 | Optimización Básica | Sleep quality, meal timing, basic supplements |
| 3 | Optimización Intermedia | HRV tracking, cold exposure, intermittent fasting |
| 4 | Biohacking Avanzado | Zone 2 training, sauna protocols, biomarker-guided supplements |
| 5 | Ajuste Fino | Eat the whole orange (not juice) to avoid glucose spikes |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 · TypeScript · Tailwind CSS · CopilotKit |
| Backend | FastAPI · LangGraph 1.1.x · LangChain |
| AI Agents | Claude Opus 4.7 (Architect) · Claude Sonnet 4.6 (Writers) |
| Model gateway | OpenRouter |
| PDF | WeasyPrint |
| Email | Resend |
| Persistence | SQLite (LangGraph checkpointer) |
| Package manager | uv |
| Deployment | Vercel (frontend) · Render (backend) |

---

## Project structure

```
.
├── frontend/               # Next.js app
│   └── src/
│       ├── app/
│       │   ├── page.tsx               # Main orchestrator (form → outline → progress → book)
│       │   └── api/copilotkit/route.ts
│       └── components/
│           ├── UserInputForm.tsx
│           ├── OutlineReview.tsx      # HITL review step
│           ├── GenerationProgress.tsx
│           └── BookDisplay.tsx
└── backend/                # FastAPI + LangGraph
    ├── main.py
    ├── pyproject.toml      # uv dependencies
    ├── Dockerfile
    ├── api/
    │   └── routes.py       # REST endpoints
    └── graph/
        ├── state.py        # TypedDict schemas
        ├── graph.py        # LangGraph StateGraph
        ├── llm.py          # LLM factory (real + FakeLLM for tests)
        ├── pdf.py          # Markdown → PDF (WeasyPrint)
        ├── mailer.py       # Email delivery (Resend)
        └── nodes/
            ├── architect.py  # Outline generation + HITL interrupt
            ├── writer.py     # Parallel subsection writer
            └── assembler.py  # Final assembly + PDF + email
```

---

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) — `pip install uv`
- [OpenRouter](https://openrouter.ai) API key
- [Resend](https://resend.com) API key (free tier: 3,000 emails/month)

### 1. Clone and configure

```bash
git clone https://github.com/camorales197/your_biohacking_book.git
cd your_biohacking_book
```

### 2. Backend

```bash
cd backend
cp .env.example .env
# Edit .env: set OPENROUTER_API_KEY and RESEND_API_KEY
uv sync
uv run uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 is already set
npm install
npm run dev
```

Open **http://localhost:3000**

### Or with Docker

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up --build
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | Get at [openrouter.ai](https://openrouter.ai) |
| `RESEND_API_KEY` | ✅ | Get at [resend.com](https://resend.com) |
| `EMAIL_FROM` | — | Sender address (`onboarding@resend.dev` for testing) |
| `ARCHITECT_MODEL` | — | Default: `anthropic/claude-opus-4-7` |
| `WRITER_MODEL` | — | Default: `anthropic/claude-sonnet-4-6` |
| `CORS_ORIGINS` | — | Default: `http://localhost:3000` |
| `CHECKPOINT_DB_PATH` | — | Default: `./checkpoints.db` |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | ✅ | FastAPI backend URL |

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/generate` | Start generation, returns `thread_id` |
| `GET` | `/api/status/{thread_id}` | Poll current status + progress |
| `POST` | `/api/approve/{thread_id}` | Approve outline or request changes |
| `GET` | `/api/book/{thread_id}` | Get final book (Markdown) |
| `GET` | `/api/book/{thread_id}/pdf` | Download book as PDF |
| `GET` | `/health` | Health check |

---

## Running tests

```bash
cd backend
TESTING=true uv run pytest tests/ -v
```

All tests use `FakeLLM` — no real API calls are made.

---

## Deployment

### Backend → Render (free tier)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect your repo
3. Render auto-detects `render.yaml` — click **Apply**
4. In the Render dashboard → **Environment** → add `OPENROUTER_API_KEY` and `RESEND_API_KEY`

### Frontend → Vercel (free tier)

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your repo
2. Set **Root Directory** to `frontend`
3. Add environment variable: `NEXT_PUBLIC_BACKEND_URL` = your Render URL
4. Deploy

> **Note:** Render's free tier sleeps after 15 min of inactivity. The first request after sleep takes ~30s.

---

## Cost estimate per book

| Model | Task | Approx. cost |
|-------|------|-------------|
| Claude Opus 4.7 | Outline generation (~3k tokens) | ~$0.045 |
| Claude Sonnet 4.6 | ~20 subsections × ~400 words | ~$0.15–0.30 |
| **Total per book** | | **~$0.20–$0.35** |

---

## License

MIT
