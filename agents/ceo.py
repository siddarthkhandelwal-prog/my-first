import json
import pandas as pd
from tabulate import tabulate
from agents.base_agent import BaseAgent
from config import LEADS_FILE, BOOKINGS_FILE, COMPANY_CONTEXT

CEO_SYSTEM_PROMPT = """You are the CEO of Carinfo.app. Your responsibilities:
- Analyze daily lead data, booking conversions, and channel performance.
- Review organic channel metrics (SEO, content, YouTube) and CRM retargeting results.
- Assign precise, measurable daily tasks to Sales, Marketing, Product, and Tech teams.
- Think strategically: identify what's working, what's failing, and what needs urgent attention.
- Your task assignments must be grounded in the actual data provided to you.

Task Assignment Format for each department:
1. Priority Level (HIGH / MEDIUM / LOW)
2. Specific Task Description
3. Expected Outcome / KPI
4. Deadline (today / EOD / this week)
"""


class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CEO",
            role="Chief Executive Officer",
            system_prompt=CEO_SYSTEM_PROMPT,
        )
        self.leads_df = None
        self.bookings_df = None
        self.analysis_summary = {}

    def load_data(self, leads_path: str = LEADS_FILE, bookings_path: str = BOOKINGS_FILE):
        self.leads_df = pd.read_csv(leads_path)
        self.bookings_df = pd.read_csv(bookings_path)
        self._analyze()

    def _analyze(self):
        leads = self.leads_df
        bookings = self.bookings_df

        total_leads = len(leads)
        total_bookings = len(bookings)
        overall_conversion = round(total_bookings / total_leads * 100, 1) if total_leads else 0

        # Channel breakdown
        channel_stats = (
            leads.groupby("channel")
            .agg(leads_count=("lead_id", "count"))
            .reset_index()
        )
        converted_leads = leads[leads["lead_id"].isin(bookings["lead_id"])]
        channel_conv = (
            converted_leads.groupby("channel")
            .agg(converted=("lead_id", "count"))
            .reset_index()
        )
        channel_stats = channel_stats.merge(channel_conv, on="channel", how="left").fillna(0)
        channel_stats["conversion_rate"] = (
            channel_stats["converted"] / channel_stats["leads_count"] * 100
        ).round(1)

        # Partner breakdown
        partner_stats = (
            bookings.groupby("partner")
            .agg(bookings=("booking_id", "count"), revenue=("premium_amount", "sum"))
            .reset_index()
        )

        # CRM vs organic
        crm_leads = leads[leads["crm_retargeted"] == "Yes"]
        organic_leads = leads[leads["crm_retargeted"] == "No"]
        crm_converted = crm_leads[crm_leads["lead_id"].isin(bookings["lead_id"])]
        organic_converted = organic_leads[organic_leads["lead_id"].isin(bookings["lead_id"])]

        crm_rate = round(len(crm_converted) / len(crm_leads) * 100, 1) if len(crm_leads) else 0
        organic_rate = round(len(organic_converted) / len(organic_leads) * 100, 1) if len(organic_leads) else 0

        # Dropped / pending leads
        pending = leads[leads["status"] == "pending"]
        dropped = leads[leads["status"] == "dropped"]

        # Top cities
        top_cities = (
            leads.groupby("customer_city")
            .agg(leads=("lead_id", "count"))
            .sort_values("leads", ascending=False)
            .head(5)
            .reset_index()
        )

        self.analysis_summary = {
            "total_leads": total_leads,
            "total_bookings": total_bookings,
            "overall_conversion_pct": overall_conversion,
            "channel_stats": channel_stats.to_dict(orient="records"),
            "partner_stats": partner_stats.to_dict(orient="records"),
            "crm_conversion_rate": crm_rate,
            "organic_conversion_rate": organic_rate,
            "crm_lead_count": len(crm_leads),
            "organic_lead_count": len(organic_leads),
            "pending_leads": len(pending),
            "dropped_leads": len(dropped),
            "top_cities": top_cities.to_dict(orient="records"),
            "total_revenue": int(bookings["premium_amount"].sum()),
        }

    def get_analysis_text(self) -> str:
        s = self.analysis_summary
        channel_table = tabulate(
            s["channel_stats"],
            headers={"channel": "Channel", "leads_count": "Leads", "converted": "Converted", "conversion_rate": "Conv%"},
            tablefmt="grid",
        )
        partner_table = tabulate(
            s["partner_stats"],
            headers={"partner": "Partner", "bookings": "Bookings", "revenue": "Revenue (₹)"},
            tablefmt="grid",
        )
        cities_table = tabulate(
            s["top_cities"],
            headers={"customer_city": "City", "leads": "Leads"},
            tablefmt="grid",
        )

        return f"""
=== CARINFO.APP — DAILY DATA ANALYSIS ===

OVERALL METRICS:
  Total Leads      : {s['total_leads']}
  Total Bookings   : {s['total_bookings']}
  Conversion Rate  : {s['overall_conversion_pct']}%
  Total Revenue    : ₹{s['total_revenue']:,}
  Pending Leads    : {s['pending_leads']}
  Dropped Leads    : {s['dropped_leads']}

CHANNEL PERFORMANCE:
{channel_table}

PARTNER PERFORMANCE:
{partner_table}

ORGANIC vs CRM:
  Organic Leads    : {s['organic_lead_count']}  |  Conversion: {s['organic_conversion_rate']}%
  CRM Leads        : {s['crm_lead_count']}   |  Conversion: {s['crm_conversion_rate']}%

TOP CITIES BY LEADS:
{cities_table}
"""

    def assign_tasks(self) -> dict:
        analysis = self.get_analysis_text()
        prompt = f"""
Based on the following data from Carinfo.app, assign specific daily tasks to each department.
Be precise, data-driven, and actionable. Reference actual numbers from the data.

{analysis}

Now generate today's task assignments for:
1. SALES TEAM
2. MARKETING TEAM
3. PRODUCT TEAM
4. TECH TEAM

For each department, give 3-4 specific tasks with priority (HIGH/MEDIUM/LOW), description, KPI, and deadline.
Format your response as a structured report that each team lead can act on immediately.
"""
        ceo_directive = self.chat(prompt)

        return {
            "analysis": analysis,
            "directive": ceo_directive,
            "summary": self.analysis_summary,
        }
