"""Build complete FPL fixture evidence from the approved upstream CSVs."""
from __future__ import annotations
import argparse,csv,os
from pathlib import Path

UPSTREAM_ROOT=Path(r"C:\Users\dlall\football_database\Premier-League-Stats\fpl_scraper\fpl_stats")
ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"data"/"fpl_fixture_evidence.csv"
AUDIT=ROOT/"data"/"fpl_fixture_evidence_build_audit.csv"

def read_csv(path):
    for enc in ("utf-8-sig","cp1252","latin-1"):
        try:
            with open(path,"r",encoding=enc,newline="") as h:
                r=csv.DictReader(h); return list(r),r.fieldnames or []
        except UnicodeDecodeError: pass
    raise ValueError(f"Could not decode CSV: {path}")

def build(season):
    path=UPSTREAM_ROOT/"fixtures"/f"{season}_all_fixtures.csv"
    if not path.is_file(): raise FileNotFoundError(f"Approved FPL fixture source not found: {path}")
    rows,fields=read_csv(path); evidence=[]; audit=[]; seen=set()
    for row in rows:
        key=(season,str(row.get("id",row.get("fixture_id",""))).strip())
        if key in seen:
            audit.append({"status":"DUPLICATE_SOURCE_ROW","source_file":str(path),"fixture_key":key[1],"reason":"Duplicate FPL fixture key"}); continue
        seen.add(key)
        out={"frl_season":season,"frl_fpl_fixture_key":key[1],"frl_fpl_source_file":str(path)}
        for f,v in row.items(): out[f"source_{f}"]=v
        evidence.append(out)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); tmp=OUTPUT.with_suffix(".tmp.csv"); ta=AUDIT.with_suffix(".tmp.csv")
    cols=list(evidence[0]) if evidence else []
    with open(tmp,"w",encoding="utf-8-sig",newline="") as h:
        w=csv.DictWriter(h,fieldnames=cols,extrasaction="ignore"); w.writeheader(); w.writerows(evidence)
    with open(ta,"w",encoding="utf-8-sig",newline="") as h:
        w=csv.DictWriter(h,fieldnames=["status","source_file","fixture_key","reason"]); w.writeheader(); w.writerows(audit)
    os.replace(tmp,OUTPUT); os.replace(ta,AUDIT)
    issues=sum(r["status"]!="RESOLVED" for r in audit)
    return len(evidence),len(fields),issues

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--season",required=True); a=p.parse_args()
    rows,fields,issues=build(a.season)
    print(f"FPL FIXTURE EVIDENCE: {rows} rows written"); print(f"SOURCE NATIVE FIELDS: {fields}"); print(f"DUPLICATE/ERROR STATES: {issues}"); print(f"Output: {OUTPUT}"); print(f"Audit: {AUDIT}")
    if issues: raise SystemExit(1)
