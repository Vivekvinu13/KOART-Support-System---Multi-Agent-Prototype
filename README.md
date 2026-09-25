# KOART Support System — Multi-Agent Prototype

A multi-agent AI support prototype for KOART 2.0 that provides a single conversational front door for users and intelligently routes requests to specialist agents.

## Overview

The system combines:

- React + Vite
- Three.js
- Python + FastAPI
- WebSockets
- Microsoft AutoGen
- Model Context Protocol (MCP)
- OpenAI models
- KOART documentation
- KOART operational data
- Quality and Volume dashboard information

Every request starts with **Agent 1 — Front Door / Triage**.

```text
                         User
                           |
                           v
                +----------------------+
                | Agent 1              |
                | Front Door / Triage  |
                +----------+-----------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Direct Answer   Agent 2       Agent 3
                       Support        Data Analyst
                       Queue
                         |
                         v
                      Agent 4
                 Solution Architect
```

The frontend also provides a Three.js 3D visualization of the agent handoffs.

---

## Core Objectives

- Provide a single front door for KOART support.
- Ensure Agent 1 receives every request first.
- Answer simple, documented questions directly.
- Route operational support questions to Agent 2.
- Route data and metrics questions to Agent 3.
- Route configuration/change requests from Agent 2 to Agent 4.
- Ground responses in supplied KOART documentation and data.
- Prevent unsupported/fabricated answers.
- Hide raw MCP/tool output from users.
- Show agent handoffs in real time.
- Keep the internal Knowledge Base outside the public Git repository.
- Keep real API credentials outside source control.

---

# Architecture

```text
+-------------------------------------------------------+
|                    FRONTEND                           |
|                                                       |
| React + Vite + Three.js                               |
|                                                       |
| - Chat interface                                      |
| - Agent status                                        |
| - Agent cards                                         |
| - Handoff display                                     |
| - 3D orchestration view                               |
| - WebSocket client                                    |
+-----------------------------+-------------------------+
                              |
                              | WebSocket
                              v
+-------------------------------------------------------+
|                    BACKEND                            |
|                                                       |
| FastAPI + AutoGen                                    |
|                                                       |
| - WebSocket endpoint                                  |
| - Agent orchestration                                 |
| - Routing                                             |
| - Agent execution                                     |
| - OpenAI model client                                 |
+-----------------------------+-------------------------+
                              |
                              | MCP
                              v
+-------------------------------------------------------+
|                    MCP LAYER                          |
|                                                       |
| MCP Server + Knowledge/Data tools                     |
|                                                       |
| - Knowledge search                                    |
| - Data answers                                        |
| - OU metrics                                          |
+-----------------------------+-------------------------+
                              |
               +--------------+--------------+
               |                             |
               v                             v
       KOART Knowledge Base             KOART Data
       PDFs / Text                      Excel / Dashboards
```

---

# Multi-Agent Architecture

| Agent | Role | Primary Responsibility |
|---|---|---|
| Agent 1 | Front Door / Triage | Receives every request and determines the route |
| Agent 2 | Support Queue | Handles detailed KOART support and operational process questions |
| Agent 3 | Data Analyst | Handles workbook, quality, volume, and metric questions |
| Agent 4 | Solution Architect | Clarifies configuration, enhancement, feature, and solution-design requests |

---

# Agent 1 — Front Door / Triage

AutoGen agent:

```text
Agent1_Triage
```

Agent 1 is always the first agent.

Responsibilities:

- Understand the user's request.
- Determine the correct specialist.
- Use KOART knowledge tools when factual information is needed.
- Never invent information.
- Never expose raw MCP output.

Internal route states:

```text
ROUTE: DIRECT
ROUTE: SUPPORT
ROUTE: DATA
```

The route marker is removed before the response reaches the user.

### Direct Questions

Examples:

- What is KOART?
- How do I access KOART?
- Where do I access KOART?
- Basic ticket navigation.
- Basic team information.
- Basic access information.

### Support Routing

Agent 1 routes to Agent 2 for:

