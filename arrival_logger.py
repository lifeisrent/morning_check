#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from pathlib import Path

# ---------- choose a writable base dir ----------
def resolve_base_dir() -> Path:
    candidates = []
    if os.name == "nt":
        up = os.environ.get("USERPROFILE")
        if up:
            candidates.append(Path(up) / "ArrivalLog")
        candidates.append(Path("C:/Users/Public/ArrivalLog"))
    candidates.append(Path.home() / "ArrivalLog")
    candidates.append(Path(__file__).resolve().parent / "ArrivalLog")

    for d in candidates:
        try:
            d.mkdir(parents=True, exist_ok=True)
            tmp = d / ".touch"
            tmp.write_text("ok", encoding="utf-8")
            tmp.unlink(missing_ok=True)
            return d
        except Exception:
            continue
    raise RuntimeError("No writable directory found for ArrivalLog")

def ensure_header(path: Path):
    if not path.exists():
        path.write_text("Date,Time,User,Status,Color\n", encoding="utf-8")  # ISO/Machine removed

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

def log_arrival(base_dir: Path, now: datetime) -> Path:
    year_path = base_dir / f"arrival_{now.year}.csv"
    ensure_header(year_path)
    status, color = classify(now)
    user = "smlee"  # hard-coded user
    row = f"{now:%Y-%m-%d},{now:%H:%M:%S},{user},{status},{color}\n"  # ISO/Machine removed
    with year_path.open("a", encoding="utf-8") as f:
        f.write(row)
    return year_path

def report_2025_2030(base_dir: Path):
    print("Date,Time,User,Status,Color")  # header updated
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
    print("[DIAG] User HOME:", str(Path.home()))
    print("[DIAG] Base dir:", str(base_dir))
    print("[DIAG] Target file:", str(base_dir / f"arrival_{now.year}.csv"))

def main():
    base_dir = resolve_base_dir()

    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        report_2025_2030(base_dir)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--diag":
        diag(base_dir)
        return

    year_path = log_arrival(base_dir, datetime.now())
    print(str(year_path))  # minimal hint

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        errlog = Path(__file__).resolve().with_name("arrival_error.log")
        with errlog.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {type(e).__name__}: {e}\n")
        raise

#