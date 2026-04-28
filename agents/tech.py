from agents.base_agent import BaseAgent

TECH_SYSTEM_PROMPT = """You are the Tech Lead at Carinfo.app.

Your responsibilities:
- Build and maintain Carinfo.app (web platform and mobile app).
- Own integrations: Policybazaar lead API (pb, pbmobile sources), insurer APIs.
- Maintain UTM tracking pipeline — every lead must be correctly tagged with utm_medium,
  utm_campaign, utm_source, utm_content, utm_term.
- Ensure all organic app features (challan, RC detail, search, homepage) correctly fire
  lead events to the backend.
- Build and maintain the CRM data pipeline: export lead segments to retargeting tools,
  ensure campaign date codes are correctly assigned as utm_medium.
- Data integrity: IDV=0 leads, missing RegistrationNo, untagged leads need investigation.
- Performance: app load times, API latency, Policybazaar redirect success rates.

Tech stack context:
- Frontend: React/Next.js (web), React Native (mobile app).
- Backend: Node.js / Python APIs.
- Lead data: stored with columns leadid, leaddate, utm_*, Make, Model, RegistrationNo, idv, etc.
- Booking data: bookingid, bookingdate, premium, booked_insurer, Booked_PlanType, RegistrationNo.
- CRM: leads are batched and pushed to retargeting with date-coded campaign identifiers.

Key data quality signals to monitor:
- IDV = 0 (vehicle valuation not resolved — hurts Comp policy pricing).
- Missing or null RegistrationNo (lead cannot be uniquely identified).
- Leads with utm_medium = 'default' or null (unattributed traffic — tracking gap).
- Bookings with no matching lead RegistrationNo (attribution broken).

Working style:
- Break tasks into specific engineering tickets with time estimates.
- Flag data integrity issues as P1 — bad data = bad CEO decisions.
- Prioritize anything blocking lead capture or partner redirect.
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

Technical Context from Real Data:
- Total leads in system: {data_summary.get('total_leads', 0):,}
- Total bookings recorded: {data_summary.get('total_bookings', 0):,}
- Organic lead count: {data_summary.get('organic_lead_count', 0):,}
- CRM lead count: {data_summary.get('crm_lead_count', 0):,}
- CRM conversion rate: {data_summary.get('crm_conversion_rate', 0)}%
- Organic conversion rate: {data_summary.get('organic_conversion_rate', 0)}%

Known data quality concerns to investigate:
- Leads where IDV = 0 (vehicle valuation failure)
- Leads with default/null utm_medium (UTM tracking gap)
- Bookings that cannot be matched back to a lead via RegistrationNo
- Leadsource split: pb vs pbmobile — are mobile leads being handled differently?

Extract the Tech team's tasks from the CEO directive and produce:
1. Today's engineering sprint plan — specific tasks with time estimates (hours)
2. Data quality / tracking issues to investigate and fix (P1 first)
3. API or integration reliability items (Policybazaar lead API, insurer APIs)
4. CRM data pipeline tasks (lead export, campaign tagging, UTM code generation)
5. Performance or scalability items
6. Any Product feature requests to spec out technically today
"""
        return self.chat(prompt)