- Project creation
- SKU creation/update
- Operational procedures
- Artwork approval procedures
- Workflow procedures
- Troubleshooting
- Support tickets
- Detailed KOART operational guidance

Support contact:

```text
support@koart.com
```

### Data Routing

Agent 1 routes to Agent 3 for:

- Metrics
- Counts
- Dashboards
- Projects
- Artworks
- SKUs
- Amends
- Operating Unit statistics
- Volume
- Quality
- Workbook information
- Dashboard information
- Data comparisons

---

# Agent 2 — Support Queue

AutoGen agent:

```text
Agent2_Support
```

Agent 2 provides practical KOART support using the supplied documentation and MCP knowledge tools.

Knowledge sources include:

- KOART Request & Support Delivery Process
- Complete Guide
- KO ART 2.0 Overview
- KOART Operation Guide
- KOART process diagrams

The agent must not expose raw MCP output, raw search results, PDF extraction blocks, or internal tool responses.

## Procedural Questions

Procedures use concise bullet-based steps:

```text
Steps to proceed:

- Step 1 — Short action title
  - Explanation

- Step 2 — Short action title
  - Explanation

- Step 3 — Short action title
  - Explanation
```

## Project Creation

The documented project-creation flow includes:

1. Log in to KOART.
2. Create a new project.
3. Select Market and Project Name.
4. Enter submission information.
5. Add a new SKU.
6. Select project members.

Relevant concepts include:

- Active Projects
- Create New Project
- Market
- Project Name
- Key Reason for Artwork Submission
- FTP Date
- Add New SKU
- Brand
- Flavor
- Auto Select Members
- Multiple approvers

---

# Agent 3 — Data Analyst

AutoGen agent:

```text
Agent3_DataAnalyst
```

Agent 3 answers data questions using only the supplied sources.

## Data Sources

1. `OU_Tasks_SKUs.xlsx`
2. Quality dashboard snapshot
3. Volume dashboard snapshot

The agent must not fabricate values or claim data is live/current unless the source supports it.

For comparisons, Markdown tables are preferred.

Example:

```text
| Operating Unit | Artworks | Share |
|---|---:|---:|
| EU | ... | ... |
| LATAM | ... | ... |
```

If a requested metric is not available:

```text
I couldn't find that metric in the supplied KOART workbook
or dashboard data.
```

---

# Agent 4 — Solution Architect

AutoGen agent:

```text
Agent4_SolutionArchitect
```

Agent 4 handles:

- Configuration requests
- Enhancements
- Features
- Workflow changes
- Migrations
- Solution design

Potential clarification areas:

- Business objective
- Current behavior
- Requested behavior
- Affected Operating Unit / market
- Affected workflow/project type
- Users or roles affected
- Examples/screenshots
- Acceptance criteria

The agent asks only the minimum questions needed.

It must not claim that a change has been approved, developed, configured, tested, or deployed unless supported by the source.

Contact:

```text
solutionarchitect@koart.com
```

Configured form:

```text
SOLUTION_ARCHITECT_FORM_URL
```

---

# Routing Logic

```text
User
 |
 v
Agent 1
 |
 +---- DIRECT ----> User
 |
 +---- SUPPORT ---> Agent 2
 |                    |
 |                    +---- Normal support
 |                    |
 |                    +---- ROUTE: SA
 |                           |
 |                           v
 |                       Agent 4
 |
 +---- DATA ------> Agent 3
```

Agent 2 can produce:

```text
ROUTE: SA
```

for Solution Architect escalation.

---

# MCP Architecture

The project uses AutoGen's MCP integration.

The agent system creates:

```text
McpWorkbench
```

and uses:

```text
StdioServerParams
```

The MCP server is launched with:

```text
python -m backend.mcp_server
```

Conceptually:

```text
AutoGen Agent
     |
     v
McpWorkbench
     |
     v
MCP Server
     |
     +-------------------+
     |                   |
     v                   v
Knowledge Search      Data / Metrics
```

---

# Knowledge Base

The local Knowledge Base is stored under:

```text
backend/data/
```

