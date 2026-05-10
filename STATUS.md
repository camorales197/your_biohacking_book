# Project Status: Generador Multiagente de Libros de Biohacking

## Architecture
- **Frontend**: Next.js 15 + TypeScript + CopilotKit → deploy Vercel
- **Backend**: FastAPI + LangGraph 1.1.10 + LangChain → deploy Render
- **LLMs**: Gemini 2.0 Flash (Architect) + Claude Haiku 4.5 (Writers) via OpenRouter
- **Persistence**: MemorySaver (tests) / SqliteSaver (production)

---

## Phase Status

| Phase | Status | Description |
|-------|--------|-------------|
| 1 - Scaffolding | ✅ DONE | Next.js + FastAPI initialized, communication verified |
| 2 - LangGraph Skeleton | ✅ DONE | State schemas, 5-node graph, interrupt pattern |
| 3 - Architect Agent + HITL | ✅ DONE | Split architect/hitl nodes, Command(resume=...) |
| 4 - Parallel Writers | ✅ DONE | Send() API map-reduce, assembler node |
| 5 - Dockerization | ✅ DONE | Dockerfile, docker-compose, render.yaml |

All 6 mock tests pass: `TESTING=true python -m pytest tests/test_graph_mock.py -v`

---

## Completed Tasks
- [x] STATUS.md created
- [x] Next.js 15 + TypeScript frontend with CopilotKit
- [x] FastAPI backend with all endpoints
- [x] LangGraph 5-node graph (architect → hitl → route_writers → writer×N → assembler)
- [x] HITL interrupt pattern (architect commits state, hitl_node pauses, Command(resume=...) resumes)
- [x] Parallel Send() API fan-out for writer agents
- [x] All 6 mock tests pass (FakeLLM, no real API calls)
- [x] Dockerfile + docker-compose + render.yaml

## Key Technical Decisions
- **architect_node** commits outline to state THEN **hitl_node** calls `interrupt()`
  - Reason: `interrupt()` inside a node freezes mid-execution without committing state
- **Resume** uses `Command(resume={...})` from `langgraph.types`
- **FakeChatLLM** custom class (langchain_community FakeListLLM is for base LLMs, not chat)
- **DeepAgents dropped**: deterministic pipeline with bounded node responsibilities

## To Run Locally
```bash
# Backend
cd backend
cp .env.example .env  # add OPENROUTER_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
cp .env.local.example .env.local
npm run dev
# → http://localhost:3000
```

## To Deploy
1. **Backend → Render**: Push to GitHub, connect repo, use `render.yaml`, set `OPENROUTER_API_KEY` in dashboard
2. **Frontend → Vercel**: `vercel --prod` from `/frontend`, set `NEXT_PUBLIC_BACKEND_URL` to Render URL

## Next Steps (post-MVP)
- Add real-time SSE streaming of writer progress (replace polling)
- Add CopilotKit CoAgent integration for deeper AI sidebar
- Add PDF export option
- Add user authentication for saved books

## Blockers
- None

---

*Last updated: All 5 phases complete*
