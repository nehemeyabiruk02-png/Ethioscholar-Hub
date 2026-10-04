#!/usr/bin/env python3
from __future__ import annotations
import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data.json"

SOURCES = [
    {"name":"Open Scholarships","kind":"open_scholarships",
     "url":"https://scholarships.grudged.io/scholarships.json","license":"CC BY 4.0"},
    {"name":"WorqNow USA scholarships","kind":"worqnow",
     "url":"https://api.worqnow.ai/education/usa/scholarships","license":"Provider terms"},
    {"name":"WorqNow UK scholarships","kind":"worqnow",
     "url":"https://api.worqnow.ai/education/uk/scholarships","license":"Provider terms"},
    {"name":"WorqNow Canada scholarships","kind":"worqnow",
     "url":"https://api.worqnow.ai/education/ca/scholarships","license":"Provider terms"},
    {"name":"WorqNow Australia scholarships","kind":"worqnow",
     "url":"https://api.worqnow.ai/education/au/scholarships","license":"Provider terms"},
]

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent":"EthioScholar-Hub/21.0 automated refresh"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))

def clean(v):
    if v is None: return ""
    if isinstance(v, (list, dict)): return json.dumps(v, ensure_ascii=False)
    return str(v).strip()

def records_from(payload):
    if isinstance(payload, list): return payload
    if isinstance(payload, dict):
        for key in ("results", "scholarships", "data", "items"):
            if isinstance(payload.get(key), list): return payload[key]
    return []

def normalize(x, source):
    if not isinstance(x, dict): return None
    title = clean(x.get("title") or x.get("name") or x.get("scholarship_name") or x.get("program_name"))
    url = clean(x.get("url") or x.get("application_url") or x.get("official_url") or x.get("website") or x.get("link"))
    if not title or not re.match(r"^https?://", url, re.I): return None
    return {
        "id": re.sub(r"[^a-z0-9]+", "-", (title + "-" + url).lower()).strip("-")[:180],
        "title": title,
        "type": clean(x.get("type") or x.get("category") or "Scholarship"),
        "level": clean(x.get("level") or x.get("degree_level") or x.get("education_level") or "Not specified"),
        "funding": clean(x.get("funding") or x.get("funding_type") or x.get("award_type") or "Varies"),
        "field": clean(x.get("field") or x.get("fields") or x.get("study_area") or "All fields"),
        "destination": clean(x.get("destination") or x.get("country") or x.get("location") or "Various"),
        "availability": clean(x.get("availability") or x.get("status") or "unknown").lower(),
        "deadline": clean(x.get("deadline") or x.get("application_deadline") or ""),
        "provider": clean(x.get("provider") or x.get("sponsor") or x.get("organization") or "Source provider"),
        "url": url,
        "source": source,
        "verified": clean(x.get("verified") or x.get("verification") or "Source-provided"),
        "description": clean(x.get("description") or x.get("summary") or "")
    }

def main():
    all_records=[]; status={}; errors=[]; successful_sources=0
    for s in SOURCES:
        try:
            raw=records_from(get_json(s["url"]))
            good=[normalize(x,s["name"]) for x in raw]
            good=[x for x in good if x]
            all_records.extend(good)
            status[s["name"]]={"ok":True,"records":len(good)}
            successful_sources += 1
        except Exception as e:
            status[s["name"]]={"ok":False,"records":0}
            errors.append({"source":s["name"],"error":str(e)[:300]})

    # Never destroy a previously working dataset because a network/API is temporarily down.
    if successful_sources == 0:
        print("No source could be reached. Keeping the existing data.json unchanged.")
        print(json.dumps(errors, indent=2))
        return 0

    unique={}
    for r in all_records:
        unique.setdefault(r["url"].lower(),r)
    records=list(unique.values())
    packet={
        "schema_version":"21.0",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "record_count":len(records),
        "records":records,
        "sources":status,
        "errors":errors,
        "policy":"Only source-returned records with HTTP(S) URLs are imported. No synthetic scholarship records are generated."
    }
    OUT.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Wrote {len(records)} real source records from {successful_sources} reachable source(s).")
    if errors: print(json.dumps(errors,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
