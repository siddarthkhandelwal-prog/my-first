#!/usr/bin/env python3
"""
Carinfo.app Daily AI Operations System
CEO assigns tasks to Sales, Marketing, Product, and Tech based on live data.
"""

import os
import sys
from datetime import date
from agents import CEOAgent, SalesAgent, MarketingAgent, ProductAgent, TechAgent
from config import REPORTS_DIR, LEADS_FILE, BOOKINGS_FILE

SEPARATOR = "=" * 70


def print_section(title: str, content: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)
    print(content)


def save_report(report_content: str, report_date: str):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, f"daily_report_{report_date}.txt")
    with open(path, "w") as f:
        f.write(report_content)
    print(f"\nReport saved to: {path}")
    return path


def run_daily_operations(leads_path: str = LEADS_FILE, bookings_path: str = BOOKINGS_FILE):
    today = date.today().strftime("%Y-%m-%d")
    print(f"\nCarinfo.app Daily Operations — {today}")
    print(SEPARATOR)

    # --- CEO: Load data and assign tasks ---
    print("\n[CEO] Loading leads and bookings data...")
    ceo = CEOAgent()
    ceo.load_data(leads_path, bookings_path)
    analysis_text = ceo.get_analysis_text()
    print(analysis_text)

    print("\n[CEO] Analyzing data and generating department task assignments...")
    result = ceo.assign_tasks()
    ceo_directive = result["directive"]
    data_summary = result["summary"]

    print_section("CEO DAILY DIRECTIVE", ceo_directive)

    full_report = f"CARINFO.APP DAILY OPERATIONS REPORT — {today}\n\n"
    full_report += analysis_text + "\n\n"
    full_report += f"{'=' * 70}\nCEO DAILY DIRECTIVE\n{'=' * 70}\n{ceo_directive}\n\n"

    # --- Sales Agent ---
    print(f"\n[Sales] Processing tasks and building execution plan...")
    sales = SalesAgent()
    sales_plan = sales.execute_tasks(ceo_directive, data_summary)
    print_section("SALES TEAM — DAILY EXECUTION PLAN", sales_plan)
    full_report += f"{'=' * 70}\nSALES TEAM — DAILY EXECUTION PLAN\n{'=' * 70}\n{sales_plan}\n\n"

    # --- Marketing Agent ---
    print(f"\n[Marketing] Processing tasks and building action plan...")
    marketing = MarketingAgent()
    marketing_plan = marketing.execute_tasks(ceo_directive, data_summary)
    print_section("MARKETING TEAM — DAILY ACTION PLAN", marketing_plan)
    full_report += f"{'=' * 70}\nMARKETING TEAM — DAILY ACTION PLAN\n{'=' * 70}\n{marketing_plan}\n\n"

    # --- Product Agent ---
    print(f"\n[Product] Processing tasks and building product priorities...")
    product = ProductAgent()
    product_plan = product.execute_tasks(ceo_directive, data_summary)
    print_section("PRODUCT TEAM — DAILY PRIORITIES", product_plan)
    full_report += f"{'=' * 70}\nPRODUCT TEAM — DAILY PRIORITIES\n{'=' * 70}\n{product_plan}\n\n"

    # --- Tech Agent ---
    print(f"\n[Tech] Processing tasks and building engineering sprint...")
    tech = TechAgent()
    tech_plan = tech.execute_tasks(ceo_directive, data_summary)
    print_section("TECH TEAM — ENGINEERING SPRINT PLAN", tech_plan)
    full_report += f"{'=' * 70}\nTECH TEAM — ENGINEERING SPRINT PLAN\n{'=' * 70}\n{tech_plan}\n\n"

    # Save full report
    save_report(full_report, today)

    print(f"\n{SEPARATOR}")
    print("  Daily operations complete. All teams have their assignments.")
    print(SEPARATOR)


if __name__ == "__main__":
    leads_path = sys.argv[1] if len(sys.argv) > 1 else LEADS_FILE
    bookings_path = sys.argv[2] if len(sys.argv) > 2 else BOOKINGS_FILE
    run_daily_operations(leads_path, bookings_path)
