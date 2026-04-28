import re
import pandas as pd
from tabulate import tabulate
from agents.base_agent import BaseAgent
from config import LEADS_FILE, BOOKINGS_FILE

CEO_SYSTEM_PROMPT = """You are the CEO of Carinfo.app. Your responsibilities:
- Analyze daily lead data, booking conversions, insurer performance, and channel metrics.
- Review organic app-feature channels (challan check, RC detail, homepage, search) and CRM retargeting results.
- Assign precise, measurable daily tasks to Sales, Marketing, Product, and Tech teams.
- Think strategically: identify what's working, what's failing, and what needs urgent attention.
- Your task assignments must be grounded in the actual data provided.

Context on how Carinfo.app works:
- Users land on app features (challan checker, RC detail, insurance homepage, universal search).
- This triggers a lead which is routed to Policybazaar (leadsource = pb/pbmobile).
- Policybazaar connects the user to an insurer (Oriental, Bajaj Allianz, ICICI Lombard, etc.).
- CRM campaigns re-engage past users via date-coded WhatsApp/Email/SMS pushes.
- Plan types: Comp (Comprehensive), TP (Third Party), SAOD (Stand Alone Own Damage), LTP.

Task Assignment Format for each department:
1. Priority (HIGH / MEDIUM / LOW)
2. Specific Task Description (reference actual data numbers)
3. Expected Outcome / KPI
4. Deadline (today / EOD / this week)
"""

# Regex patterns to detect CRM utm_medium values (date-coded campaigns)
_CRM_PATTERNS = [
    re.compile(r'^\d{2}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{4}$'),  # e.g. 01Apr2026
    re.compile(r'^\d{8}$'),                                                          # e.g. 20260428
]