Example files:

```text
Complete_Guide_KOART_2.0_ESKO_v2.pdf
KOART_Process_Diagrams_All_OUs.pdf
KOART_Request_Delivery_Process.pdf
KO_ART_2.0_Overview.pdf
OU_Tasks_SKUs.xlsx
Quality.png
Team.txt
Volume.png
```

These files contain internal KOART information and are intentionally excluded from the public Git repository.

The agents use retrieved information as internal evidence and rewrite it into user-facing responses.

---

# KOART Documentation

Supplied documentation includes:

- Complete Guide
- KO ART 2.0 Overview
- KOART Operation Guide
- KOART Request & Support Delivery Process
- KOART Global Process Flow / process diagrams
- Team information

KOART access documented in the supplied material:

```text
https://koart.esko-saas.com
```

The Request & Support Delivery Process includes concepts such as:

- Complex Requests
- Project
- Managed Services
- ESKO Project Team
- Feature or Enhancement Request
- ESKO SA / SILC
- Simple Requests

Documented implementation activities include:

```text
Discovery
    |
Resource Planning
    |
Design Workshop
    |
Design Report
    |
Build & Review
    |
UAT
    |
Training / Office Hours
    |
Daily Support
    |
Managed Services
```

The agents should not invent costs or SLAs.

---

# Data Sources

The Data Analyst uses:

```text
OU_Tasks_SKUs.xlsx
Quality dashboard snapshot
Volume dashboard snapshot
```

## Quality Dashboard

The supplied Quality dashboard contains:

- Average Amends Globally
- Current Year Average Amends
- Global Version 1 %
- Current Year Version 1 %
- Total Projects
- Total Artworks
- Average Amends by Operating Unit
- Artwork version distribution

## Volume Dashboard

The supplied Volume dashboard contains:

- Total Projects
- Total Artworks
- Completed
- Cancelled
- WIP
- Market volume
- Artwork volume by Operating Unit

These supplied dashboard values are not automatically live production telemetry.

---

# Frontend

The frontend uses:

- React
- Vite
- Three.js
- CSS
- WebSockets

Primary entry point:

```text
frontend/src/main.jsx
```

The frontend contains:

- KOART branding
- Support conversation
- Connection status
- Agent cards
- Example questions
- Handoff display
- 3D orchestration
- Agent legend
- Request lifecycle cards

Example questions:

```text
How do I access KOART 2.0?
How do I create a new project in KOART?
What is the average amends for ASP?
```

---

# 3D Visualization

The right-hand UI panel contains a Three.js orchestration view.

Agents are represented as colored spheres:

```text
Agent 1 — Front Door / Triage
Agent 2 — Support Queue
Agent 3 — Data Analyst
Agent 4 — Solution Architect
```

Approximate layout:

```text
                         Agent 2
                       Support Queue
                            ●
                            |
                            |
Agent 1 ● ------------------+------------------ ● Agent 4
Front Door                                      Solution Architect
                            |
                            |
                            ●
                         Agent 3
                       Data Analyst
```

Labels beneath the spheres show:

```text
Agent Name
Agent Role
```

Handoff lines are created when route events are received.

Examples:

```text
Agent 1 → Agent 2
Agent 1 → Agent 3
Agent 2 → Agent 4
```

---

# WebSocket Communication

The frontend connects to:

```text
ws://<hostname>:8000/ws/chat
```

Local development:

```text
ws://localhost:8000/ws/chat
```

The frontend handles events including:

```text
ticket
agent_start
agent_end
agent_message
route
final
```

Example route event:

```json
{
  "type": "route",
  "from": "Agent 1",
  "to": "Agent 2"
}
```

Example final event:

```json
{
  "type": "final",
  "agent": "Agent 2",
  "answer": "..."
}
```

---

# Backend

Backend technology:

- Python
- FastAPI
- AutoGen
- OpenAI
- MCP
- WebSockets

Primary components:

```text
backend/
├── __init__.py
├── mcp_server.py
├── requirements.txt
│
└── app/
    ├── __init__.py
    ├── agents.py
    ├── config.py
    ├── knowledge.py
    ├── main.py
    └── metrics.py
```

