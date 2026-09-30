"""Run the local synthetic pipeline; record actual stage receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


if __name__ == "__main__":
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", MPLCONFIGDIR=str(ROOT / ".mplconfig"))
    stages = [("prepare.py", []), ("analyze.py", []), ("figure.py", ["--export"]), ("verify.py", [])]
    for filename, args in stages:
        command = [sys.executable, str(ROOT / filename), *args]
        started = datetime.now(timezone.utc).isoformat()
        clock = time.perf_counter()
        run = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        output_path = ROOT / f"{Path(filename).stem}.execution.log"
        output_path.write_text(run.stdout + run.stderr)
        record = {"started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                  "duration_seconds": time.perf_counter() - clock, "command": command,
                  "exit_code": run.returncode, "log": str(output_path),
                  "code_sha256": hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()}
        with (ROOT / "execution_log.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps(record) + "\n")
        print(json.dumps({"stage": filename, "exit_code": run.returncode,
                          "duration_seconds": record["duration_seconds"]}))
        if run.returncode:
            print(run.stdout + run.stderr)
            raise SystemExit(run.returncode)
