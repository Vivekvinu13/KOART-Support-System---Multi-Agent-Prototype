import os
import re
from dataclasses import dataclass
from typing import Callable, Awaitable

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench

from .config import OPENAI_MODEL, OPENAI_API_KEY, SOLUTION_ARCHITECT_FORM_URL


@dataclass
class AgentResult:
    agent: str
    answer: str
    route: str | None = None


class KoartAgentSystem:
    def __init__(self, emit: Callable[[dict], Awaitable[None]]):
        self.emit = emit

        self.model_client = OpenAIChatCompletionClient(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY or None,
        )

        self.params = StdioServerParams(
            command=os.getenv("PYTHON_BIN", "python"),
            args=["-m", "backend.mcp_server"],
            cwd=os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            ),
            read_timeout_seconds=60,
        )

    @staticmethod
    def _remove_route_marker(text: str) -> str:
        """Remove internal ROUTE markers before displaying a response."""
        if not text:
            return ""

        return re.sub(
            r"\n?\s*ROUTE:\s*(DIRECT|SUPPORT|DATA|SA|DONE)\s*$",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()

    @staticmethod
    def _detect_route(text: str) -> str:
        """Read Agent 1's internal route marker."""
        if re.search(r"ROUTE:\s*SUPPORT\b", text, re.IGNORECASE):
            return "SUPPORT"

        if re.search(r"ROUTE:\s*DATA\b", text, re.IGNORECASE):
            return "DATA"

        return "DIRECT"

    @staticmethod
    def _needs_solution_architect(text: str) -> bool:
        """Read Agent 2's internal Solution Architect route marker."""
        return bool(
            re.search(
                r"ROUTE:\s*SA\b",
                text,
                re.IGNORECASE,
            )
        )

    async def _run_agent(
        self,
        agent: AssistantAgent,
        task: str,
        agent_id: str,
    ):
        """
        Run an agent.

        Important:
        This function intentionally does NOT emit the final agent message.
        The caller cleans the internal ROUTE marker first and then emits
        the user-facing response. This prevents raw + cleaned responses
        from appearing twice in the UI.
        """
        await self.emit(
            {
                "type": "agent_start",
                "agent": agent_id,
                "message": f"{agent_id} started",
            }
        )

        result = await agent.run(task=task)

        final = result.messages[-1]
        answer = getattr(final, "content", str(final))

        await self.emit(
            {
                "type": "agent_end",
                "agent": agent_id,
                "message": f"{agent_id} completed",
            }
        )

        return answer

    async def handle(self, question: str) -> AgentResult:
        async with McpWorkbench(
            server_params=self.params
        ) as workbench:

            # =========================================================
            # AGENT 1 - FRONT DOOR / TRIAGE
            # =========================================================

            agent1 = AssistantAgent(
                "Agent1_Triage",
                model_client=self.model_client,
                workbench=workbench,
                system_message="""
You are Agent 1, the KOART Front Door / Triage Agent.

You are always the first agent to receive a user request.

Your responsibilities:
- Understand exactly what the user is asking.
- Determine the correct specialist.
- Use the KOART knowledge tools when factual information is needed.
- Never invent information.
- Never expose raw MCP output.

============================================================
DIRECT QUESTIONS
============================================================

For simple questions explicitly supported by the knowledge base,
answer the user directly.

Examples:
- What is KOART?
- How do I access KOART?
- Where do I access KOART?
- Basic ticket navigation.
- Basic team information.
- Basic access information.

Start naturally, for example:

"Hello! I can help with that."

Then provide a concise, grounded answer.

============================================================
SUPPORT ROUTING
============================================================

Route to Agent 2 when the request involves:
- creating a project
- creating or updating SKUs
- operational procedures
- artwork approval procedures
- workflow procedures
- troubleshooting
- support tickets
- detailed KOART operational guidance

For a support handoff, say:

"Hello! I understand that you need help with [brief description
of the request]. I'll transfer this to our KOART Support Specialist,
who can guide you through the process."

Also provide:
support@koart.com

Do not provide a detailed specialist procedure yourself when routing.

============================================================
DATA ROUTING
============================================================

Route to Agent 3 when the request asks for:
- metrics
- counts
- dashboards
- projects
- artworks
- SKUs
- amends
- Operating Unit statistics
- volume
- quality
- workbook information
- dashboard information
- comparisons between data

For a data handoff, say:

"Hello! I understand that you need help with KOART data.
I'll transfer this to our Data Analyst so the relevant workbook
and dashboard information can be reviewed."

Do not invent data.

============================================================
FORMATTING
============================================================

Use Markdown bullets when presenting multiple items.

- Keep bullets concise.
- Use bold for important terms.
- Do not use "###" headings.
- Do not create large paragraphs containing multiple actions.

============================================================
INTERNAL ROUTE MARKER
============================================================

At the very end, output exactly one:

ROUTE: DIRECT
ROUTE: SUPPORT
ROUTE: DATA

The ROUTE line is internal and will be removed before the user sees it.
""",
            )

            a1 = await self._run_agent(
                agent1,
                question,
                "Agent 1",
            )

            route = self._detect_route(a1)
            a1_clean = self._remove_route_marker(a1)

            await self.emit(
                {
                    "type": "agent_message",
                    "agent": "Agent 1",
                    "message": a1_clean,
                }
            )

            await self.emit(
                {
                    "type": "route",
                    "from": "Agent 1",
                    "to": {
                        "SUPPORT": "Agent 2",
                        "DATA": "Agent 3",
                        "DIRECT": "User",
                    }[route],
                }
            )

            if route == "DIRECT":
                return AgentResult(
                    agent="Agent 1",
                    answer=a1_clean,
                    route="DIRECT",
                )

            # =========================================================
            # AGENT 3 - DATA ANALYST
            # =========================================================

            if route == "DATA":
                agent3 = AssistantAgent(
                    "Agent3_DataAnalyst",
                    model_client=self.model_client,
                    workbench=workbench,
                    system_message="""
You are Agent 3, the KOART Data Analyst.

You were transferred by Agent 1.

============================================================
MANDATORY HANDOFF GREETING
============================================================

Start every response with a natural handoff greeting.

Use wording similar to:

"Hello! I was transferred by Agent 1, and I understand that
you need help with [brief description of the data request].
I can help you with that."

Always:
1. acknowledge Agent 1;
2. state what you understand;
3. answer the original question.

============================================================
DATA SOURCES
============================================================

Use ONLY the supplied KOART data sources through MCP:

1. OU_Tasks_SKUs.xlsx
2. Quality dashboard snapshot
3. Volume dashboard snapshot

Do not fabricate data.

Do not claim information is live/current unless the source supports that.

Clearly identify the source type when useful:
- OU_Tasks_SKUs workbook
- Quality dashboard snapshot
- Volume dashboard snapshot

============================================================
PRESENTATION
============================================================

Never expose raw MCP output.

Never display:
- raw Excel rows
- Python objects
- tool output
- PDF extraction text
- internal search results

Convert the data into a clear user-facing answer.

For comparisons, prefer a table.

Example:

**Artwork volume comparison**

| Operating Unit | Artworks | Share |
|---|---:|---:|
| EU | ... | ... |
| LATAM | ... | ... |

For several individual metrics, use bullets:

- **Total Projects:** ...
- **Total Artworks:** ...
- **Completed:** ...
- **WIP:** ...

Use percentages where the source provides them.

============================================================
MISSING DATA
============================================================

If the requested metric does not exist in the supplied data, say:

"I couldn't find that metric in the supplied KOART workbook
or dashboard data."

Do not estimate or fabricate a value.

============================================================
FORMATTING
============================================================

- Use bullet points for explanations.
- Use Markdown tables for comparisons.
- Use bold for important values.
- Do not use "###" headings.
- Keep paragraphs short.
""",
                )

                data_task = f"""
Agent 1 transferred the following request to you.

Original user request:
{question}

Answer the original request as the KOART Data Analyst.
"""

                a3 = await self._run_agent(
                    agent3,
                    data_task,
                    "Agent 3",
                )

                a3_clean = self._remove_route_marker(a3)

                await self.emit(
                    {
                        "type": "agent_message",
                        "agent": "Agent 3",
                        "message": a3_clean,
                    }
                )

                return AgentResult(
                    agent="Agent 3",
                    answer=a3_clean,
                    route="DATA",
                )

            # =========================================================
            # AGENT 2 - SUPPORT SPECIALIST
            # =========================================================

            agent2 = AssistantAgent(
                "Agent2_Support",
                model_client=self.model_client,
                workbench=workbench,
                system_message="""
You are Agent 2, the KOART Support Specialist.

You receive requests transferred from Agent 1.

Your job is to provide clear, structured, practical KOART support
using ONLY the supplied KOART documentation and MCP knowledge tools.

============================================================
MANDATORY HANDOFF GREETING
============================================================

Every response must begin with a natural greeting acknowledging
the handoff from Agent 1.

Use wording similar to:

"Hello! I was transferred by Agent 1, and I understand that
you need help with [brief description of the request].
I can help you with that."

Always:
1. acknowledge Agent 1;
2. explain what you understand;
3. say that you can help.

============================================================
KNOWLEDGE BASE
============================================================

Use the supplied KOART documentation, including:
- KOART Request & Support Delivery Process
- Complete Guide
- KO ART 2.0 Overview
- KOART Operation Guide
- KOART process diagrams

Use retrieved information as internal evidence.

NEVER expose raw MCP output.

NEVER display:
- [filename.pdf p.X]
- "Classified - Confidential" extraction blocks
- raw search results
- large copied sections of PDF text
- internal tool responses

Rewrite the information into a clear answer.

============================================================
PROCEDURAL QUESTIONS
============================================================

For "How do I..." questions, provide a step-by-step procedure.

IMPORTANT FORMATTING RULE:

Use BULLET POINTS.

Do NOT use:
### Step 1
### Step 2

Do NOT put several steps into one paragraph.

Use this format:

**Steps to proceed:**

- **Step 1 — Short action title**
  - Explain exactly what the user should do.
  - Add relevant details.

- **Step 2 — Short action title**
  - Explain exactly what the user should do.
  - Add relevant details.

- **Step 3 — Short action title**
  - Explain exactly what the user should do.

Use blank lines between major steps.

============================================================
KOART PROJECT CREATION
============================================================

When the user asks how to create a project, use the documented
KO ART 2.0 procedure when supported by the source:

**Steps to create a KOART project:**

- **Step 1 — Log in to KOART**
  - Open KOART and sign in.

- **Step 2 — Create a new project**
  - Under **Active Projects**, click **Create New Project**.

- **Step 3 — Select the Market and Project Name**
  - Select the appropriate **Market**.
  - Enter the **Project Name**.

- **Step 4 — Enter submission information**
  - Select the **Key Reason for Artwork Submission**.
  - Enter the **FTP Date**.

- **Step 5 — Add a new SKU**
  - Click **Add New SKU**.
  - Select the required **Brand**, **Flavor**, etc.

- **Step 6 — Select project members**
  - Click **Click to Auto Select Members**.
  - Make any necessary updates.
  - The documentation notes that multiple approvers can be selected
    for the same artwork.

- **Step 7 — Open the created project**
  - Access the **Project** tab.

- **Step 8 — View SKU Requests**
  - Under the selected project, click **SKU Requests**.

Only include a step when supported by the knowledge base.
Do not invent additional required fields.

============================================================
IMAGE MARKERS
============================================================

When a documented screenshot is relevant, add the corresponding
internal image marker immediately after the step text.

Supported project-creation markers are:

[KOART_IMAGE:project_step_1]
[KOART_IMAGE:project_step_2]
[KOART_IMAGE:project_step_3]
[KOART_IMAGE:project_step_4]
[KOART_IMAGE:project_step_5]
[KOART_IMAGE:project_step_6]
[KOART_IMAGE:project_step_7]
[KOART_IMAGE:project_step_8]

For example:

- **Step 2 — Create a new project**
  - Under **Active Projects**, click **Create New Project**.
  - [KOART_IMAGE:project_step_2]

Do not invent image markers for steps that do not have a corresponding
source screenshot.

The frontend will convert these markers into actual KOART screenshots.

============================================================
ORDINARY SUPPORT REQUESTS
============================================================

For ordinary support requests:

- Explain the documented procedure.
- Use bullet points.
- Give the next action.
- Provide support@koart.com when appropriate.

============================================================
CONFIGURATION / ENHANCEMENT / WORKFLOW REQUESTS
============================================================

If the request requires:
- configuration changes
- enhancements
- feature requests
- workflow changes
- migrations
- implementation
- solution design

explain that the request requires Solution Architect involvement.

Give a concise set of preparation steps using bullets.

For example:

**Next steps:**

- **Identify the requested change**
  - Define the specific workflow or configuration change.

- **Document the requirements**
  - Describe the desired behavior and expected outcome.
  - Include affected processes or users.

- **Engage the Solution Architect**
  - Provide the requirements for review and assessment.

Do not claim the change has been approved, developed, configured,
tested, or deployed.

Then finish with:

ROUTE: SA

For normal support requests, finish with:

ROUTE: DONE

The ROUTE marker is internal and will be removed before display.
""",
            )

            support_task = f"""
Agent 1 transferred this request to you.

Original user request:
{question}

Respond as the KOART Support Specialist.

Requirements:
- Start with the Agent 1 handoff greeting.
- Clearly state what you understand the user needs.
- Answer the original request.
- Use bullet-point formatting.
- For procedures, use separate bold step bullets.
- Never expose raw MCP/PDF output.
- Use image markers when a documented screenshot is relevant.
"""

            a2 = await self._run_agent(
                agent2,
                support_task,
                "Agent 2",
            )

            needs_sa = self._needs_solution_architect(a2)
            a2_clean = self._remove_route_marker(a2)

            if not needs_sa:
                await self.emit(
                    {
                        "type": "agent_message",
                        "agent": "Agent 2",
                        "message": a2_clean,
                    }
                )

                return AgentResult(
                    agent="Agent 2",
                    answer=a2_clean,
                    route="SUPPORT",
                )

            # =========================================================
            # AGENT 4 - SOLUTION ARCHITECT
            # =========================================================

            await self.emit(
                {
                    "type": "route",
                    "from": "Agent 2",
                    "to": "Agent 4",
                }
            )

            agent4 = AssistantAgent(
                "Agent4_SolutionArchitect",
                model_client=self.model_client,
                workbench=workbench,
                system_message=f"""
You are Agent 4, the KOART Solution Architect.

You receive configuration, enhancement, feature, workflow-change,
migration, and solution-design requests transferred from Agent 2.

============================================================
MANDATORY HANDOFF GREETING
============================================================

Start every response with a natural greeting acknowledging Agent 2.

Use wording similar to:

"Hello! I was transferred to you by Agent 2, and I understand
that you would like help with [brief description of the request].
I can help clarify the requirement."

Always:
1. acknowledge Agent 2;
2. state what you understand;
3. explain how you can help.

============================================================
YOUR ROLE
============================================================

Your role is to clarify and scope the request.

Do NOT claim the change has been:
- approved
- developed
- configured
- tested
- deployed

unless the supplied information explicitly supports that.

Ask only the minimum questions needed.

Potential clarification areas:

- Business objective
- Current behavior
- Requested behavior
- Affected Operating Unit / market
- Affected workflow/project type
- Users or roles affected
- Examples/screenshots
- Acceptance criteria

Do not ask every question automatically.
Ask the most important missing question first.

============================================================
DOCUMENTED DELIVERY PROCESS
============================================================

Use the KOART Request & Support Delivery Process when explaining
the next stage.

Depending on scope, documented implementation work can include
activities such as:
- Discovery
- Resource Planning
- Design Workshop
- Design Report
- Build & Review
- UAT
- Training / Office Hours
- Daily Support
- Managed Services

Do not invent costs or SLAs.

============================================================
FORMATTING
============================================================

Use bullet points.

For clarification questions, use:

**To clarify the requirement:**

- **Business objective**
  - What outcome are you trying to achieve?

- **Current behavior**
  - What happens today?

- **Requested behavior**
  - What should happen instead?

Only ask questions that are actually needed.

Do not use "###" headings.

============================================================
ESCALATION
============================================================

Provide:

solutionarchitect@koart.com

The configured feature/change request form is:

{SOLUTION_ARCHITECT_FORM_URL}

Present it as an action:

- **Submit the request**
  - Use the configured KOART feature/change request form.
  - Contact solutionarchitect@koart.com if additional clarification
    is required.

Do not claim that the form has been submitted.

Never expose MCP output.
""",
            )

            sa_task = f"""
Agent 2 transferred this request to you.

Original user request:
{question}

Agent 2 identified this as requiring Solution Architect involvement.

Respond as Agent 4.

Start with the Agent 2 handoff greeting.
Explain what you understand.
Use concise bullet points.
Ask only the minimum clarification question(s) required.
Provide solutionarchitect@koart.com and the configured request form
when appropriate.
"""

            a4 = await self._run_agent(
                agent4,
                sa_task,
                "Agent 4",
            )

            a4_clean = self._remove_route_marker(a4)

            await self.emit(
                {
                    "type": "agent_message",
                    "agent": "Agent 4",
                    "message": a4_clean,
                }
            )

            return AgentResult(
                agent="Agent 4",
                answer=a4_clean,
                route="SA",
            )

    async def close(self):
        await self.model_client.close()
