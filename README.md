# 🌉 SETU AI (सेतु): Schedule Execution Tracking & Unification Engine

> **Smart India Hackathon (SIH 2026) | Problem ID:** SIH26122  
> **Target Organization:** Oil India Limited (OIL)  
> **Domain:** Smart Infrastructure / Project Management Automation  
> **Asset Focus:** Duliajan Gas Compressor Station & Manifold Expansion  

---

## 📌 Executive Summary

Major upstream oil and gas infrastructure projects face chronic schedule slippage. While central project management offices (PMOs) maintain structured baselines in **Oracle Primavera P6** and **Microsoft Project**, construction sites generate fragmented progress data via daily free-text diaries, WhatsApp updates, and discipline-specific Excel logs.

Because site updates never automatically sync to master schedules, delays compound invisibly until critical paths are breached.

**SETU AI** acts as an intelligent, automated bridge (*Setu*) that connects unstructured ground execution directly into enterprise schedules through hybrid AI matching, Human-in-the-Loop oversight, and real-time delay analytics.

---

## 🏗️ System Architecture & Data Pipeline

```text
[ Field Site Reports ]                      [ Master Schedule Exports ]
  - Daily Free-Text Diaries (.txt)            - Primavera P6 / MS Project (.xlsx/.csv)
  - Discipline Excel Logs (.xlsx)                                 |
                 |                                                v
                 v                                   +---------------------------+
+---------------------------------+                  |  Module 1: Schedule DB    |
|  Module 2: Rule/Regex Extractor |                  |  - SQLite (L5/L6 schema)  |
|  - Date, Discipline, Action     |                  |  - Interactive Gantt      |
|  - Event Lifecycle & % Progress |                  +-------------+-------------+
+----------------+----------------+                                |
                 |                                                 |
                 v                                                 v
+--------------------------------------------------------------------------------+
| Module 3: Hybrid AI Semantic Matching Engine                                   |
| - Domain Term Expansion (Rebar -> Reinforcement Steel)                         |
| - Dense Vector Semantic Embeddings (Sentence-Transformers: all-MiniLM-L6-v2)   |
| - Lexical Fuzzy Token Alignment (RapidFuzz Token-Set Ratio)                    |
| - Discipline Constraint Logic & Confidence Calibration (0-100%)                |
+----------------------------------------+---------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------+
| Module 4: Human-in-the-Loop (HITL) Validation & Deduplication                  |
| - Confidence Tiers (High >=85% | Review 65-84% | Low <65%)                     |
| - Planner Approval / Override / Unlink Interface                               |
| - Idempotent State Locking (Prevents Duplicate Entries)                        |
| - Immutable Audit Trail (activity_updates_audit)                               |
+----------------------------------------+---------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------+
| Module 5: Schedule Synchronization & Variance Engine                           |
| - Start Variance: (Actual Start - Planned Start)                               |
| - Finish Variance: (Actual Finish - Planned Finish)                            |
| - Database State Update (NOT_STARTED -> IN_PROGRESS -> COMPLETED)              |
+----------------------------------------+---------------------------------------+
                                         |
                                         v
+--------------------------------------------------------------------------------+
| Module 6: Executive Delay Intelligence & Analytics Dashboard                   |
| - Critical Path Threat Flags (Float Erosion Alerts)                            |
| - Discipline Slippage Benchmarks (Average Days Delayed)                        |
| - Real-Time Physical Completion vs. Baseline Window                            |
+--------------------------------------------------------------------------------+

# 🚀 Key Modules & Functional Capabilities

OIL-Track AI is organized into six core modules, each responsible for a specific stage of the **planning-to-execution bridge**.

| Module                          | Purpose                                                                                                                          | Technical Stack                     |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Module 1: Schedule Baseline** | Ingests L5/L6 activities, establishes baseline dates, and renders interactive Gantt charts.                                      | SQLite3, Pandas, Plotly Express     |
| **Module 2: Field Extraction**  | Normalizes daily unstructured logs into discrete execution events.                                                               | Python `re`, OpenPyXL               |
| **Module 3: Hybrid AI Matcher** | Bridges site terminology such as *“rebar”* and *“concreting”* to schedule terminology such as *“reinforcement”* and *“casting”*. | `all-MiniLM-L6-v2`, RapidFuzz       |
| **Module 4: HITL Validation**   | Provides planners with an approval queue, confidence scoring, and deduplication locking.                                         | Streamlit State, SQLite Audit Table |
| **Module 5: Progress Sync**     | Updates actual start/finish dates, computes daily delay variance, and synchronizes master records.                               | Python `datetime`, SQLite Upsert    |
| **Module 6: Delay Analytics**   | Surfaces critical-path threats, discipline delay hotspots, and physical completion rates.                                        | Plotly Express, Aggregate Analytics |

## Module Workflow

```text
Project Schedule
       │
       ▼
