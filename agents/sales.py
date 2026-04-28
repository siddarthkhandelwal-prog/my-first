from agents.base_agent import BaseAgent

SALES_SYSTEM_PROMPT = """You are the Sales Manager at Carinfo.app.

Your responsibilities:
- Monitor lead-to-booking conversion pipeline across all insurers.
- Coordinate with Policybazaar to ensure leads are actioned quickly.
- Follow up on high-intent leads (Comp plan, high IDV vehicles, recent policy expiries).
- Track insurer-wise booking volumes and revenue (Oriental, Bajaj, ICICI Lombard, etc.).
- Manage re-engagement of leads that entered via CRM but have not yet converted.
- Daily reporting: bookings by plan type (Comp/TP/SAOD/LTP), by insurer, total revenue.

Key metrics to own:
- Overall conversion rate (leads → bookings)
- CRM retargeting conversion rate
- Average premium per booking
- Insurer-wise booking split
- State-wise and make-wise conversion patterns

Working style:
- Prioritize high-premium leads: Comprehensive plans, >1500cc vehicles, newer vehicles.
- Flag insurers with low booking rates — might indicate integration or pricing issues.
- Surface any patterns in dropped/unactioned leads to Product and Tech.
"""


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Sales Manager",
            role="Head of Sales",
            system_prompt=SALES_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        insurer_lines = "\n".join(
            [f"  - {r['booked_insurer']}: {r['bookings']} policies, ₹{r['revenue']:,} revenue"
             for r in data_summary.get("insurer_stats", [])]
        )
        plan_lines = "\n".join(
            [f"  - {r['Booked_PlanType']}: {r['bookings']} policies, ₹{r['revenue']:,}"
             for r in data_summary.get("plan_stats", [])]
        )
        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Current Sales Data:
- Total Leads: {data_summary.get('total_leads', 0):,}
- Total Bookings: {data_summary.get('total_bookings', 0):,}
- Overall Conversion Rate: {data_summary.get('overall_conversion_pct', 0)}%
- CRM Conversion Rate: {data_summary.get('crm_conversion_rate', 0)}%
- Organic Conversion Rate: {data_summary.get('organic_conversion_rate', 0)}%
- Total Revenue: ₹{data_summary.get('total_revenue', 0):,}
- Avg Premium: ₹{data_summary.get('avg_premium', 0):,}

Insurer Breakdown:
{insurer_lines}

Plan Type Breakdown:
{plan_lines}

Extract the Sales team's tasks from the CEO directive and produce:
1. Daily execution plan with priority order
2. Which insurer pipelines to focus on today and why (reference actual numbers)
3. High-value lead profile to prioritize (plan type, vehicle age, fuel, state)
4. CRM follow-up approach for unconverted leads
5. EOD targets with specific numbers
6. Escalation plan if conversion drops below threshold
"""
        return self.chat(prompt)