def _is_crm(medium) -> bool:
    if pd.isna(medium):
        return False
    return any(p.match(str(medium).strip()) for p in _CRM_PATTERNS)


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
        self.leads_df = pd.read_csv(leads_path, low_memory=False)
        if bookings_path.endswith(".xlsx"):
            self.bookings_df = pd.read_excel(bookings_path)
        else:
            self.bookings_df = pd.read_csv(bookings_path, low_memory=False)
        self._analyze()

    def _analyze(self):
        leads = self.leads_df.copy()
        bookings = self.bookings_df.copy()

        # --- Join leads → bookings via RegistrationNo ---
        converted_reg = set(bookings["RegistrationNo"].dropna().str.upper().str.strip())
        leads["reg_upper"] = leads["RegistrationNo"].fillna("").str.upper().str.strip()
        leads["converted"] = leads["reg_upper"].isin(converted_reg)

        # --- Channel classification (after adding converted column) ---
        leads["is_crm"] = leads["utm_medium"].apply(_is_crm)
        organic_leads = leads[~leads["is_crm"]]
        crm_leads = leads[leads["is_crm"]]

        total_leads = len(leads)
        total_bookings = len(bookings)
        converted_leads = leads[leads["converted"]]
        overall_conv = round(len(converted_leads) / total_leads * 100, 1) if total_leads else 0

        # --- Organic channel breakdown ---
        organic_channel = (
            organic_leads.groupby("utm_medium")
            .agg(leads_count=("leadid", "count"))
            .reset_index()
            .sort_values("leads_count", ascending=False)
            .head(10)
        )
        organic_converted = organic_leads[organic_leads["converted"]]
        org_conv_by_channel = (
            organic_converted.groupby("utm_medium")
            .agg(converted=("leadid", "count"))
            .reset_index()
        )
        organic_channel = organic_channel.merge(org_conv_by_channel, on="utm_medium", how="left").fillna(0)
        organic_channel["conv_pct"] = (
            organic_channel["converted"] / organic_channel["leads_count"] * 100
        ).round(1)
        organic_channel.rename(columns={"utm_medium": "channel"}, inplace=True)

        # --- CRM overall ---
        crm_converted = crm_leads[crm_leads["converted"]]
        crm_conv_rate = round(len(crm_converted) / len(crm_leads) * 100, 1) if len(crm_leads) else 0
        org_conv_rate = round(len(organic_converted) / len(organic_leads) * 100, 1) if len(organic_leads) else 0

        # --- Insurer breakdown ---
        insurer_stats = (
            bookings.groupby("booked_insurer")
            .agg(bookings=("bookingid", "count"), revenue=("premium", "sum"))
            .reset_index()
            .sort_values("bookings", ascending=False)
            .head(10)
        )
        insurer_stats["revenue"] = insurer_stats["revenue"].astype(int)

        # --- Plan type breakdown ---
        plan_stats = (
            bookings.groupby("Booked_PlanType")
            .agg(bookings=("bookingid", "count"), revenue=("premium", "sum"))
            .reset_index()
            .sort_values("bookings", ascending=False)
        )
        plan_stats["revenue"] = plan_stats["revenue"].astype(int)

        # --- Top states ---
        top_states = (
            leads.groupby("regstate")
            .agg(leads=("leadid", "count"))
            .sort_values("leads", ascending=False)
            .head(8)
            .reset_index()
        )

        # --- Top makes ---
        top_makes = (
            leads.groupby("Make")
            .agg(leads=("leadid", "count"))
            .sort_values("leads", ascending=False)
            .head(8)
            .reset_index()
        )

        # --- Fuel type ---
        fuel_stats = (
            leads.groupby("FuelType")
            .agg(leads=("leadid", "count"))
            .sort_values("leads", ascending=False)
            .reset_index()
        )

        # --- CC group breakdown ---
        cc_stats = (
            leads.groupby("CC_Group")
            .agg(leads=("leadid", "count"))
            .sort_values("leads", ascending=False)
            .reset_index()
        )

        # --- Vehicle age distribution ---
        age_stats = (
            leads.groupby("vehicleage")
            .agg(leads=("leadid", "count"))
            .sort_values("leads", ascending=False)
            .reset_index()
        )

        # --- Total revenue ---
        total_revenue = int(bookings["premium"].sum())
        avg_premium = int(bookings["premium"].mean())

        self.analysis_summary = {
            "total_leads": total_leads,
            "total_bookings": total_bookings,
            "overall_conversion_pct": overall_conv,
            "total_revenue": total_revenue,
            "avg_premium": avg_premium,
            "organic_lead_count": len(organic_leads),
            "crm_lead_count": len(crm_leads),
            "organic_conversion_rate": org_conv_rate,
            "crm_conversion_rate": crm_conv_rate,
            "organic_channel_stats": organic_channel.to_dict(orient="records"),
            "insurer_stats": insurer_stats.to_dict(orient="records"),
            "plan_stats": plan_stats.to_dict(orient="records"),
            "top_states": top_states.to_dict(orient="records"),
            "top_makes": top_makes.to_dict(orient="records"),
            "fuel_stats": fuel_stats.to_dict(orient="records"),
            "cc_stats": cc_stats.to_dict(orient="records"),
        }

    def get_analysis_text(self) -> str:
        s = self.analysis_summary

        organic_table = tabulate(
            s["organic_channel_stats"],
            headers={"channel": "App Channel", "leads_count": "Leads", "converted": "Booked", "conv_pct": "Conv%"},
            tablefmt="grid",
            floatfmt=".1f",
        )
        insurer_table = tabulate(
            s["insurer_stats"],
            headers={"booked_insurer": "Insurer", "bookings": "Policies", "revenue": "Revenue (₹)"},
            tablefmt="grid",
        )
        plan_table = tabulate(
            s["plan_stats"],
            headers={"Booked_PlanType": "Plan Type", "bookings": "Policies", "revenue": "Revenue (₹)"},
            tablefmt="grid",
        )
        states_table = tabulate(
            s["top_states"],
            headers={"regstate": "State", "leads": "Leads"},
            tablefmt="grid",
        )
        makes_table = tabulate(
            s["top_makes"],
            headers={"Make": "Vehicle Make", "leads": "Leads"},
            tablefmt="grid",
        )
        fuel_table = tabulate(
            s["fuel_stats"],
            headers={"FuelType": "Fuel", "leads": "Leads"},
            tablefmt="grid",
        )

        return f"""
=== CARINFO.APP — DAILY DATA ANALYSIS ===

OVERALL METRICS:
  Total Leads        : {s['total_leads']:,}
  Total Bookings     : {s['total_bookings']:,}
  Conversion Rate    : {s['overall_conversion_pct']}%
  Total Revenue      : ₹{s['total_revenue']:,}
  Average Premium    : ₹{s['avg_premium']:,}

CHANNEL SPLIT (Leads):
  Organic (App)      : {s['organic_lead_count']:,} leads  |  Conversion: {s['organic_conversion_rate']}%
  CRM (Retargeting)  : {s['crm_lead_count']:,} leads  |  Conversion: {s['crm_conversion_rate']}%

ORGANIC APP CHANNEL BREAKDOWN:
{organic_table}

INSURER PERFORMANCE (Bookings):
{insurer_table}

POLICY PLAN TYPE:
{plan_table}

TOP STATES BY LEADS:
{states_table}

TOP VEHICLE MAKES:
{makes_table}

FUEL TYPE DISTRIBUTION:
{fuel_table}
"""

    def assign_tasks(self) -> dict:
        analysis = self.get_analysis_text()
        prompt = f"""
Based on the following real data from Carinfo.app, assign specific daily tasks to each department.
Be precise, reference actual numbers, and make every task actionable.

{analysis}

Generate today's task assignments for:
1. SALES TEAM — focus on conversion pipeline, insurer coordination, and pending leads.
2. MARKETING TEAM — organic channel optimization, CRM campaign strategy.
3. PRODUCT TEAM — app feature improvements, funnel optimization, new page opportunities.
4. TECH TEAM — integrations, data pipelines, performance, UTM tracking reliability.

For each department: 3-4 tasks with Priority (HIGH/MEDIUM/LOW), description, KPI, and deadline.
Reference specific numbers from the data (e.g., CRM conversion rate, top states, insurer volumes).
"""
        directive = self.chat(prompt)
        return {
            "analysis": analysis,
            "directive": directive,
            "summary": self.analysis_summary,
        }