┌──────────────────────────┐
│  Module 1                │
│  Schedule Baseline       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Module 2                │
│  Field Extraction        │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Module 3                │
│  Hybrid AI Matcher       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Module 4                │
│  HITL Validation         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Module 5                │
│  Progress Synchronization│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Module 6                │
│  Delay Analytics         │
└──────────────────────────┘
```

## Core Flow

**Schedule Baseline → Field Data Extraction → AI Activity Matching → Human Validation → Progress Synchronization → Delay Analytics**

This architecture creates a continuous bridge between the **planned L5/L6 schedule** and **actual field execution data**.

# 🛠️ Technology Stack

The OIL-Track AI prototype uses a lightweight, modular technology stack designed for **rapid development, local execution, and reliable processing of project-progress data**.

| Category                   | Technology                                            | Purpose                                                                                       |
| -------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Programming Language**   | Python 3.11+                                          | Core application logic, data processing, AI/ML integration, and automation                    |
| **Frontend Framework**     | Streamlit                                             | Interactive web interface with a custom dark industrial enterprise theme                      |
| **Embedded Database**      | SQLite3                                               | Local relational database for schedules, progress records, validation data, and audit logs    |
| **Data Engineering**       | Pandas, NumPy, OpenPyXL                               | Data cleaning, transformation, analysis, and Excel file processing                            |
| **Semantic Embeddings**    | Hugging Face `sentence-transformers/all-MiniLM-L6-v2` | Local, CPU-optimized semantic representation of activity descriptions                         |
| **Fuzzy Matching**         | RapidFuzz                                             | Fast lexical matching using Levenshtein distance and token-based similarity                   |
| **Visualization**          | Plotly Express                                        | Interactive Gantt charts, delay distributions, progress visualizations, and completion charts |
| **Verification & Testing** | Python `unittest`                                     | Automated testing of core application components and processing workflows                     |

## 🏗️ Architecture Philosophy

The technology stack is intentionally designed around four principles:

* **Lightweight:** The prototype can run locally without requiring a complex cloud infrastructure.
* **Modular:** Each technology has a clearly defined responsibility within the system.
* **Explainable:** Matching and validation processes can be inspected and audited.
* **Scalable:** Components such as SQLite, local embeddings, and Streamlit can later be replaced or extended for production deployment.

## 🤖 AI & Matching Layer

The core intelligent matching system combines two complementary approaches:

**Semantic Matching**

`all-MiniLM-L6-v2` converts activity descriptions into numerical embeddings, allowing the system to identify activities with similar meanings even when different terminology is used.

**Fuzzy Matching**

`RapidFuzz` compares textual similarity between field terminology and schedule activities, helping handle abbreviations, spelling variations, and terminology differences.

The combination creates a **Hybrid AI Matching Engine** that connects field language with structured L5/L6 schedule activities.


📁 Repository Structure
OIL-Track-AI/
|-- app.py                           # Main Streamlit 5-tab application cockpit
|-- requirements.txt                 # Pinned dependencies
|-- README.md                        # Technical documentation and project dossier
|-- database/
|   `-- oil_track.db                 # SQLite database (planned_activities and audit trail)
|-- data/
|   |-- schedule/
|   |   `-- project_schedule.xlsx    # Baseline Primavera P6 export (18 L5/L6 activities)
|   `-- daily_reports/
|       |-- site_diary_2026_09_07.txt# Synthetic raw unstructured site diary
|       `-- discipline_daily_log.xlsx# Multi-column discipline field spreadsheet
|-- src/
|   |-- schedule/
|   |   |-- generate_sample_schedule.py # Baseline schedule generator
|   |   `-- db_manager.py            # SQLite schema, ingestion, sync, and audit functions
|   |-- extraction/
|   |   |-- generate_sample_reports.py  # Synthetic site update generator
|   |   `-- extractor.py             # Rule and Regex parser for text/Excel reports
|   |-- matching/
|   |   `-- matcher.py               # Hybrid semantic and lexical matching engine
|   `-- analytics/
|       `-- engine.py                # Schedule variance and critical path KPI analytics
`-- tests/
    `-- test_pipeline.py             # Automated unit and integration test suite

