#!/usr/bin/env python3
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
import platform
import getpass

# ---------- Resolve a writable base dir ----------
def resolve_base_dir():
    # 1) Prefer USERPROFILE on Windows (avoids weird ~ for elevated sessions)
    candidates = []
    if os.name == "nt":
        up = os.environ.get("USERPROFILE")
        if up: candidates.append(Path(up) / "ArrivalLog")
        candidates.append(Path("C:/Users/Public/ArrivalLog"))
    # 2) Fallback to expanduser("~")
    candidates.append(Path(Path.home()) / "ArrivalLog")
    # 3) Last resort: script directory
    script_dir = Path(__file__).resolve().parent
    candidates.append(script_dir / "ArrivalLog")

    for d in candidates:
        try:
            d.mkdir(parents=True, exist_ok=True)
            # quick write test
            (d / ".touch").write_text("ok", encoding="utf-8")
            (d / ".touch").unlink(missing_ok=True)
            return d
        except Exception:
            continue
    # if everything fails, raise
    raise RuntimeError("No writable directory found for ArrivalLog")

def ensure_header(path: Path):
    if not path.exists():
        path.write_text("Date,Time,ISO,User,Machine,Status,Color\n", encoding="utf-8")

def classify(now: datetime):
    T_OK_MAX   = (8, 50)  # < 08:50 => OK
    T_WARN_MAX = (9,  0)  # < 09:00 => WARNING, else ERROR
    hhmm = (now.hour, now.minute)
    if hhmm < T_OK_MAX:
        return "OK", "Green"
    elif hhmm < T_WARN_MAX:
        return "WARNING", "Yellow"
    else:
        return "ERROR", "Red"

def get_user():
    try:
        return os.getlogin()
    except Exception:
        try:
            return getpass.getuser()
        except Exception:
            return "unknown"

def log_arrival(base_dir: Path, now: datetime):
    year_path = base_dir / f"arrival_{now.year}.csv"
    ensure_header(year_path)
    status, color = classify(now)
    user = get_user()
    machine = os.environ.get("COMPUTERNAME", platform.node())
    row = f"{now:%Y-%m-%d},{now:%H:%M:%S},{now.isoformat(timespec='seconds')},{user},{machine},{status},{color}\n"
    with year_path.open("a", encoding="utf-8") as f:
        f.write(row)
    return year_path

def report_2025_2030(base_dir: Path):
    print("Date,Time,ISO,User,Machine,Status,Color")
    for y in range(2025, 2031):
        fp = base_dir / f"arrival_{y}.csv"
        if not fp.exists():
            continue
        for line in fp.read_text(encoding="utf-8").splitlines():
            if line.startswith("Date,"):  # skip header
                continue
            print(line)

def diag(base_dir: Path):
    now = datetime.now()
    print("[DIAG] Python:", sys.executable)
    print("[DIAG] Platform:", platform.platform())
    print("[DIAG] User HOME:", str(Path.home()))
    print("[DIAG] Base dir:", str(base_dir))
    target = base_dir / f"arrival_{now.year}.csv"
    print("[DIAG] Target file:", str(target))

def main():
    # pick a reliable directory
    base_dir = resolve_base_dir()

    # modes
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report_2025_2030(base_dir)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--diag":
        diag(base_dir)
        return

    # default = log once
    now = datetime.now()
    year_path = log_arrival(base_dir, now)
    # optional minimal console hint (won't break scheduler)
    print(str(year_path))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # write a local error log next to script so you actually see failures
        errlog = Path(__file__).resolve().with_name("arrival_error.log")
        with errlog.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {type(e).__name__}: {e}\n")
        raise
