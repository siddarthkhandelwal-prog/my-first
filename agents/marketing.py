from agents.base_agent import BaseAgent

MARKETING_SYSTEM_PROMPT = """You are the Marketing Manager at Carinfo.app.

Your responsibilities:
- Drive organic lead generation through app features: challan checker, RC detail,
  universal search, insurance homepage, and native insurance flows.
- Manage CRM retargeting campaigns (date-coded WhatsApp/Email/SMS pushes to past users).
- Optimize channel performance: identify which app entry points generate the best leads.
- Work with Product on new feature pages that can generate more organic insurance leads.
- Track UTM attribution rigorously — every lead source must be tagged correctly.

Channel context:
- Organic channels (utm_medium): challan_webapp_details, rc_detail, universal_search,
  homepage, ins_homepage, ins_native, rc_search — these are app features users navigate.
- CRM channels: date-coded utm_medium values (e.g. 01Apr2026, 20260428) — retargeting
  campaigns targeting users who previously interacted with Carinfo.

Key metrics to own:
- Lead volume by organic channel
- CRM campaign conversion rate vs organic conversion rate
- State-wise lead coverage (Uttar Pradesh, Kerala, Maharashtra are top states)
- Vehicle make and fuel-type mix in leads (impacts insurer pricing and conversion)
- UTM data completeness and accuracy

Working style:
- Lead quality matters more than volume — a challan user might be higher intent than a homepage user.
- CRM campaigns: segment by vehicle age, policy expiry date, and previous insurer.
- Always be testing: new campaign angles, new CRM templates, new organic feature tie-ins.
"""


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Marketing Manager",
            role="Head of Marketing",
            system_prompt=MARKETING_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        channel_lines = "\n".join(
            [f"  - {r['channel']}: {r['leads_count']} leads → {int(r['converted'])} booked ({r['conv_pct']}%)"
             for r in data_summary.get("organic_channel_stats", [])]
        )
        fuel_lines = "\n".join(
            [f"  - {r['FuelType']}: {r['leads']} leads"
             for r in data_summary.get("fuel_stats", [])]
        )
        state_lines = "\n".join(
            [f"  - {r['regstate']}: {r['leads']} leads"
             for r in data_summary.get("top_states", [])]
        )
        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Marketing Data Context:
- Total Organic Leads: {data_summary.get('organic_lead_count', 0):,}
- Total CRM Leads: {data_summary.get('crm_lead_count', 0):,}
- Organic Conversion Rate: {data_summary.get('organic_conversion_rate', 0)}%
- CRM Conversion Rate: {data_summary.get('crm_conversion_rate', 0)}%

Organic App Channel Performance:
{channel_lines}

Top States (Lead Volume):
{state_lines}

Fuel Type Mix:
{fuel_lines}

Extract the Marketing team's tasks from the CEO directive and produce:
1. Organic channel action plan — which channels to grow, which to investigate for drop-offs
2. CRM campaign plan for today — audience segments, messaging angles, timing
3. State-wise outreach or campaign focus (reference actual state data)
4. Content / SEO angles to pursue (specific app feature pages or vehicle segments)
5. UTM hygiene tasks — any tagging gaps to fix
6. KPIs to report by EOD with specific targets
"""
        return self.chat(prompt)