Central orchestration class:

```text
KoartAgentSystem
```

The system manages:

- OpenAI model configuration
- MCP server parameters
- Agent creation
- Agent execution
- Routing
- Agent events
- Final responses

---

# Agent Execution Lifecycle

```text
Agent Start Event
       |
       v
agent.run(...)
       |
       v
Extract final message
       |
       v
Agent End Event
       |
       v
Return to routing logic
```

Internal route markers are removed before user-facing messages are emitted.

---

# Model Configuration

The development model is:

```text
gpt-4o-mini
```

The API key is read from the environment.

---

# Environment Configuration

Expected variables include:

```text
OPENAI_API_KEY
OPENAI_MODEL
SOLUTION_ARCHITECT_FORM_URL
CORS_ORIGINS
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
SOLUTION_ARCHITECT_FORM_URL=https://your-production-form-url
CORS_ORIGINS=http://localhost:5173
```

The real `.env` file must remain local.

---

# Project Structure

```text
koart-support-chatbot/
│
├── .gitignore
├── README.md
│
├── backend/
│   ├── __init__.py
│   ├── .env.example
│   ├── mcp_server.py
│   ├── requirements.txt
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── config.py
│   │   ├── knowledge.py
│   │   ├── main.py
│   │   └── metrics.py
│   │
│   └── data/
│       └── Local Knowledge Base
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── package-lock.json
    │
    └── src/
        ├── main.jsx
        └── styles.css
```

> Note: Use the actual stylesheet filename present in `frontend/src/` if it differs from the example structure above.

---

# Local-Only Files

The following should not be committed:

```text
.venv/
backend/.env
backend/data/
frontend/node_modules/
__pycache__/
```

---

# Prerequisites

Install:

- Python
- Node.js
- Git

Verify:

```powershell
python --version
node --version
npm.cmd --version
git --version
```

---

# Installation

Clone:

```powershell
git clone https://github.com/Vivekvinu13/KOART-Support-System---Multi-Agent-Prototype.git
```

Enter the project:

```powershell
cd KOART-Support-System---Multi-Agent-Prototype
```

## Backend

Create virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend
equirements.txt
```

## Environment

Create local `.env`:

```powershell
Copy-Item backend\.env.example backend\.env
```

Edit:

```powershell
notepad backend\.env
```

Set the real API key and configuration values.

---

# Knowledge Base Setup

Place approved local Knowledge Base files under:

```text
backend/data/
```

Example:

```text
backend/
└── data/
    ├── Complete_Guide_KOART_2.0_ESKO_v2.pdf
    ├── KOART_Process_Diagrams_All_OUs.pdf
    ├── KOART_Request_Delivery_Process.pdf
    ├── KO_ART_2.0_Overview.pdf
    ├── OU_Tasks_SKUs.xlsx
    ├── Quality.png
    ├── Team.txt
    └── Volume.png
```

Do not commit these files to the public repository.

---

# Running the Backend

From the project root:

```powershell
cd D:\GENAI\koart-support-chatbot
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

WebSocket:

```text
ws://localhost:8000/ws/chat
```

---

# Running the Frontend

Open another terminal:

```powershell
cd D:\GENAI\koart-support-chatbotrontend
```

Install:

```powershell
npm.cmd install
```

Run:

```powershell
npm.cmd run dev
```

Open:

```text
http://localhost:5173/
```

---

# Complete Local Startup

### Terminal 1

```powershell
cd D:\GENAI\koart-support-chatbot
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```

### Terminal 2

```powershell
cd D:\GENAI\koart-support-chatbotrontend
npm.cmd run dev
```

Then open:

```text
http://localhost:5173/
```

---

# Example Questions

## Direct

```text
How do I access KOART 2.0?
```

Flow:

```text
User → Agent 1 → Direct Answer
```

## Support

```text
How do I create a new project in KOART?
```

Flow:

```text
User → Agent 1 → Agent 2
```

