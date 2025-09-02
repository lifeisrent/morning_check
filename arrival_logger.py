#!/usr/bin/env python3
import os
from datetime import datetime

# === Configuration ===
BASE_DIR = os.path.join(os.path.expanduser("~"), "ArrivalLog")   # Default save folder: User home/ArrivalLog
FNAME = f"arrival_{datetime.now().year}.csv"                     # Yearly file
PATH = os.path.join(BASE_DIR, FNAME)

# Threshold times (24h format)
T_OK_MAX   = (8, 50)   # Before 08:50 → OK
T_WARN_MAX = (9, 0)    # Before 09:00 → WARNING, otherwise ERROR

def ensure_dir_and_header():
    os.makedirs(BASE_DIR, exist_ok=True)
    if not os.path.exists(PATH):
        with open(PATH, "w", encoding="utf-8") as f:
            f.write("Date,Time,ISO,User,Machine,Status,Color\n")

def classify(now: datetime):
    hhmm = (now.hour, now.minute)
    if hhmm < T_OK_MAX:
        return "OK", "Green"
    elif hhmm < T_WARN_MAX:
        return "WARNING", "Yellow"
    else:
        return "ERROR", "Red"

def main():
    now = datetime.now()  # System local time
    status, color = classify(now)
    ensure_dir_and_header()
    try:
        user = os.getlogin()
    except Exception:
        user = "unknown"
    row = f"{now:%Y-%m-%d},{now:%H:%M:%S},{now.isoformat(timespec='seconds')},{user},{os.environ.get('COMPUTERNAME','')},{status},{color}\n"
    with open(PATH, "a", encoding="utf-8") as f:
        f.write(row)

# Optional report mode
import csv
import sys

def report_2025_2030():
    base = os.path.join(os.path.expanduser("~"), "ArrivalLog")
    years = range(2025, 2031)
    rows = []
    for y in years:
        p = os.path.join(base, f"arrival_{y}.csv")
        if not os.path.exists(p):
            continue
        with open(p, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            rows.extend(r)

    print("Date,Time,ISO,User,Machine,Status,Color")
    for r in rows:
        print(f"{r['Date']},{r['Time']},{r['ISO']},{r['User']},{r['Machine']},{r['Status']},{r['Color']}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report_2025_2030()
    else:
        main()
