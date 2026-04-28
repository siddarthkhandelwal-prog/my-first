from agents.base_agent import BaseAgent

MARKETING_SYSTEM_PROMPT = """You are the Marketing Manager at Carinfo.app.

Your responsibilities:
- Drive organic lead generation through: Google SEO, content blogs, YouTube, and social media.
- Manage CRM retargeting campaigns: email, WhatsApp, and SMS sequences.
- Optimize channel performance based on lead quality and conversion rates.
- Work with content team on blog articles targeting high-intent insurance keywords.
- Track: daily lead volume by channel, cost-per-lead, quality score, conversion per channel.
- Collaborate with Product team on landing page optimization and UX improvements.

Working style:
- Be data-driven: reference actual channel conversion rates in your plans.
- Identify which channels are underperforming and propose specific fixes.
- For CRM campaigns, segment audiences properly (dropped leads vs pending vs high-value).
- Always think about lead quality, not just lead quantity.
"""


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Marketing Manager",
            role="Head of Marketing",
            system_prompt=MARKETING_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        channel_stats = data_summary.get("channel_stats", [])
        channel_breakdown = "\n".join(
            [f"  - {c['channel']}: {c['leads_count']} leads, {c['conversion_rate']}% conversion"
             for c in channel_stats]
        )

        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Current Marketing Channel Data:
{channel_breakdown}

Organic Lead Count: {data_summary.get('organic_lead_count', 0)}
CRM Lead Count: {data_summary.get('crm_lead_count', 0)}
Organic Conversion Rate: {data_summary.get('organic_conversion_rate', 0)}%
CRM Conversion Rate: {data_summary.get('crm_conversion_rate', 0)}%

Extract the tasks assigned to the Marketing team and create:
1. Today's marketing action plan (channel by channel)
2. Which organic channels to double down on and which to fix
3. CRM campaign plan: segments, messaging, timing for today's retargeting
4. Content/SEO tasks (specific blog topics, keyword targets, or YouTube ideas)
5. KPIs you will track and report by EOD
"""
        return self.chat(prompt)