## Data

```text
What is the average amends for ASP?
```

Flow:

```text
User → Agent 1 → Agent 3
```

## Configuration

```text
We need to change the KOART workflow for a specific market.
```

Possible flow:

```text
User → Agent 1 → Agent 2 → Agent 4
```

---

# Support Escalation

Support:

```text
support@koart.com
```

Solution Architect:

```text
solutionarchitect@koart.com
```

Feature/change request form:

```text
SOLUTION_ARCHITECT_FORM_URL
```

---

# Response Rules

Agents should:

- Keep responses clear.
- Avoid unsupported claims.
- Use Markdown bullets where appropriate.
- Use bold for important values.
- Keep paragraphs short.
- Avoid exposing internal tools.

They should not expose:

- Raw MCP output
- Raw search results
- Python objects
- Internal route markers
- Raw Excel rows
- Large extracted PDF sections
- Internal tool responses

---

# Security

Never commit:

```text
backend/.env
backend/data/
```

Never expose:

```text
OPENAI_API_KEY
```

The repository should contain `.env.example`, not the real `.env`.

Production should use secure secret management, authentication, authorization, HTTPS/WSS, restricted CORS, rate limiting, and audit logging.

---

# GitHub

Repository:

https://github.com/Vivekvinu13/KOART-Support-System---Multi-Agent-Prototype

Basic workflow:

```powershell
git status
git add .
git commit -m "Describe the change"
git push
```

README update:

```powershell
git add README.md
git commit -m "Update project documentation"
git push
```

---

# Troubleshooting

## `npm` PowerShell Error

If PowerShell blocks `npm.ps1`, use:

```powershell
npm.cmd --version
npm.cmd install
npm.cmd run dev
```

## Frontend Shows `Connecting…`

Verify backend:

```powershell
uvicorn backend.app.main:app --reload --port 8000
```

Verify WebSocket:

```text
ws://localhost:8000/ws/chat
```

## Knowledge Base Errors

Verify:

```text
backend/data/
```

exists locally and contains the required files.

## OpenAI Authentication

Check:

```text
backend/.env
```

and:

```env
OPENAI_API_KEY=your_real_openai_api_key
```

## MCP Startup

The system launches:

```text
python -m backend.mcp_server
```

Verify:

- Virtual environment is active.
- Dependencies are installed.
- Project root is the working directory.
- `backend/mcp_server.py` exists.
- Required local data exists.

---

# Current Prototype Scope

The current implementation demonstrates:

- Multi-agent routing
- Agent specialization
- Knowledge-grounded support
- Data-oriented responses
- Configuration/change escalation
- MCP integration
- AutoGen orchestration
- FastAPI backend
- WebSocket communication
- React frontend
- Three.js visualization
- Live agent handoffs
- Local Knowledge Base integration
- Environment-based configuration

---

# Known Limitations

This is a prototype, not a complete production deployment.

Production work would still be required for:

- Enterprise authentication
- Identity integration
- Role-based authorization
- Persistent conversations
- Production ticketing integration
- Service Desk integration
- Production monitoring
- Advanced observability
- Automated evaluation
- Model governance
- Prompt/version management
- Secure production Knowledge Base ingestion
- Production deployment infrastructure
- Secure WebSockets
- HTTPS/WSS
- Rate limiting
- Production secret management
- Data access controls
- Audit logging

---

# Future Enhancements

Potential extensions:

- Service Desk integration
- Ticket creation/status
- Training specialist
- Workflow administration agent
- User administration agent
- Reporting agent
- Platform administration agent
- Persistent conversations
- User context
- Ticket references
- Agent routing analytics
- Model/tool latency monitoring
- Token usage monitoring
- User feedback
- Automated evaluation
- Production observability

---

# End-to-End Examples

## Direct Access

```text
User
  |
  v
Agent 1
  |
  v
Knowledge Search
  |
  v
Direct Answer
```

## Project Creation

```text
User
  |
  v
Agent 1
  |
  | ROUTE: SUPPORT
  v
Agent 2
  |
  v
KOART Operation Guide
  |
  v
Step-by-step response
```

