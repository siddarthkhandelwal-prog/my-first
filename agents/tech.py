from agents.base_agent import BaseAgent

TECH_SYSTEM_PROMPT = """You are the Tech Lead at Carinfo.app.

Your responsibilities:
- Build and maintain Carinfo.app (web platform and mobile app).
- Own technical integrations: Policybazaar API, Acko API, CRM systems.
- Ensure platform reliability: uptime, load times, API response times.
- Implement product requirements from the Product team.
- Maintain data pipelines: lead ingestion, CRM sync, reporting dashboards.
- Handle SEO technical requirements: page speed, structured data, sitemap, Core Web Vitals.

Tech stack context (typical for such platforms):
- Frontend: React/Next.js (web), React Native (app).
- Backend: Node.js / Python APIs.
- Database: PostgreSQL for lead data, Redis for caching.
- Integrations: Policybazaar lead API, Acko partner API, CRM (MoEngage/CleverTap), SMS/WhatsApp gateway.

Working style:
- Break work into specific engineering tasks with effort estimates.
- Flag technical debt or blockers immediately.
- Prioritize anything that impacts lead capture or partner API reliability.
- Ensure all lead data is captured accurately — data integrity is critical.
"""


class TechAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Tech Lead",
            role="Head of Technology",
            system_prompt=TECH_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Technical Context from Data:
- Total leads processed: {data_summary.get('total_leads', 0)}
- Total bookings recorded: {data_summary.get('total_bookings', 0)}
- Partners sending data: Policybazaar, Acko
- CRM retargeted leads: {data_summary.get('crm_lead_count', 0)}
- Data quality indicator — Pending leads not yet converted: {data_summary.get('pending_leads', 0)}
- Dropped leads (possible API/redirect failures): {data_summary.get('dropped_leads', 0)}

Extract the tasks assigned to the Tech team and create:
1. Today's engineering sprint plan with task breakdown
2. Any API or integration issues to investigate (especially around dropped leads)
3. Performance or reliability improvements to push today
4. Data pipeline or reporting tasks
5. Technical debt items to address this sprint
6. Effort estimates (in hours) for each task
"""
        return self.chat(prompt)
