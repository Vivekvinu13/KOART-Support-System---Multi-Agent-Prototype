# KOART Support System — Multi-Agent Prototype

## Agent routing

1. **Agent 1 — Front Door / Triage**: always receives the ticket first. It answers basic documented questions and routes support questions to Agent 2 or data questions to Agent 3.
2. **Agent 2 — Support Queue**: uses the KOART Request & Support Delivery Process, Complete Guide, Overview and OU process diagrams. It handles documented support/request procedures and routes configuration/feature/enhancement/change requests to Agent 4.
3. **Agent 3 — Data Analyst**: uses `OU_Tasks_SKUs.xlsx` plus the supplied Quality and Volume dashboard snapshots for quantitative questions.
4. **Agent 4 — Solution Architect**: scopes configuration/feature/change requests, asks for missing information, and provides the configured intake form URL plus `solutionarchitect@koart.com`.

The requested three-agent flow is preserved for the main paths, with Agent 4 added for the Solution Architect escalation described in the requirements.

## Grounding

The source files supplied with this prototype are copied into `backend/data/`. The MCP server exposes:
- `search_koart_knowledge`
- `query_koart_data`
- `get_ou_metrics`

The Quality dashboard values are encoded as a snapshot because the source was provided as an image. The snapshot shown in the supplied image includes global average amends of 1.8 and OU values such as ASP 2.2, Africa 1.9, EU 1.8, LATAM 1.7, NA 1.7, EME 1.6, INSWA 1.6, GCM 1.4, SK 1.5 and JP 1.5.

## Run

### Backend
```bash
cd koart-support-chatbot
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# edit backend/.env and set OPENAI_API_KEY
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Notes

- `gpt-4o-mini` is the default requested model; change `OPENAI_MODEL` to another OpenAI model if desired.
- Set `SOLUTION_ARCHITECT_FORM_URL` to the real production form URL. The local demo defaults to `/solution-architect/request`.
- The MCP server is launched by AutoGen's `McpWorkbench` over stdio.
- This is a prototype: add authentication, ticket persistence, audit logging, PII controls, rate limiting, and a real ticketing integration before production use.