## Data Question

```text
User
  |
  v
Agent 1
  |
  | ROUTE: DATA
  v
Agent 3
  |
  v
OU / Quality / Volume Data
  |
  v
Data Answer
```

## Configuration Request

```text
User
  |
  v
Agent 1
  |
  | ROUTE: SUPPORT
  v
Agent 2
  |
  | ROUTE: SA
  v
Agent 4
  |
  +---- Clarification questions
  |
  +---- Solution Architect contact
  |
  +---- Feature/change request form
```

---

# Design Principles

## 1. One Front Door

Every request starts with Agent 1.

## 2. Specialist Ownership

```text
Agent 1 → Triage
Agent 2 → Support
Agent 3 → Data
Agent 4 → Solution Architecture
```

## 3. Grounded Answers

Agents use supplied KOART sources when factual information is required.

## 4. No Fabrication

Agents should not fabricate unsupported information.

## 5. Controlled Tool Access

Agents interact with Knowledge and Data functionality through MCP.

## 6. Transparent Orchestration

The UI exposes:

- Agent status
- Handoff messages
- 3D agent nodes
- Handoff lines
- Active-agent highlighting

## 7. Separation of Secrets and Source

Application source is stored in GitHub.

Sensitive credentials and internal Knowledge Base files remain local.

---

# Technology Summary

| Layer | Technology |
|---|---|
| UI | React |
| Build Tool | Vite |
| 3D Visualization | Three.js |
| Backend | Python |
| API Framework | FastAPI |
| Agent Framework | Microsoft AutoGen |
| Tool Protocol | MCP |
| Model Provider | OpenAI |
| Communication | WebSockets |
| Knowledge | KOART PDFs / text |
| Data | Excel + dashboard snapshots |
| Source Control | Git / GitHub |

---

# Final Architecture

```text
                                USER
                                  |
                                  v
                    +---------------------------+
                    |       React Frontend      |
                    |                           |
                    | Chat + Agent Status       |
                    | 3D Agent Visualization    |
                    +-------------+-------------+
                                  |
                                  | WebSocket
                                  v
                    +---------------------------+
                    |       FastAPI Backend     |
                    |                           |
                    | KoartAgentSystem          |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |       AutoGen Layer       |
                    |                           |
                    | Agent 1                   |
                    | Front Door / Triage       |
                    +-------------+-------------+
                                  |
               +------------------+------------------+
               |                  |                  |
               | DIRECT           | SUPPORT          | DATA
               |                  |                  |
               v                  v                  v
             USER             Agent 2              Agent 3
                              Support              Data
                              Queue                Analyst
                                |
                                | SA
                                v
                              Agent 4
                         Solution Architect
                                |
                                v
                     Change / Feature Intake


                     AutoGen + MCP Layer
                              |
                              v
                    +-----------------------+
                    |     MCP Workbench     |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |      MCP Server       |
                    +-----------+-----------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
           Knowledge Search              Data / Metrics
                 |                             |
                 v                             v
          KOART Documentation        Excel / Dashboards
```

---

# Summary

The KOART Support System — Multi-Agent Prototype demonstrates a multi-agent support architecture where:

```text
Agent 1
Front Door / Triage
        |
        +------ Direct Knowledge Answer
        |
        +------ Agent 2
        |       Support Queue
        |           |
        |           +------ Normal Support
        |           |
        |           +------ Agent 4
        |                   Solution Architect
        |
        +------ Agent 3
                Data Analyst
```

The system combines:

- AI-powered triage
- Specialist agent routing
- KOART Knowledge Base retrieval
- Operational support guidance
- Data analysis
- Configuration/change clarification
- MCP-based tool access
- AutoGen orchestration
- FastAPI backend
- WebSocket communication
- React frontend
- Three.js 3D visualization
- Real-time handoff visualization

The prototype is intended as a foundation for further development into a production-grade intelligent KOART support platform.

https://github.com/Vivekvinu13/KOART-Support-System---Multi-Agent-Prototype
