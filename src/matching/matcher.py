"""
OIL-Track AI - Module 3
matcher.py: Tuned Hybrid AI matching engine combining semantic embeddings,
domain ontology synonyms, and fuzzy string metrics.
"""

import os
import re
import sqlite3
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "all-MiniLM-L6-v2"

# Domain-specific ontology mapping for Oil & Gas infrastructure
DOMAIN_SYNONYMS = {
    r"\brebar\b": "reinforcement steel rebar",
    r"\bconcreting\b": "concrete pouring cast",
    r"\bpcc\b": "plain cement concrete",
    r"\bfit-up\b": "joint fit-up alignment",
    r"\bcable tray\b": "overhead cable tray",
    r"\bloop checking\b": "instrument loop test check",
    r"\bhydrotest\b": "hydrotesting pressure test"
}

def expand_domain_terms(text: str) -> str:
    """Expands construction jargon into standard engineering synonyms."""
    cleaned = text.lower()
    for pattern, replacement in DOMAIN_SYNONYMS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned

class ActivityMatcher:
    def __init__(self, db_path=os.path.join("database", "oil_track.db")):
        self.db_path = db_path
        self.model = SentenceTransformer(MODEL_NAME)
        self.schedule_df = pd.DataFrame()
        self.schedule_embeddings = None
        self.reload_schedule()

    def reload_schedule(self):
        """Loads baseline activities from SQLite and builds contextual embeddings."""
        conn = sqlite3.connect(self.db_path)
        self.schedule_df = pd.read_sql_query(
            "SELECT activity_id, level, discipline, wbs_package, activity_description FROM planned_activities",
            conn
        )
        conn.close()

        if self.schedule_df.empty:
            print("[Matcher] Warning: Schedule database is empty!")
            return

        # Combine WBS package and activity description for richer semantic context
        contextual_descriptions = [
            f"{row['discipline']} - {row['wbs_package']}: {row['activity_description']}"
            for _, row in self.schedule_df.iterrows()
        ]
        self.schedule_embeddings = self.model.encode(
            contextual_descriptions,
            convert_to_tensor=True,
            show_progress_bar=False
        )

    def match_activity(self, extracted_text: str, extracted_discipline: str = "Unknown", top_k: int = 3) -> list[dict]:
        """Matches extracted text against the schedule candidate pool."""
        if self.schedule_df.empty or self.schedule_embeddings is None:
            return []

        expanded_text = expand_domain_terms(extracted_text)
        query_context = f"{extracted_discipline}: {expanded_text}" if extracted_discipline != "Unknown" else expanded_text

        query_embedding = self.model.encode(query_context, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, self.schedule_embeddings)[0].cpu().numpy()

        results = []
        for idx, row in self.schedule_df.iterrows():
            cand_desc = row["activity_description"]
            cand_disc = row["discipline"]

            semantic_score = float(cos_scores[idx]) * 100.0

            # Compute fuzzy scores against both raw description and expanded string
            fuzzy_desc = fuzz.token_set_ratio(expanded_text.lower(), cand_desc.lower())
            fuzzy_wbs = fuzz.token_set_ratio(expanded_text.lower(), row["wbs_package"].lower())
            fuzzy_score = max(fuzzy_desc, fuzzy_wbs * 0.8)

            # 70% Semantic + 30% Fuzzy weighting
            hybrid_score = (0.70 * semantic_score) + (0.30 * fuzzy_score)

            # Discipline validation
            disc_match = (
                extracted_discipline != "Unknown" and 
                extracted_discipline.lower() == cand_disc.lower()
            )
            if disc_match:
                hybrid_score += 10.0
            elif extracted_discipline != "Unknown" and extracted_discipline.lower() != cand_disc.lower():
                hybrid_score -= 15.0

            final_confidence = min(max(hybrid_score, 0.0), 100.0)

            results.append({
                "activity_id": row["activity_id"],
                "level": row["level"],
                "discipline": cand_disc,
                "wbs_package": row["wbs_package"],
                "activity_description": cand_desc,
                "semantic_score": round(semantic_score, 1),
                "fuzzy_score": round(fuzzy_score, 1),
                "discipline_match": disc_match,
                "confidence": round(final_confidence, 1)
            })

        results = sorted(results, key=lambda x: x["confidence"], reverse=True)
        return results[:top_k]

if __name__ == "__main__":
    matcher = ActivityMatcher()

    test_queries = [
        ("Rebar fixing completed for compressor foundation", "Civil"),
        ("Suction line joint fit-up and alignment", "Piping"),
        ("Overhead cable tray installation", "Electrical"),
        ("Emergency shower inspection", "HSE")
    ]

    print("\n--- RUNNING TUNED MATCHER VERIFICATION ---")
    for text, disc in test_queries:
        matches = matcher.match_activity(text, disc, top_k=1)
        top = matches[0]
        print(f"\nSite Query: \"{text}\" [{disc}]")
        print(f"Top Match:  {top['activity_id']} - \"{top['activity_description']}\"")
        print(f"Confidence: {top['confidence']}% (Semantic: {top['semantic_score']}%, Fuzzy: {top['fuzzy_score']}%)")