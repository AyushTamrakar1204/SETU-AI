"""
OIL-Track AI - Module 2
generate_sample_reports.py: Generates realistic synthetic site reports
(Free-text site diary and Discipline Excel log).
"""

import os
import pandas as pd

def generate_reports():
    reports_dir = os.path.join("data", "daily_reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Synthetic Free-Text Site Diary
    site_diary_content = """DAILY SITE PROGRESS REPORT
Project: Duliajan Gas Compressor Expansion
Date: 2026-09-07
Prepared By: Site In-Charge (Civil & Piping)

Summary of Site Execution:
1. Civil Discipline: Rebar fixing completed for compressor foundation. Quality team did bar check.
2. Civil Discipline: Plain cement concrete (PCC) curing completed yesterday.
3. Civil Discipline: Started excavation for pipe rack sleeper foundations.
4. Piping Discipline: Structural steel delivery arrived on site. Unloading in progress.
5. Piping Discipline: Pipe rack structural steel erection work started this morning.
6. Mechanical: Compressor equipment placement postponed due to heavy rain.
"""

    txt_path = os.path.join(reports_dir, "site_diary_2026_09_07.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(site_diary_content.strip())

    # 2. Synthetic Discipline-Wise Excel Log
    excel_data = [
        {
            "Date": "2026-09-08",
            "Discipline": "Civil",
            "Work Description": "Foundation concreting for compressor unit started early shift.",
            "Reported Status": "In Progress",
            "Estimated Progress": "40%"
        },
        {
            "Date": "2026-09-09",
            "Discipline": "Civil",
            "Work Description": "Compressor foundation concreting completed by 18:00 hrs.",
            "Reported Status": "Completed",
            "Estimated Progress": "100%"
        },
        {
            "Date": "2026-09-14",
            "Discipline": "Piping",
            "Work Description": "Pipe rack erection ongoing with crane 50T.",
            "Reported Status": "In Progress",
            "Estimated Progress": "60%"
        },
        {
            "Date": "2026-09-17",
            "Discipline": "Piping",
            "Work Description": "Suction line joint fit-up and alignment completed.",
            "Reported Status": "Completed",
            "Estimated Progress": "100%"
        },
        {
            "Date": "2026-09-18",
            "Discipline": "Electrical",
            "Work Description": "Overhead cable tray installation started in compressor room.",
            "Reported Status": "Started",
            "Estimated Progress": "20%"
        }
    ]

    df_excel = pd.DataFrame(excel_data)
    xlsx_path = os.path.join(reports_dir, "discipline_daily_log.xlsx")
    df_excel.to_excel(xlsx_path, index=False, engine="openpyxl")

    print("[OK] Generated synthetic site reports:")
    print(f"     -> Text Diary: {txt_path}")
    print(f"     -> Excel Log : {xlsx_path}")

if __name__ == "__main__":
    generate_reports()