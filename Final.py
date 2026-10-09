"""Download ISTAT road-accident data (dataflow 41_983) in year chunks, with cache and retry.

Usage:  python src/fetch_istat.py            # download missing chunks + metadata
        python src/fetch_istat.py --force    # re-download everything
"""
import argparse
import time
from collections import deque
from pathlib import Path

import pandas as pd
import requests

BASE = "https://esploradati.istat.it/SDMXWS/rest"
DATAFLOW = "41_983"
RAW_DIR = Path(__file__).resolve().parents[0] / "data" / "raw" / "istat"

# Year chunks: adjust once you know the real time coverage (see metadata file).
CHUNKS = [(2015, 2017), (2018, 2020), (2021, 2023), (2024, 2026)]

HEADERS_CSV = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}
TIMEOUT = (30, 3 * 3600)        # connect 30s, read up to 3h (server is slow)
MAX_REQ_PER_MIN = 3             # ISTAT blocks after 5/min for 24-48h: stay well below
MAX_ATTEMPTS = 6
BACKOFF = [60, 120, 300, 600, 900]  # seconds between retries

_sent = deque()


def _throttle():
    """Sliding-window limiter: never more than MAX_REQ_PER_MIN requests in 60s."""
    while _sent and time.time() - _sent[0] > 60:
        _sent.popleft()
    if len(_sent) >= MAX_REQ_PER_MIN:
        wait = 60 - (time.time() - _sent[0]) + 5
        print(f"  rate limiter: waiting {wait:.0f}s")
        time.sleep(wait)
    _sent.append(time.time())


def get(url, headers=None, params=None):
    """GET with throttling and retry. Returns Response, or None if 404 (no data)."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _throttle()
        t0 = time.time()
        print(f"  attempt {attempt}: {url} {params or ''}")
        try:
            r = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
            print(f"  -> HTTP {r.status_code} in {time.time() - t0:.0f}s")
            if r.status_code == 200:
                return r
            if r.status_code == 404:          # SDMX "NoRecordsFound"
                return None
            if r.status_code == 429:          # rate limited: stop, don't make it worse
                raise SystemExit("Rate limited (429). Stop and retry in 24-48h.")
        except requests.RequestException as e:
            print(f"  -> error after {time.time() - t0:.0f}s: {e}")
        if attempt < MAX_ATTEMPTS:
            wait = BACKOFF[min(attempt - 1, len(BACKOFF) - 1)]
            print(f"  retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {MAX_ATTEMPTS} attempts: {url}")


def save(path, content):
    tmp = path.with_suffix(path.suffix + ".part")   # atomic write: no half files in cache
    tmp.write_bytes(content)
    tmp.replace(path)


def fetch_metadata(force=False):
    """Dataflow + DSD + codelists (meaning of DATA_TYPE, REF_AREA, ...). One request."""
    path = RAW_DIR / "metadata_41_983.xml"
    if path.exists() and not force:
        print(f"cached: {path.name}")
        return
    r = get(f"{BASE}/dataflow/IT1/{DATAFLOW}/latest", params={"references": "all"})
    if r is not None:
        save(path, r.content)


def fetch_chunks(force=False):
    for start, end in CHUNKS:
        path = RAW_DIR / f"accidents_{start}_{end}.csv"
        empty = path.with_suffix(".empty")
        if (path.exists() or empty.exists()) and not force:
            print(f"cached: {path.name}")
            continue
        print(f"fetching {start}-{end}")
        r = get(f"{BASE}/data/{DATAFLOW}", headers=HEADERS_CSV,
                params={"startPeriod": start, "endPeriod": end})
        if r is None:
            empty.touch()                     # remember "no data" to avoid re-asking
            print("  no data for this period")
        else:
            save(path, r.content)


def combine():
    files = sorted(RAW_DIR.glob("accidents_*.csv"))
    df = pd.concat((pd.read_csv(f, dtype=str) for f in files), ignore_index=True)
    df = df.drop_duplicates()
    out = RAW_DIR.parent / "istat_accidents_all.csv"
    df.to_csv(out, index=False)
    print(f"combined {len(files)} chunks -> {out.name} ({len(df):,} rows)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fetch_metadata(args.force)
    fetch_chunks(args.force)
    combine()