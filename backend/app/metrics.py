from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
XLSX = DATA_DIR / "OU_Tasks_SKUs.xlsx"

QUALITY_METRICS = {
    "average_amends_globally": 1.8,
    "current_year_average_amends": 1.8,
    "global_version_1_percent": 50.7,
    "current_year_version_1_percent": 50.9,
    "total_projects_skus": 78790,
    "total_artworks": 57229,
    "average_amends_by_operating_unit": {
        "ASP": 2.2, "AFRICA": 1.9, "EU": 1.8, "LATAM": 1.7,
        "NA": 1.7, "EME": 1.6, "INSWA": 1.6, "GCM": 1.4,
        "SK": 1.5, "JP": 1.5
    },
    "snapshot_date_range": "2024-04-02 to 2026-08-08",
}

VOLUME_METRICS = {
    "total_projects_skus": 43404,
    "total_artworks": 30878,
    "projects_completed_percent": 77,
    "projects_canceled_percent": 17,
    "projects_work_in_progress_percent": 6,
    "busiest_market": "India",
    "busiest_market_projects": 3246,
}

def _report_df():
    return pd.read_excel(XLSX, sheet_name="Report", header=None)

def _report_records():
    df = _report_df()
    headers = list(df.iloc[1])
    rows = []
    for _, r in df.iloc[2:12].iterrows():
        if pd.isna(r.iloc[0]): continue
        item = {}
        for i,h in enumerate(headers):
            key = str(h).strip() if not pd.isna(h) else f"column_{i}"
            v = r.iloc[i]
            if pd.isna(v) or v == "-": v = None
            item[key] = v.item() if hasattr(v, "item") else v
        rows.append(item)
    return rows

def data_answer(question: str) -> str:
    q = question.lower()
    rows = _report_records()
    if any(k in q for k in ["user", "users"]):
        parts = []
        for r in rows:
            parts.append(f"{r['OU']}: {int(r['Users (OU)'])} OU users, {int(r['Users (Approvals)'])} approval users, {int(r['Users Logged (6 months)'])} users logged in 6 months")
        return "OU user counts from the attached OU_Tasks_SKUs workbook: " + "; ".join(parts) + "."
    if "project" in q and any(k in q for k in ["how many", "count", "created", "total"]):
        return (f"The supplied Volume dashboard snapshot shows {VOLUME_METRICS['total_projects_skus']:,} total projects (SKU's) and {VOLUME_METRICS['total_artworks']:,} total artworks.")
    if "sku" in q:
        parts = [f"{r['OU']}: {int(r['SKUs'])} SKUs" for r in rows]
        return "SKU counts by OU from the workbook: " + "; ".join(parts) + "."
    if "artwork" in q:
        parts = [f"{r['OU']}: {int(r['Number of Artworks Approved'])} approved artworks" for r in rows]
        return "Approved artwork counts by OU from the workbook: " + "; ".join(parts) + "."
    if "amend" in q or "amends" in q:
        return "Quality dashboard snapshot: global average amends is 1.8. By OU: " + ", ".join(
            f"{k} {v}" for k,v in QUALITY_METRICS["average_amends_by_operating_unit"].items()
        ) + f". Snapshot date range shown: {QUALITY_METRICS['snapshot_date_range']}."
    if "version" in q:
        return f"Quality dashboard snapshot: Global Version 1% is {QUALITY_METRICS['global_version_1_percent']}% and Current Year Version 1% is {QUALITY_METRICS['current_year_version_1_percent']}%."
    if "volume" in q or "completed" in q or "cancel" in q or "work in progress" in q:
        return (f"Volume dashboard snapshot: {VOLUME_METRICS['total_projects_skus']:,} projects (SKUs), "
                f"{VOLUME_METRICS['total_artworks']:,} artworks; {VOLUME_METRICS['projects_completed_percent']}% completed, "
                f"{VOLUME_METRICS['projects_canceled_percent']}% canceled, {VOLUME_METRICS['projects_work_in_progress_percent']}% work in progress. "
                f"Busier market shown: {VOLUME_METRICS['busiest_market']} ({VOLUME_METRICS['busiest_market_projects']}).")
    return "The attached workbook contains OU-level counts for artworks, SKUs, renders, repros, users, workflows and tasks. Ask for a specific metric or OU."

def list_ou_metrics(ou: str) -> str:
    target = ou.upper().replace(" ", "")
    aliases = {"EU":"EUOU","LATAM":"LATAMOU","AFRICA":"AOU","ASP":"ASPOU","EME":"EMEOU","NA":"NAOU","GCM":"GCMOU","JP":"JPOU","SK":"SKOU","INSWA":"INSWAOU"}
    target = aliases.get(target, target)
    for r in _report_records():
        if str(r["OU"]).upper() == target:
            return str(r)
    return f"OU '{ou}' was not found in the workbook."
