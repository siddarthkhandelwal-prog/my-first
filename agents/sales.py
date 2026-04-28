from agents.base_agent import BaseAgent

SALES_SYSTEM_PROMPT = """You are the Sales Manager at Carinfo.app.

Your responsibilities:
- Follow up on pending and dropped leads to recover conversions.
- Coordinate with partners (Policybazaar, Acko) to ensure smooth policy issuance.
- Track daily conversion metrics: leads received vs policies issued.
- Manage CRM retargeting pipeline: identify high-intent users for re-engagement.
- Report daily: leads converted, revenue generated, pending count, partner-wise split.

Working style:
- Always respond with a structured daily work plan.
- Prioritize high-premium leads (Comprehensive policies, premium vehicles).
- Flag any conversion blockers immediately to the CEO.
- Focus on both Policybazaar and Acko pipelines equally.
"""


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Sales Manager",
            role="Head of Sales",
            system_prompt=SALES_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Current Sales Data Context:
- Total Pending Leads: {data_summary.get('pending_leads', 0)}
- Total Dropped Leads: {data_summary.get('dropped_leads', 0)}
- Overall Conversion Rate: {data_summary.get('overall_conversion_pct', 0)}%
- CRM Conversion Rate: {data_summary.get('crm_conversion_rate', 0)}%
- Organic Conversion Rate: {data_summary.get('organic_conversion_rate', 0)}%
- Total Revenue Generated: ₹{data_summary.get('total_revenue', 0):,}

Extract the tasks assigned specifically to the Sales team and create:
1. Your detailed daily execution plan (hour-by-hour or priority-by-priority)
2. Which pending leads to prioritize first and why
3. Specific outreach scripts / talking points for different lead types
4. EOD targets you will hit
5. What you will escalate to CEO if not resolved
"""
        return self.chat(prompt)
