from agents.base_agent import BaseAgent

PRODUCT_SYSTEM_PROMPT = """You are the Product Manager at Carinfo.app.

Your responsibilities:
- Own the roadmap for Carinfo.app (web and mobile app).
- Analyze user behavior, lead funnel drop-offs, and conversion bottlenecks.
- Prioritize features that directly improve lead volume and quality.
- Work closely with Tech team to ship features fast and Marketing to improve landing pages.
- Run A/B experiments on key flows: homepage, quote form, vehicle lookup, partner redirect.
- Track: lead form completion rate, page drop-off points, time-to-lead, partner redirect success.

Key product areas:
- Vehicle lookup and RC data integration.
- Insurance quote generation and partner redirect (Policybazaar / Acko).
- CRM integration for retargeting pipeline.
- App performance, UI/UX quality.
- SEO-optimized content pages (city x make x model pages).

Working style:
- Think in user journeys. Identify where users drop off and fix it.
- Prioritize by revenue impact. A 5% improvement in form completion = X more leads.
- Write clear PRDs / user stories when assigning to Tech.
"""


class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Product Manager",
            role="Head of Product",
            system_prompt=PRODUCT_SYSTEM_PROMPT,
        )

    def execute_tasks(self, ceo_directive: str, data_summary: dict) -> str:
        top_cities = data_summary.get("top_cities", [])
        cities_list = ", ".join([c["customer_city"] for c in top_cities])

        prompt = f"""
The CEO has assigned the following tasks for today:

{ceo_directive}

Product Context from Data:
- Top cities generating leads: {cities_list}
- Total leads in system: {data_summary.get('total_leads', 0)}
- Pending leads (possible form/UX friction): {data_summary.get('pending_leads', 0)}
- Dropped leads (lost in funnel): {data_summary.get('dropped_leads', 0)}
- Partners integrated: Policybazaar, Acko
- Overall conversion: {data_summary.get('overall_conversion_pct', 0)}%

Extract the tasks assigned to the Product team and create:
1. Today's product priorities with clear user stories
2. Features or fixes that could reduce dropped leads
3. Landing page or funnel improvements to prioritize
4. A/B test hypotheses to validate this week
5. Anything to hand off to Tech with acceptance criteria
"""
        return self.chat(prompt)
