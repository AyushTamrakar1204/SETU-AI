"""
OIL-Track AI - Module 6
engine.py: Analytics engine calculating schedule variance, discipline KPIs,
and critical path delay risks for executive decision-making.
"""

import sqlite3
import pandas as pd
from datetime import datetime

DEFAULT_DB_PATH = "database/oil_track.db"

def compute_schedule_analytics(db_path=DEFAULT_DB_PATH) -> dict:
    """Computes comprehensive execution health metrics from SQLite."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM planned_activities", conn)
    conn.close()

    if df.empty:
        return {}

    # Calculate dynamic variance in days
    df["start_delay_days"] = 0
    df["finish_delay_days"] = 0
    df["health_status"] = "NOT_STARTED"

    for idx, row in df.iterrows():
        p_finish = pd.to_datetime(row["planned_finish"])
        p_start = pd.to_datetime(row["planned_start"])

        # Start variance
        if pd.notna(row["actual_start"]) and row["actual_start"]:
            a_start = pd.to_datetime(row["actual_start"])
            df.at[idx, "start_delay_days"] = int((a_start - p_start).days)

        # Finish variance
        if pd.notna(row["actual_finish"]) and row["actual_finish"]:
            a_finish = pd.to_datetime(row["actual_finish"])
            finish_diff = int((a_finish - p_finish).days)
            df.at[idx, "finish_delay_days"] = finish_diff

            if finish_diff > 0:
                df.at[idx, "health_status"] = "DELAYED"
            elif finish_diff < 0:
                df.at[idx, "health_status"] = "AHEAD"
            else:
                df.at[idx, "health_status"] = "ON_TIME"
        elif row["status"] == "IN_PROGRESS":
            df.at[idx, "health_status"] = "IN_PROGRESS"

    # 1. Macro KPIs
    total_tasks = len(df)
    completed_tasks = len(df[df["status"] == "COMPLETED"])
    in_progress_tasks = len(df[df["status"] == "IN_PROGRESS"])
    unstarted_tasks = len(df[df["status"] == "NOT_STARTED"])
    
    delayed_tasks = df[df["finish_delay_days"] > 0]
    total_delayed_count = len(delayed_tasks)
    total_delay_days = int(delayed_tasks["finish_delay_days"].sum())

    # 2. Critical Path Risk Analysis
    critical_delayed = df[
        (df["baseline_status"].isin(["CRITICAL", "MILESTONE"])) & 
        (df["finish_delay_days"] > 0)
    ]

    # 3. Discipline-Wise Performance Aggregation
    discipline_stats = df.groupby("discipline").agg(
        total_activities=("activity_id", "count"),
        completed=("status", lambda s: (s == "COMPLETED").sum()),
        delayed=("finish_delay_days", lambda d: (d > 0).sum()),
        avg_finish_delay=("finish_delay_days", lambda d: round(d[d > 0].mean() if (d > 0).any() else 0.0, 1)),
        max_finish_delay=("finish_delay_days", "max")
    ).reset_index()

    return {
        "df_processed": df,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "unstarted_tasks": unstarted_tasks,
        "delayed_count": total_delayed_count,
        "total_delay_days": total_delay_days,
        "critical_delayed_count": len(critical_delayed),
        "critical_delayed_df": critical_delayed,
        "discipline_stats": discipline_stats
    }

if __name__ == "__main__":
    analytics = compute_schedule_analytics()
    print("--- SCHEDULE HEALTH ANALYTICS ---")
    print(f"Total Tasks    : {analytics['total_tasks']}")
    print(f"Completed      : {analytics['completed_tasks']}")
    print(f"Delayed Tasks  : {analytics['delayed_count']} (Total: {analytics['total_delay_days']} days)")
    print(f"Critical Delayed: {analytics['critical_delayed_count']}")
    print("\nDiscipline Breakdown:")
    print(analytics["discipline_stats"].to_string(index=False))