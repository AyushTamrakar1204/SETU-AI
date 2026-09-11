"""
OIL-Track AI - Module 2
extractor.py: Parses free-text and tabular site reports into structured event data 
with intelligent engineering terminology normalization.
"""

import os
import re
import pandas as pd

# Keywords for rule-based extraction
DISCIPLINES = ["Civil", "Mechanical", "Piping", "Electrical", "Instrumentation", "HSE"]

STATUS_MAPPING = {
    "COMPLETED": ["completed", "finished", "done"],
    "STARTED": ["started", "began", "commenced"],
    "IN_PROGRESS": ["in progress", "ongoing", "continuing"]
}

def detect_discipline(text: str) -> str:
    """Finds the first matching discipline in a text string."""
    text_lower = text.lower()
    for d in DISCIPLINES:
        if d.lower() in text_lower:
            return d
    return "Unknown"

def detect_status(text: str) -> str:
    """Infers the event status from keywords in the text."""
    text_lower = text.lower()
    for status, keywords in STATUS_MAPPING.items():
        for kw in keywords:
            if kw in text_lower:
                return status
    return "UNKNOWN"

def normalize_field_jargon(text: str) -> str:
    """
    Normalizes common site slang/jargon into standard L5/L6 engineering terminology 
    to bridge vocabulary gaps and ensure high organic AI matching confidence.
    """
    normalized = text.lower()
    
    # Construction vocabulary dictionary for Oil & Gas projects
    jargon_map = {
        "rebar": "reinforcement work",
        "shuttering": "formwork",
        "pcc": "plain cement concrete foundation",
        "cc": "concrete pouring",
        "exc": "excavation",
        "sleeper": "sleeper foundations",
        "ms line": "pipeline erection and welding",
        "hydro": "hydrotesting"
    }
    
    for jargon, formal in jargon_map.items():
        # Match whole words or phrase patterns
        normalized = re.sub(rf"\b{jargon}\b", formal, normalized)
        
    return normalized

def clean_action_text(text: str, discipline: str) -> str:
    """Removes discipline prefixes, numbers, and normalizes field jargon for the AI matcher."""
    # Remove leading numbers and bullets (e.g., "1. ", "- ")
    clean = re.sub(r"^[\d\.\-\s]+", "", text)
    # Remove the discipline name if it starts the sentence (e.g., "Civil Discipline: ")
    clean = re.sub(rf"(?i)^{discipline}\s*(discipline)?\s*:\s*", "", clean)
    
    # Normalize field jargon into formal engineering terms for accurate semantic matching
    clean = normalize_field_jargon(clean)
    
    return clean.strip()

def parse_text_diary(file_path: str) -> list[dict]:
    """Extracts events from a free-text daily site diary."""
    events = []
    report_date = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Extract master report date
        date_match = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            report_date = date_match.group(1)
            continue

        # Extract execution items (assuming numbered lists for the MVP)
        if re.match(r"^\d+\.", line):
            discipline = detect_discipline(line)
            status = detect_status(line)
            clean_text = clean_action_text(line, discipline)
            
            # Estimate progress based on status
            progress = 100.0 if status == "COMPLETED" else (20.0 if status == "STARTED" else 50.0)

            events.append({
                "source_type": "Free Text",
                "report_date": report_date or "Unknown",
                "discipline": discipline,
                "raw_text": line,
                "clean_activity": clean_text,
                "event_type": status,
                "progress_pct": progress
            })

    return events

def parse_excel_log(file_path: str) -> list[dict]:
    """Extracts events from a tabular discipline-wise Excel log."""
    events = []
    df = pd.read_excel(file_path, engine="openpyxl")

    for _, row in df.iterrows():
        raw_text = str(row.get("Work Description", ""))
        discipline = str(row.get("Discipline", detect_discipline(raw_text)))
        status_raw = str(row.get("Reported Status", ""))
        
        status = detect_status(status_raw + " " + raw_text)
        
        prog_str = str(row.get("Estimated Progress", "0")).replace("%", "")
        try:
            progress = float(prog_str)
        except ValueError:
            progress = 0.0

        events.append({
            "source_type": "Excel Log",
            "report_date": str(row.get("Date", "Unknown"))[:10],
            "discipline": discipline.strip(),
            "raw_text": raw_text,
            "clean_activity": clean_action_text(raw_text, discipline),
            "event_type": status,
            "progress_pct": progress
        })

    return events

if __name__ == "__main__":
    txt_file = os.path.join("data", "daily_reports", "site_diary_2026_09_07.txt")
    excel_file = os.path.join("data", "daily_reports", "discipline_daily_log.xlsx")

    print("--- EXTRACTING FROM TEXT DIARY ---")
    txt_events = parse_text_diary(txt_file)
    for e in txt_events:
        print(f"[{e['discipline']} | {e['event_type']}] {e['clean_activity']} ({e['progress_pct']}%)")

    print("\n--- EXTRACTING FROM EXCEL LOG ---")
    excel_events = parse_excel_log(excel_file)
    for e in excel_events:
         print(f"[{e['discipline']} | {e['event_type']}] {e['clean_activity']} ({e['progress_pct']}%)")