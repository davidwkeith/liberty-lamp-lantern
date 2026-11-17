"""Download the public-domain plate scans listed in stencils/sources/sources.json.

Scans aren't committed (several MB each); this re-creates them. Polite: one
request at a time with a pause, identifying user agent, skips existing files.
"""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "sources"
UA = "liberty-lamp-stencils/0.1 (personal non-commercial project; contact via GitHub)"

for name, meta in json.loads((SRC / "sources.json").read_text()).items():
    out = SRC / meta["file"]
    if out.exists():
        continue
    req = urllib.request.Request(meta["download"], headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 30 * 2**attempt
            print(f"{name}: rate limited, waiting {wait}s")
            time.sleep(wait)
    if not data.startswith(b"\xff\xd8"):
        raise SystemExit(f"{name}: not a JPEG")
    out.write_bytes(data)
    print(f"fetched {name} ({len(data) // 1024} KB) — {meta['license']}, {meta['page']}")
    time.sleep(20)
