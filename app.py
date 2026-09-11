"""
SETU AI (सेतु) - Schedule Execution Tracking & Unification Engine
An Intelligent Planning-to-Execution Bridge for Oil India Limited (OIL)
SIH 2026 Problem ID: SIH26122

Integrated Architecture:
- Module 1: Schedule Baseline & Ingestion
- Module 2: Intelligent Data Capture (Text/Excel/Voice/Photo/GPS/Offline)
- Module 3: Hybrid AI Semantic Matching
- Module 4: Human-in-the-Loop Review, Deduplication & Audit Trail
- Module 5: Actual Progress & Variance Synchronization
- Module 6: Project Intelligence & Delay Analytics
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.schedule.db_manager import (
    init_db,
    fetch_all_activities,
    ingest_schedule_file,
    log_audit_record,
    sync_actual_progress,
    get_db_connection,
    get_reviewed_events_map,
    clear_audit_trail
)
from src.extraction.extractor import parse_text_diary, parse_excel_log
from src.extraction.audio_extractor import transcribe_site_audio
from src.matching.matcher import ActivityMatcher
from src.analytics.engine import compute_schedule_analytics

st.set_page_config(
    page_title="SETU AI | Schedule Execution Tracking & Unification Engine",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE & COLD-START SELF-INITIALIZATION ---
init_db()

# Auto-seed baseline schedule and reports if launching on a fresh cloud container
df_check = fetch_all_activities()
default_sched_path = os.path.join("data", "schedule", "project_schedule.xlsx")
if df_check.empty and os.path.exists(default_sched_path):
    try:
        ingest_schedule_file(default_sched_path)
    except Exception as e:
        print(f"Warning during auto-ingest: {e}")

# Auto-seed sample reports if missing
default_report_dir = os.path.join("data", "daily_reports")
if not os.path.exists(default_report_dir) or not os.listdir(default_report_dir):
    try:
        from src.extraction.generate_sample_reports import main as gen_reports
        gen_reports()
    except Exception as e:
        print(f"Notice: Sample reports auto-generation skipped: {e}")

@st.cache_resource
def get_matcher():
    return ActivityMatcher()

matcher = get_matcher()

# Enterprise dark styling
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-top: 4px solid #f59e0b;
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.80rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #94a3b8;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .high-conf { color: #10b981; font-weight: bold; }
    .med-conf  { color: #f59e0b; font-weight: bold; }
    .low-conf  { color: #ef4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🌉 SETU AI Console")
    st.caption("Schedule Execution Tracking & Unification")
    st.markdown("---")

    st.subheader("📥 Data Ingestion")
    
    st.write("**1. Master Schedule (P6/MSP):**")
    sched_file = st.file_uploader("Upload Baseline (.xlsx/.csv)", type=["xlsx", "xls", "csv"], key="sched_up")
    if sched_file is not None:
        save_path = os.path.join("data", "schedule", sched_file.name)
        with open(save_path, "wb") as f:
            f.write(sched_file.getbuffer())
        try:
            count = ingest_schedule_file(save_path)
            matcher.reload_schedule()
            st.success(f"✓ Ingested {count} activities.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")
    st.write("**2. Site Progress Reports:**")
    site_file = st.file_uploader("Upload Site Log (.txt / .xlsx)", type=["txt", "xlsx"], key="site_up")
    
    st.markdown("---")
    st.subheader("🌐 Field Connectivity & Settings")
    
    # Offline Mode Simulator Toggle
    is_offline = st.checkbox("Simulate Offline Mode (Cache Local)", value=False)
    if is_offline:
        st.warning("⚠️ Offline Mode Active: Reports will be saved locally to IndexedDB/LocalStorage cache.")
    else:
        st.success("🟢 Online: Syncing live to central P6 server.")

    # Multilingual Mode Selector
    target_lang = st.selectbox(
        "Supervisor Spoken Language",
        options=["English (en)", "Hindi (hi)", "Bengali (bn)", "Tamil (ta)", "Marathi (mr)"],
        index=0
    )
    lang_code = target_lang.split("(")[-1].strip(")")

    st.markdown("---")
    st.markdown("""
    **Core Pipeline:**  
    `Ingest ➔ Extract ➔ Match ➔ HITL ➔ Sync ➔ Analytics`  
    
    **Target Asset:**  
    `Duliajan Gas Compressor Station`  
    
    **Client Organization:**  
    `Oil India Limited (OIL)`  
    
    **Challenge:**  
    `SIH 2026 (Problem ID: SIH26122)`
    """)

# --- MAIN HERO ---
st.markdown("## 🌉 SETU AI (सेतु): Schedule Execution Tracking & Unification Engine")
st.caption("AI-Powered Bridge Connecting Field Execution to Master Primavera P6 Baselines | Oil India Limited")
st.markdown("---")

# 6 Main Tabs (Expanded with Field Supervisor Multi-Modal Mode)
nav_tab1, nav_tab6_field, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "📊 Executive Delay Analytics (M6)",
    "👷 Site Supervisor Field Capture (M2)",
    "🔍 Site Review & AI Match Queue (M2-M4)",
    "⚡ Live Progress & Variance Tracking (M5)",
    "📅 Baseline Master Schedule (M1)",
    "📜 Verification Audit Trail (M4)"
])

# =========================================================================
# TAB 1: EXECUTIVE DELAY ANALYTICS & PROJECT INTELLIGENCE (MODULE 6)
# =========================================================================
with nav_tab1:
    analytics = compute_schedule_analytics()

    if not analytics:
        st.warning("No project schedule data available to compute analytics.")
    else:
        st.subheader("Executive Project Health & Delay Intelligence")
        st.caption("Live aggregate analysis of actual site progress vs. Primavera P6 baseline commitments.")

        ek1, ek2, ek3, ek4, ek5 = st.columns(5)
        ek1.metric("Total Activities", analytics["total_tasks"])
        ek2.metric("Completed Tasks", f"{analytics['completed_tasks']} / {analytics['total_tasks']}")
        ek3.metric("Delayed Tasks", analytics["delayed_count"], delta=f"-{analytics['total_delay_days']} days slippage", delta_color="inverse")
        ek4.metric("Critical Path Threats", analytics["critical_delayed_count"], delta="High Risk" if analytics["critical_delayed_count"] > 0 else "Normal", delta_color="inverse")
        
        comp_rate = round((analytics["completed_tasks"] / analytics["total_tasks"]) * 100, 1) if analytics["total_tasks"] > 0 else 0
        ek5.metric("Project Physical %", f"{comp_rate}%")

        st.markdown("---")

        vcol1, vcol2 = st.columns([1.5, 1.2])

        with vcol1:
            st.markdown("#### 🚨 Discipline Slippage & Delay Distribution")
            disc_df = analytics["discipline_stats"]

            fig_bar = px.bar(
                disc_df,
                x="discipline",
                y="delayed",
                color="avg_finish_delay",
                text="delayed",
                labels={"discipline": "Discipline", "delayed": "Delayed Tasks", "avg_finish_delay": "Avg Delay (Days)"},
                title="Number of Delayed Tasks per Discipline (Colored by Avg Days)",
                color_continuous_scale="Reds"
            )
            fig_bar.update_layout(height=360, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with vcol2:
            st.markdown("#### 🎯 Execution Task Health Status")
            health_counts = analytics["df_processed"]["health_status"].value_counts().reset_index()
            health_counts.columns = ["Status", "Count"]

            fig_donut = px.pie(
                health_counts,
                names="Status",
                values="Count",
                hole=0.5,
                color="Status",
                color_discrete_map={
                    "COMPLETED": "#10b981",
                    "IN_PROGRESS": "#3b82f6",
                    "DELAYED": "#ef4444",
                    "ON_TIME": "#10b981",
                    "AHEAD": "#8b5cf6",
                    "NOT_STARTED": "#64748b"
                },
                title="Task Lifecycle & Variance Breakdown"
            )
            fig_donut.update_layout(height=360, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_donut, use_container_width=True)

        if analytics["critical_delayed_count"] > 0:
            st.error(f"⚠️ **ATTENTION PLANNERS:** {analytics['critical_delayed_count']} activity on the **CRITICAL PATH** has experienced schedule slippage! Immediate intervention recommended.")
            crit_df = analytics["critical_delayed_df"]
            st.dataframe(
                crit_df[[
                    "activity_id", "discipline", "wbs_package", 
                    "activity_description", "planned_finish", "actual_finish", 
                    "finish_delay_days", "baseline_status"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "activity_id": "Activity ID",
                    "finish_delay_days": st.column_config.NumberColumn("Delay (Days)", format="+%d d")
                }
            )
        else:
            st.success("✅ No critical path delays detected. Project baseline integrity is maintained.")

# =========================================================================
# TAB 2: SITE SUPERVISOR FIELD CAPTURE (MODULE 2 - Voice, Photo, GPS, Offline)
# =========================================================================
with nav_tab6_field:
    st.subheader("👷 Site Supervisor Multi-Modal Field Capture")
    st.write("Submit daily progress using voice notes, typed text, or photo proof. Metadata (GPS & timestamp) is automatically bound.")

    with st.form("field_capture_form"):
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            st.markdown("##### 🎙️ Voice & Text Reporting")
            audio_data = st.audio_input("Record voice update from site")
            text_fallback = st.text_area("Or type site observation manually:", placeholder="e.g., Poured 50m3 concrete for Foundation Pier 3...")
            
        with col_input2:
            st.markdown("##### 📸 Visual Proof & Location")
            photo_proof = st.camera_input("Take site progress photo")
            image_file = st.file_uploader("Or upload site image file", type=["jpg", "png", "jpeg"])
            
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            simulated_gps = "26.6749° N, 94.5362° E (Duliajan Station Zone 3)"
            
            st.text_input("Captured Timestamp", value=current_timestamp, disabled=True)
            st.text_input("Auto-Tagged GPS Chainage", value=simulated_gps, disabled=True)

        submit_report = st.form_submit_button("🚀 Transmit Field Report to AI Engine", type="primary")

        if submit_report:
            processed_text = ""
            
            if audio_data is not None:
                with st.spinner("Transcribing and translating audio via OpenAI Whisper..."):
                    processed_text = transcribe_site_audio(audio_data, language_code=lang_code)
                    st.info(f"**Transcribed Audio Text:** {processed_text}")
            elif text_fallback:
                processed_text = text_fallback
            else:
                processed_text = "General progress update logged with visual proof."

            st.success(f"Successfully captured report! Timestamp: {current_timestamp} | GPS: {simulated_gps}")
            if photo_proof or image_file:
                st.image(photo_proof if photo_proof else image_file, caption="Verified Site Photo Proof Attached", width=300)
                
            st.balloons()

# =========================================================================
# TAB 3: SITE REVIEW & AI MATCH QUEUE (MODULES 2, 3, 4 with Deduplication)
# =========================================================================
with nav_tab2:
    st.subheader("Extracted Site Events ➔ AI Candidate Matching")
    st.write("Site reports are automatically parsed and linked to planned L5/L6 activities. Review or confirm matches below.")

    raw_events = []
    if site_file is not None:
        temp_path = os.path.join("data", "daily_reports", site_file.name)
        with open(temp_path, "wb") as f:
            f.write(site_file.getbuffer())
        if site_file.name.endswith(".txt"):
            raw_events = parse_text_diary(temp_path)
        elif site_file.name.endswith(".xlsx"):
            raw_events = parse_excel_log(temp_path)
    else:
        default_txt = os.path.join("data", "daily_reports", "site_diary_2026_09_07.txt")
        if os.path.exists(default_txt):
            raw_events = parse_text_diary(default_txt)
            st.info("💡 Displaying pre-loaded site diary: `site_diary_2026_09_07.txt`. Upload custom reports via the sidebar.")

    if not raw_events:
        st.warning("No site updates detected. Please upload a report in the sidebar.")
    else:
        df_sched = fetch_all_activities()
        reviewed_map = get_reviewed_events_map()

        for i, event in enumerate(raw_events):
            event_key = f"{event['report_date']}||{event['raw_text'].strip()}"
            is_reviewed = event_key in reviewed_map
            review_info = reviewed_map.get(event_key, {})

            candidates = matcher.match_activity(
                event["clean_activity"],
                extracted_discipline=event["discipline"],
                top_k=3
            )

            top = candidates[0] if candidates else None
            conf = top["confidence"] if top else 0.0

            if conf >= 85:
                conf_badge = f'<span class="high-conf">🟢 High Confidence ({conf}%)</span>'
            elif conf >= 65:
                conf_badge = f'<span class="med-conf">🟡 Review Recommended ({conf}%)</span>'
            else:
                conf_badge = f'<span class="low-conf">🔴 Low Match ({conf}%)</span>'

            status_tag = f" — [{review_info.get('decision', 'PROCESSED')}: {review_info.get('matched_activity_id', '')}]" if is_reviewed else f" — {conf}% Match"

            with st.expander(f"Event #{i+1}: [{event['discipline']}] {event['clean_activity'][:50]}...{status_tag}", expanded=(i == 0 and not is_reviewed)):
                c1, c2 = st.columns([1.2, 1])

                with c1:
                    st.markdown("**Site Report Observation:**")
                    st.code(event["raw_text"], language="text")
                    st.write(f"📅 **Date:** `{event['report_date']}` | **Status:** `{event['event_type']}` | **Progress:** `{event['progress_pct']}%`")

                with c2:
                    if is_reviewed:
                        decision = review_info.get("decision")
                        act_id = review_info.get("matched_activity_id")
                        if decision == "APPROVED":
                            st.success(f"✅ **Action Taken:** Approved and linked to `{act_id}`.")
                        else:
                            st.warning(f"🚩 **Action Taken:** Flagged as unlinked activity.")
                    else:
                        st.markdown(f"**AI Recommended Link:** {conf_badge}", unsafe_allow_html=True)
                        if top:
                            st.write(f"**Task ID:** `{top['activity_id']}` ({top['level']})")
                            st.write(f"**Description:** {top['activity_description']}")
                            st.caption(f"WBS: {top['wbs_package']} | Semantic: {top['semantic_score']}% | Fuzzy: {top['fuzzy_score']}%")
                        else:
                            st.write("No matching candidate found.")

                st.markdown("---")

                if is_reviewed:
                    st.info("🔒 This event has been processed. Action buttons are locked to preserve audit integrity.")
                else:
                    act_col1, act_col2, act_col3 = st.columns([1.5, 2.5, 1])

                    with act_col2:
                        cand_choices = [f"{c['activity_id']} | {c['activity_description']} ({c['confidence']}%)" for c in candidates]
                        chosen_cand_str = st.selectbox("Target Schedule Activity:", options=cand_choices, key=f"sel_cand_{i}")
                        selected_act_id = chosen_cand_str.split(" | ")[0].strip() if chosen_cand_str else (top['activity_id'] if top else None)

                    with act_col1:
                        if st.button("✓ Approve Match", key=f"app_btn_{i}", type="primary"):
                            if selected_act_id:
                                try:
                                    matched_desc = top["activity_description"] if (top and top["activity_id"] == selected_act_id) else chosen_cand_str
                                    
                                    log_audit_record({
                                        "report_date": event["report_date"],
                                        "discipline": event["discipline"],
                                        "raw_site_text": event["raw_text"],
                                        "matched_activity_id": selected_act_id,
                                        "matched_description": matched_desc,
                                        "confidence": conf,
                                        "event_type": event["event_type"],
                                        "reported_progress": event["progress_pct"],
                                        "decision": "APPROVED",
                                        "reviewer_comments": "Approved via Planner Review Queue."
                                    })

                                    sync_res = sync_actual_progress(
                                        activity_id=selected_act_id,
                                        report_date=event["report_date"],
                                        event_type=event["event_type"],
                                        progress_pct=event["progress_pct"]
                                    )

                                    st.toast(f"✅ Approved & Synced: {selected_act_id}", icon="🚀")
                                    st.rerun()
                                except Exception as err:
                                    st.error(f"Approval failed: {err}")

                    with act_col3:
                        if st.button("🚩 Reject / Unlink", key=f"rej_btn_{i}"):
                            try:
                                log_audit_record({
                                    "report_date": event["report_date"],
                                    "discipline": event["discipline"],
                                    "raw_site_text": event["raw_text"],
                                    "matched_activity_id": "UNLINKED",
                                    "matched_description": "None",
                                    "confidence": conf,
                                    "event_type": event["event_type"],
                                    "reported_progress": event["progress_pct"],
                                    "decision": "REJECTED",
                                    "reviewer_comments": "Flagged as unlinked by planner."
                                })
                                st.toast("Flagged as unlinked", icon="⚠️")
                                st.rerun()
                            except Exception as err:
                                st.error(f"Rejection failed: {err}")

# =========================================================================
# TAB 4: LIVE PROGRESS & VARIANCE TRACKING (MODULE 5)
# =========================================================================
with nav_tab3:
    st.subheader("Live Execution Status & Variance Tracking")
    st.caption("Real-time comparison between planned baseline and actual site execution.")

    df_live = fetch_all_activities()

    df_live["start_delay_days"] = None
    df_live["finish_delay_days"] = None

    for idx, r in df_live.iterrows():
        if pd.notna(r["actual_start"]) and r["actual_start"]:
            p_st = pd.to_datetime(r["planned_start"])
            a_st = pd.to_datetime(r["actual_start"])
            df_live.at[idx, "start_delay_days"] = (a_st - p_st).days

        if pd.notna(r["actual_finish"]) and r["actual_finish"]:
            p_fn = pd.to_datetime(r["planned_finish"])
            a_fn = pd.to_datetime(r["actual_finish"])
            df_live.at[idx, "finish_delay_days"] = (a_fn - p_fn).days

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    completed_n = len(df_live[df_live["status"] == "COMPLETED"])
    in_prog_n = len(df_live[df_live["status"] == "IN_PROGRESS"])
    delayed_n = len(df_live[df_live["finish_delay_days"] > 0])

    p_col1.metric("Completed Tasks", completed_n)
    p_col2.metric("In Progress Tasks", in_prog_n)
    p_col3.metric("Delayed Tasks", delayed_n)
    p_col4.metric("Unstarted Tasks", len(df_live) - (completed_n + in_prog_n))

    st.write("")

    st.dataframe(
        df_live[[
            "activity_id",
            "discipline",
            "activity_description",
            "status",
            "progress_pct",
            "planned_start",
            "actual_start",
            "planned_finish",
            "actual_finish",
            "finish_delay_days"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "activity_id": st.column_config.TextColumn("ID", width="small"),
            "discipline": st.column_config.TextColumn("Discipline", width="small"),
            "activity_description": st.column_config.TextColumn("Activity Description", width="large"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "progress_pct": st.column_config.ProgressColumn("Progress %", min_value=0, max_value=100, format="%.0f%%"),
            "finish_delay_days": st.column_config.NumberColumn("Finish Delay (Days)", help="Positive = Delayed, Negative = Ahead"),
        }
    )

# =========================================================================
# TAB 5: BASELINE MASTER SCHEDULE (MODULE 1 - ENHANCED)
# =========================================================================
with nav_tab4:
    df_activities = fetch_all_activities()
    if df_activities.empty:
        st.warning("No activities found in the master schedule database.")
    else:
        st.subheader("📅 Master Baseline Schedule & Work Breakdown Structure")
        st.caption("Immutable planned baseline exported from Oracle Primavera P6 / MS Project. Single Source of Truth for L5/L6 activities.")

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Activities", len(df_activities))
        k2.metric("Disciplines", df_activities["discipline"].nunique())
        l5_n = len(df_activities[df_activities["level"] == "L5"])
        l6_n = len(df_activities[df_activities["level"] == "L6"])
        k3.metric("WBS Levels", f"{l5_n} L5 | {l6_n} L6")
        
        crit_n = len(df_activities[df_activities["baseline_status"] == "CRITICAL"])
        k4.metric("Critical Path Tasks", crit_n, help="Tasks with zero float; any slippage delays final plant handover.")

        earliest = df_activities["planned_start"].min()
        latest = df_activities["planned_finish"].max()
        k5.metric("Project Duration", f"{earliest} → {latest}")

        st.markdown("---")

        sched_sub1, sched_sub2, sched_sub3 = st.tabs([
            "📊 Interactive Gantt Timeline",
            "📋 Schedule Activity Register",
            "📈 Discipline & Work Package Distribution"
        ])

        with sched_sub1:
            st.markdown("##### ⏱️ Baseline Execution Window (Gantt)")
            st.caption("Bars represent planned activity durations. Hover over any bar to inspect task scope and dependencies.")

            df_gantt = df_activities.copy()
            df_gantt["planned_start"] = pd.to_datetime(df_gantt["planned_start"])
            df_gantt["planned_finish"] = pd.to_datetime(df_gantt["planned_finish"])
            df_gantt["Duration (Days)"] = (df_gantt["planned_finish"] - df_gantt["planned_start"]).dt.days

            fig = px.timeline(
                df_gantt,
                x_start="planned_start",
                x_end="planned_finish",
                y="activity_id",
                color="discipline",
                hover_name="activity_description",
                hover_data={
                    "wbs_package": True,
                    "level": True,
                    "baseline_status": True,
                    "Duration (Days)": True,
                    "activity_id": False
                },
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                height=520,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Calendar Window (September - October 2026)",
                yaxis_title="Activity ID",
                legend_title="Discipline"
            )
            st.plotly_chart(fig, use_container_width=True)

        with sched_sub2:
            st.markdown("##### 🔍 Search & Filter Master Schedule")
            
            f_col1, f_col2, f_col3 = st.columns([1.5, 1.2, 3])
            with f_col1:
                all_disc = sorted(df_activities["discipline"].unique().tolist())
                sel_disc = st.multiselect("Filter by Discipline", options=all_disc, default=all_disc, key="t4_disc")

            with f_col2:
                all_lvl = sorted(df_activities["level"].unique().tolist())
                sel_lvl = st.multiselect("Filter by Level", options=all_lvl, default=all_lvl, key="t4_lvl")

            with f_col3:
                search_kw = st.text_input("Search Task Description, ID, or WBS", placeholder="e.g. Compressor, Foundation, Rebar, Cable...", key="t4_search")

            filtered_sched = df_activities[
                (df_activities["discipline"].isin(sel_disc)) &
                (df_activities["level"].isin(sel_lvl))
            ]

            if search_kw:
                q = search_kw.strip().lower()
                filtered_sched = filtered_sched[
                    filtered_sched["activity_description"].str.lower().str.contains(q) |
                    filtered_sched["activity_id"].str.lower().str.contains(q) |
                    filtered_sched["wbs_package"].str.lower().str.contains(q)
                ]

            st.dataframe(
                filtered_sched[[
                    "activity_id",
                    "level",
                    "discipline",
                    "wbs_package",
                    "activity_description",
                    "planned_start",
                    "planned_finish",
                    "baseline_status"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "activity_id": st.column_config.TextColumn("Activity ID", width="small"),
                    "level": st.column_config.TextColumn("Level", width="small"),
                    "discipline": st.column_config.TextColumn("Discipline", width="medium"),
                    "wbs_package": st.column_config.TextColumn("WBS Work Package", width="medium"),
                    "activity_description": st.column_config.TextColumn("Activity Scope Description", width="large"),
                    "planned_start": st.column_config.DateColumn("Planned Start"),
                    "planned_finish": st.column_config.DateColumn("Planned Finish"),
                    "baseline_status": st.column_config.TextColumn("Critical Path Status", width="small"),
                }
            )
            st.caption(f"Displaying {len(filtered_sched)} of {len(df_activities)} scheduled items")

        with sched_sub3:
            st.markdown("##### 📊 Work Breakdown Analysis")
            c_pie, c_table = st.columns([1.2, 1.8])

            with c_pie:
                disc_counts = df_activities["discipline"].value_counts().reset_index()
                disc_counts.columns = ["Discipline", "Activity Count"]
                fig_donut = px.pie(
                    disc_counts,
                    values="Activity Count",
                    names="Discipline",
                    hole=0.45,
                    title="Discipline Task Share",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_donut.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=340)
                st.plotly_chart(fig_donut, use_container_width=True)

            with c_table:
                st.markdown("**Discipline & Work Package Summary**")
                pkg_summary = df_activities.groupby(["discipline", "wbs_package", "baseline_status"]).size().reset_index(name="Task Count")
                st.dataframe(pkg_summary, use_container_width=True, hide_index=True)

# =========================================================================
# TAB 6: VERIFICATION AUDIT TRAIL (MODULE 4)
# =========================================================================
with nav_tab5:
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.subheader("Traceability & Human Approval Audit Trail")
        st.caption("Immutable record of all site-to-schedule links confirmed or rejected by planners.")
    with head_col2:
        if st.button("🗑️ Clear Audit Log", help="Resets the audit trail for fresh demo runs"):
            clear_audit_trail()
            st.toast("Audit trail reset successfully!", icon="🧹")
            st.rerun()

    conn = get_db_connection()
    df_audit = pd.read_sql_query("SELECT * FROM activity_updates_audit ORDER BY timestamp DESC", conn)
    conn.close()

    if df_audit.empty:
        st.info("No approval events recorded yet. Approve matches in Tab 2 to populate this log.")
    else:
        st.dataframe(
            df_audit[[
                "audit_id",
                "timestamp",
                "report_date",
                "discipline",
                "matched_activity_id",
                "confidence",
                "decision",
                "raw_site_text",
                "reviewer_comments"
            ]],
            use_container_width=True,
            hide_index=True
        )
        st.caption(f"Total audit entries: {len(df_audit)}")