# ⚙️ Quickstart Guide

Follow the steps below to set up, initialize, test, and launch **OIL-Track AI** locally.

## 1. Set Up the Environment

Create a Python virtual environment, activate it, and install the required dependencies.

**PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Note:** If PowerShell blocks script execution, you may need to adjust the execution policy or activate the environment using Command Prompt instead.

---

## 2. Initialize the Database & Generate Baseline Artifacts

Run the following scripts to generate the sample project schedule, initialize the SQLite database, and create sample field reports.

**PowerShell:**

```powershell
python src/schedule/generate_sample_schedule.py
python src/schedule/db_manager.py
python src/extraction/generate_sample_reports.py
```

### What These Commands Do

| Script                        | Function                                         |
| ----------------------------- | ------------------------------------------------ |
| `generate_sample_schedule.py` | Generates the synthetic L5/L6 project schedule   |
| `db_manager.py`               | Initializes and prepares the SQLite database     |
| `generate_sample_reports.py`  | Generates synthetic daily field-progress reports |

---

## 3. Run Automated Tests

Execute the automated test suite to verify that the core pipeline is functioning correctly.

**PowerShell:**

```powershell
python -m unittest tests/test_pipeline.py
```

A successful run should show that the configured test cases have passed.

---

## 4. Launch the Web Application

Start the Streamlit application using:

**PowerShell:**

```powershell
streamlit run app.py
```

After launching, Streamlit will provide a local URL in the terminal. Open that URL in your browser to access the **OIL-Track AI** dashboard.

---

## 🚀 Quick Command Summary

For convenience, the complete setup sequence is:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

python src/schedule/generate_sample_schedule.py
python src/schedule/db_manager.py
python src/extraction/generate_sample_reports.py

python -m unittest tests/test_pipeline.py

streamlit run app.py
```

## ✅ Expected Workflow

```text
Environment Setup
       ↓
Install Dependencies
       ↓
Generate Sample Schedule
       ↓
Initialize SQLite Database
       ↓
Generate Sample Field Reports
       ↓
Run Automated Tests
       ↓
Launch Streamlit Application
       ↓
Access OIL-Track AI Dashboard
```

## 🧪 Verification Matrix

OIL-Track AI includes automated verification tests covering the major components of the data-processing and progress-tracking pipeline.

| Test ID   | Target Component     | Input Condition                                      | Expected Result                                                  | Status   |
| --------- | -------------------- | ---------------------------------------------------- | ---------------------------------------------------------------- | -------- |
| `test_01` | Discipline Parser    | `"1. Civil Discipline: Reinforcement..."`            | Extracted discipline: `"Civil"`                                  | **PASS** |
| `test_02` | Status Parser        | `"Rebar fixing completed today"`                     | Status: `"COMPLETED"`                                            | **PASS** |
| `test_03` | Semantic Matcher     | `"Rebar fixing completed for compressor foundation"` | Matched activity: `CIV-FND-003` with **≥ 80% confidence**        | **PASS** |
| `test_04` | Variance Calculation | Planned: `2026-09-09`<br>Actual: `2026-09-11`        | Finish variance: **+2 days**                                     | **PASS** |
| `test_05` | Deduplication        | Repeated approval event                              | Event key exists in reviewed map; duplicate processing prevented | **PASS** |

### 📊 Verification Summary

| Metric         |                   Result |
| -------------- | -----------------------: |
| Total Tests    |                    **5** |
| Passed         |                    **5** |
| Failed         |                    **0** |
| Overall Status |               **✅ PASS** |
| Test Coverage  | Core pipeline components |

### 🔍 Components Verified

The verification suite validates the following critical capabilities:

* **Discipline Parsing** — Correctly identifies the project discipline from field reports.
* **Status Detection** — Identifies execution states such as `COMPLETED`.
* **Semantic Activity Matching** — Maps field terminology to the appropriate L5/L6 schedule activity.
* **Variance Calculation** — Calculates the difference between planned and actual execution dates.
* **Deduplication** — Prevents the same approval/progress event from being processed multiple times.

> **Verification Result:** All five core automated test cases pass successfully, confirming that the primary data extraction, matching, synchronization, and validation components are functioning as expected.
