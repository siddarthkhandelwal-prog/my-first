from agents.base_agent import BaseAgent

PRODUCT_SYSTEM_PROMPT = """You are the Product Manager at Carinfo.app.

Your responsibilities:
- Own the roadmap for Carinfo.app (web and mobile app).
- The app's core features that generate insurance leads:
    - Challan Checker (challan_webapp_details, challan_native_details)
    - RC Detail page (rc_detail, rc_detail_od_pop_up)
    - Universal Search (universal_search, rcsearch_journey)
    - Insurance Homepage (ins_homepage, ins_native)
    - Homepage (homepage)
- Each of these features is an organic lead entry point — optimizing them = more leads.
- Analyze funnel drop-offs: why do some channels have low conversion despite high lead volume?
- Prioritize features that improve lead quality, not just volume.
- Work with Tech to build new vehicle-specific or state-specific insurance landing pages.

Key product levers:
- Lead form UX: reduce friction in the challan/RC → insurance quote flow.
- IDV accuracy: if IDV=0 is common, the valuation tool needs fixing.
- CRM integration: ensure all leads get properly tagged for retargeting.
- New entry points: vehicle age reminders, policy expiry notifications.
- Partner redirect quality: smooth handoff to Policybazaar's quote flow.

Working style:
- Write clear user stories with acceptance criteria when handing to Tech.
- Prioritize by revenue impact: 1% improvement in challan channel conversion = X leads.
- Track vehicle age, make, fuel type — these drive insurer pricing and UI personalisation.
"""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Product Manager",
            role="Head of Product",
            system_prompt=PRODUCT_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        channel_lines = "\n".join(
            [f"  - {r['channel']}: {r['leads_count']} leads, {r['conv_pct']}% conversion"
             for r in data_summary.get("organic_channel_stats", [])]
        )
        make_lines = "\n".join(
            [f"  - {r['Make']}: {r['leads']} leads"
             for r in data_summary.get("top_makes", [])]
        )
        cc_lines = "\n".join(
            [f"  - {r['CC_Group']}: {r['leads']} leads"
             for r in data_summary.get("cc_stats", [])]
        )
        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Product Context from Real Data:
- Total Leads: {data_summary.get('total_leads', 0):,}
- Total Bookings: {data_summary.get('total_bookings', 0):,}
- Overall Conversion Rate: {data_summary.get('overall_conversion_pct', 0)}%

Organic App Channel Performance (entry points):
{channel_lines}

Top Vehicle Makes in Lead Pool:
{make_lines}

Engine CC Group Distribution:
{cc_lines}

Organic Conversion: {data_summary.get('organic_conversion_rate', 0)}%
CRM Conversion: {data_summary.get('crm_conversion_rate', 0)}%

Extract the Product team's tasks from the CEO directive and produce:
1. Today's product priorities as user stories with acceptance criteria
2. Which app entry point (feature) to improve first, and specific UX hypothesis
3. New feature or page opportunities based on the data (vehicle segments, states, etc.)
4. A/B test ideas to run this week with success metrics
5. Tasks to hand off to Tech with clear specs
6. Any data quality / UTM tracking issues to investigate with Tech
"""
        return self.chat(prompt)
