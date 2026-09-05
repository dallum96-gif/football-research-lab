from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date, datetime, timezone
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import adaptive_dixon_coles as adc
import poisson_model
import query_lab


OUTCOMES = ("home_win", "draw", "away_win")


def _dt(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _number(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _identity_index() -> dict[tuple[str, str], dict]:
    output = {}
    for row in query_lab.load_identity_registry():
        if str(row.get("mapping_status") or "") != "VERIFIED":
            continue
        season = str(row.get("season") or "").strip()
        local_id = str(row.get("local_team_id") or "").strip()
        code = str(row.get("persistent_team_code") or "").strip()
        if season and local_id and code:
            output[(season, local_id)] = {
                "team_code": code,
                "name": str(row.get("canonical_name") or "").replace("_", " ").strip(),
            }
    return output


def _target_fixtures(season: str, target_date: date) -> list[dict]:
    identities = _identity_index()
    output = []
    for fixture in query_lab.load_fixtures():
        if str(fixture.get("season") or "") != season:
            continue
        kickoff = _dt(fixture.get("kickoff_time"))
        if kickoff is None or kickoff.date() != target_date:
            continue
        home = identities.get((season, str(fixture.get("home_team_id") or "")))
        away = identities.get((season, str(fixture.get("away_team_id") or "")))
        if home is None or away is None:
            continue
        output.append({
            "season": season,
            "fixture_id": str(fixture.get("fixture_id") or ""),
            "kickoff": kickoff,
            "kickoff_time": fixture.get("kickoff_time"),
            "home_team_code": home["team_code"],
            "away_team_code": away["team_code"],
            "home_team": home["name"],
            "away_team": away["name"],
            "repo_home_score": _number(fixture.get("home_score")),
            "repo_away_score": _number(fixture.get("away_score")),
        })
    output.sort(key=lambda row: (row["kickoff"], int(row["fixture_id"])))
    return output


def _fit_to_cutoff(config: adc.AdaptiveDCConfig, season: str, cutoff: datetime) -> adc.OnlineDixonColes:
    seasons = tuple(adc.DEFAULT_SEASONS) + ((season,) if season not in adc.DEFAULT_SEASONS else tuple())
    completed = [row for row in adc.canonical_completed_fixtures(seasons) if row["kickoff"] < cutoff]
    model = adc.OnlineDixonColes(config)
    for kickoff, grouped in groupby(completed, key=lambda row: row["kickoff"]):
        batch = list(grouped)
        model.advance_time(kickoff)
        for fixture in batch:
            model.update(
                fixture["home_team_code"],
                fixture["away_team_code"],
                fixture["home_goals"],
                fixture["away_goals"],
            )
    return model


def _most_likely_score(home_lambda: float, away_lambda: float, rho: float) -> tuple[int, int, float]:
    matrix = adc.dixon_coles_score_matrix(home_lambda, away_lambda, rho)
    (home_goals, away_goals), probability = max(matrix.items(), key=lambda item: item[1])
    return home_goals, away_goals, float(probability)


def forecast(season: str, target_date: date) -> dict:
    fixtures = _target_fixtures(season, target_date)
    if not fixtures:
        raise ValueError(f"No canonical {season} fixtures found on {target_date.isoformat()}.")

    selection = adc.select_development_config()
    config = selection["selected"]
    cutoff = min(row["kickoff"] for row in fixtures)
    model = _fit_to_cutoff(config, season, cutoff)

    rows = []
    for kickoff, grouped in groupby(fixtures, key=lambda row: row["kickoff"]):
        batch = list(grouped)
        model.advance_time(kickoff)
        for fixture in batch:
            prediction = model.predict(fixture["home_team_code"], fixture["away_team_code"])
            probabilities = prediction["probabilities"]
            expected = prediction["expected_goals"]
            score_home, score_away, score_probability = _most_likely_score(
                float(expected["home"]), float(expected["away"]), float(prediction["rho"])
            )
            predicted_outcome = max(OUTCOMES, key=lambda outcome: float(probabilities[outcome]))
            rows.append({
                "season": season,
                "fixture_id": fixture["fixture_id"],
                "kickoff_time": fixture["kickoff_time"],
                "home_team": fixture["home_team"],
                "away_team": fixture["away_team"],
                "home_win": float(probabilities["home_win"]),
                "draw": float(probabilities["draw"]),
                "away_win": float(probabilities["away_win"]),
                "predicted_outcome": predicted_outcome,
                "expected_home_goals": float(expected["home"]),
                "expected_away_goals": float(expected["away"]),
                "most_likely_score": [score_home, score_away],
                "most_likely_score_probability": score_probability,
                "rho": float(prediction["rho"]),
                "home_prior_matches": int(prediction["home_prior_matches"]),
                "away_prior_matches": int(prediction["away_prior_matches"]),
                "home_representation": prediction["home_representation"],
                "away_representation": prediction["away_representation"],
                "repo_result_at_forecast": (
                    None
                    if fixture["repo_home_score"] is None or fixture["repo_away_score"] is None
                    else [int(fixture["repo_home_score"]), int(fixture["repo_away_score"])]
                ),
            })

    return {
        "forecast_id": f"ADAPTIVE_DIXON_COLES_V1_SLATE_{target_date.isoformat()}",
        "status": "PRE_MATCH_RESEARCH_FORECAST",
        "model": adc.MODEL_VERSION,
        "selected_config": config.key,
        "season": season,
        "date_utc": target_date.isoformat(),
        "training_cutoff": cutoff.isoformat(),
        "training_rule": "Only canonical completed fixtures strictly before the first target-slate kickoff are fitted; target-date results are never consumed.",
        "fixture_count": len(rows),
        "rows": rows,
        "claims": {
            "trusted_model": "NO",
            "betting_edge": "NONE",
            "market_prices_used": False,
        },
    }


def _pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def render_html(report: dict) -> str:
    cards = []
    labels = {"home_win": "HOME", "draw": "DRAW", "away_win": "AWAY"}
    for row in report["rows"]:
        predicted = labels[row["predicted_outcome"]]
        home_p = 100.0 * row["home_win"]
        draw_p = 100.0 * row["draw"]
        away_p = 100.0 * row["away_win"]
        score = row["most_likely_score"]
        cards.append(f"""
        <article class="match">
          <div class="teams"><strong>{html.escape(row['home_team'])}</strong><span>v</span><strong>{html.escape(row['away_team'])}</strong></div>
          <div class="meta">Fixture {html.escape(row['fixture_id'])} · {html.escape(row['kickoff_time'])} · model lean <b>{predicted}</b></div>
          <div class="bars">
            <div><span>H {_pct(row['home_win'])}</span><i style="width:{home_p:.2f}%"></i></div>
            <div><span>D {_pct(row['draw'])}</span><i style="width:{draw_p:.2f}%"></i></div>
            <div><span>A {_pct(row['away_win'])}</span><i style="width:{away_p:.2f}%"></i></div>
          </div>
          <div class="footer">xG forecast {row['expected_home_goals']:.2f}–{row['expected_away_goals']:.2f} · modal score {score[0]}–{score[1]} ({_pct(row['most_likely_score_probability'])})</div>
        </article>
        """)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FRL Adaptive DC slate {html.escape(report['date_utc'])}</title>
<style>
body{{font-family:Inter,system-ui,sans-serif;background:#f4efe4;color:#24231f;margin:0;padding:28px}}
main{{max-width:920px;margin:auto}}h1{{font-size:28px;margin:0 0 6px}}.sub{{color:#6d685e;margin-bottom:22px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}}.match{{background:#fffaf0;border:1px solid #d8cfbf;border-radius:14px;padding:16px}}
.teams{{display:flex;justify-content:space-between;gap:10px;font-size:17px;align-items:center}}.teams span{{color:#8b8377}}.meta,.footer{{font-size:12px;color:#70695f;margin-top:9px}}
.bars{{margin-top:14px;display:grid;gap:7px}}.bars div{{height:24px;background:#e8e0d3;border-radius:8px;position:relative;overflow:hidden}}.bars i{{display:block;height:100%;background:#b86f55;opacity:.72}}
.bars span{{position:absolute;z-index:2;left:8px;top:4px;font-size:12px;font-weight:700}}.note{{margin-top:18px;font-size:12px;color:#70695f}}
</style>
</head>
<body><main>
<h1>FRL Adaptive Dixon–Coles · {html.escape(report['date_utc'])}</h1>
<div class="sub">Frozen pre-slate research forecast · {report['fixture_count']} fixtures · no market prices used</div>
<div class="grid">{''.join(cards)}</div>
<div class="note">Training cutoff: {html.escape(report['training_cutoff'])}. This is experimental research output, not a trusted-model or betting-edge claim.</div>
</main></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Forecast a dated Premier League slate with frozen Adaptive Dixon-Coles V1.")
    parser.add_argument("--season", default="2026-27")
    parser.add_argument("--date", required=True, help="UTC calendar date, YYYY-MM-DD")
    parser.add_argument("--output-dir", default=str(ROOT / "artifacts" / "forecast_snapshots"))
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date)
    report = forecast(args.season, target_date)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"adaptive_dc_{args.season}_{args.date}.json"
    html_path = output_dir / f"adaptive_dc_{args.season}_{args.date}.html"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")

    print("FRL ADAPTIVE DIXON-COLES V1 PRE-MATCH SLATE")
    print(f"season={report['season']}")
    print(f"date={report['date_utc']}")
    print(f"training_cutoff={report['training_cutoff']}")
    print(f"fixtures={report['fixture_count']}")
    for row in report["rows"]:
        score = row["most_likely_score"]
        print(
            f"fixture={row['fixture_id']} | {row['home_team']} v {row['away_team']} | "
            f"H={_pct(row['home_win'])} D={_pct(row['draw'])} A={_pct(row['away_win'])} | "
            f"xG={row['expected_home_goals']:.2f}-{row['expected_away_goals']:.2f} | "
            f"modal={score[0]}-{score[1]}"
        )
    print(f"json={json_path}")
    print(f"html={html_path}")


if __name__ == "__main__":
    main()
