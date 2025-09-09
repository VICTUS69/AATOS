# dashboard/app.py
import os
from flask import Flask, render_template, jsonify, request
import pandas as pd
from datetime import datetime

app = Flask(__name__, template_folder="templates")

# --- CONFIG: adjust via env var DATA_CSV or leave as default ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # repo root
DEFAULT_CANDIDATES = [
    os.environ.get("DATA_CSV"),
    os.path.join(BASE_DIR, "data", "Banglore_traffic_Dataset.csv"),
    os.path.join(BASE_DIR, "data", "Bangalore_traffic_Dataset.csv"),
    os.path.join(BASE_DIR, "Banglore_traffic_Dataset.csv"),
    os.path.join(BASE_DIR, "Bangalore_traffic_Dataset.csv"),
]
CSV_PATH = next((p for p in DEFAULT_CANDIDATES if p and os.path.exists(p)), None)

# friendly constants for computation
BASE_GREEN = 20  # base green seconds
SCALING_FACTOR = 300.0

def find_csv_path():
    if CSV_PATH:
        return CSV_PATH
    # if not auto-found, attempt to check env var again
    env = os.environ.get("DATA_CSV")
    if env and os.path.exists(env):
        return env
    return None

def compute_green_time_from_count(count, min_green=10, max_green=120):
    g = BASE_GREEN + (count / SCALING_FACTOR)
    g = max(min_green, min(max_green, g))
    return int(round(g))

def safe_load_df(path):
    try:
        df = pd.read_csv(path, parse_dates=["Date"], infer_datetime_format=True)
    except Exception:
        # fallback - no parse
        df = pd.read_csv(path)
    return df

def create_summary(df):
    # ensure important columns exist with forgiving names
    col_map = {c.lower(): c for c in df.columns}
    # try common column names
    vol_col = col_map.get("traffic volume", col_map.get("traffic_volume", "Traffic Volume"))
    speed_col = col_map.get("average speed", col_map.get("average_speed", "Average Speed"))
    cong_col = col_map.get("congestion level", col_map.get("congestion_level", "Congestion Level"))
    incident_col = col_map.get("incident reports", col_map.get("incident_reports", "Incident Reports"))
    loc_col = col_map.get("road/intersection name", col_map.get("road_intersection name", "Road/Intersection Name"))
    # fallback to Area Name if Road/Intersection missing
    if loc_col not in df.columns:
        loc_col = col_map.get("area name", "Area Name")

    # fill missing columns gracefully
    if vol_col not in df.columns:
        df[vol_col] = 0
    if speed_col not in df.columns:
        df[speed_col] = 0.0
    if cong_col not in df.columns:
        df[cong_col] = 0.0
    if incident_col not in df.columns:
        df[incident_col] = 0

    agg = df.groupby(loc_col).agg(
        total_traffic = (vol_col, "sum"),
        avg_speed = (speed_col, "mean"),
        avg_congestion = (cong_col, "mean"),
        incidents = (incident_col, "sum")
    ).reset_index().rename(columns={loc_col: "location"})

    # compute suggested green times (split heuristically into NS/EW)
    def compute_row_greens(row):
        tot = row["total_traffic"]
        # normalize to a per-interval number — for demo we don't need time units exact
        ns = int(tot * 0.6)
        ew = int(tot - ns)
        return {
            "ns_green": compute_green_time_from_count(ns),
            "ew_green": compute_green_time_from_count(ew)
        }

    greens = agg.apply(lambda r: compute_row_greens(r), axis=1)
    agg["ns_green_s"] = [g["ns_green"] for g in greens]
    agg["ew_green_s"] = [g["ew_green"] for g in greens]

    # alert flag if incidents > 0
    agg["alert"] = agg["incidents"].apply(lambda x: f"{int(x)} reported" if x>0 else "")
    # round numeric columns
    agg["avg_speed"] = agg["avg_speed"].round(2)
    agg["avg_congestion"] = agg["avg_congestion"].round(2)
    agg["total_traffic"] = agg["total_traffic"].astype(int)
    return agg.sort_values(by="avg_congestion", ascending=False)

@app.route("/")
def index():
    csv = find_csv_path()
    missing = csv is None
    return render_template("index.html", csv_found=not missing)

@app.route("/api/summary")
def api_summary():
    csv = find_csv_path()
    if not csv:
        return jsonify({"error":"dataset not found. Set DATA_CSV env var or place CSV under repo/data/ with expected filename."}), 400
    df = safe_load_df(csv)
    summary = create_summary(df)
    # return top 50 as list of dicts
    return jsonify(summary.head(50).to_dict(orient="records"))

@app.route("/api/location")
def api_location():
    """
    Query param: ?name=LOCATION_NAME
    Returns timeseries (date, traffic volume, avg speed, congestion)
    """
    name = request.args.get("name")
    if not name:
        return jsonify({"error":"please supply ?name=LOCATION_NAME"}), 400
    csv = find_csv_path()
    if not csv:
        return jsonify({"error":"dataset not found"}), 400
    df = safe_load_df(csv)
    # columns tolerant mapping similar to create_summary
    col_map = {c.lower(): c for c in df.columns}
    vol_col = col_map.get("traffic volume", "Traffic Volume")
    speed_col = col_map.get("average speed", "Average Speed")
    cong_col = col_map.get("congestion level", "Congestion Level")
    loc_col = col_map.get("road/intersection name", "Road/Intersection Name")
    if loc_col not in df.columns:
        loc_col = "Area Name"
    # filter rows
    sel = df[df[loc_col].astype(str).str.lower() == name.strip().lower()]
    if sel.empty:
        # try partial match
        sel = df[df[loc_col].astype(str).str.lower().str.contains(name.strip().lower())]
    if sel.empty:
        return jsonify({"error": "no rows found for that location"}), 404
    # ensure Date exists (try to coerce)
    if "Date" in sel.columns:
        try:
            sel["Date"] = pd.to_datetime(sel["Date"])
        except Exception:
            pass
    # return a simple series
    times = []
    for _, r in sel.iterrows():
        times.append({
            "date": str(r["Date"]) if "Date" in r and pd.notna(r["Date"]) else "",
            "traffic_volume": int(r.get(vol_col, 0)) if pd.notna(r.get(vol_col, 0)) else 0,
            "avg_speed": float(r.get(speed_col, 0.0)) if pd.notna(r.get(speed_col, 0.0)) else 0.0,
            "congestion": float(r.get(cong_col, 0.0)) if pd.notna(r.get(cong_col, 0.0)) else 0.0
        })
    return jsonify(times[:500])  # cap size for safety

if __name__ == "__main__":
    # allow overriding host/port via env vars
    host = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.environ.get("DASHBOARD_PORT", "5000"))
    debug = os.environ.get("DASHBOARD_DEBUG", "1") == "1"
    print("Starting dashboard. CSV autodetect:", CSV_PATH)
    app.run(host=host, port=port, debug=debug)
