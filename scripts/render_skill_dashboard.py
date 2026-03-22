#!/usr/bin/env python3
"""Render a stock-board style skill telemetry dashboard."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from render_skill_report import DEFAULT_INPUTS, avg, load_runs_from_path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML_OUTPUT = REPO_ROOT / "telemetry" / "skill-dashboard.html"
DEFAULT_JSON_OUTPUT = REPO_ROOT / "telemetry" / "skill-dashboard.json"
OUTCOME_SCORES = {
    "success": 1.0,
    "partial": 0.55,
    "failed": 0.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a ranked skill telemetry dashboard as HTML plus JSON."
    )
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="Repeatable input JSONL path. If omitted, uses existing local telemetry logs.",
    )
    parser.add_argument("--html-output", default=str(DEFAULT_HTML_OUTPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    return parser.parse_args()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def get_input_paths(raw_inputs: list[str]) -> list[Path]:
    if raw_inputs:
        return [Path(item).expanduser().resolve() for item in raw_inputs]
    return [path.resolve() for path in DEFAULT_INPUTS if path.exists()]


def load_runs(paths: list[Path]) -> list[dict]:
    runs = []
    for path in paths:
        if not path.exists():
            raise SystemExit(f"Input log does not exist: {path}")
        runs.extend(load_runs_from_path(path))
    if not runs:
        raise SystemExit("No runs found in the provided telemetry logs.")
    runs.sort(key=lambda item: item["timestamp"])
    return runs


def daily_window(end_day: datetime, days: int) -> list[datetime]:
    start = end_day - timedelta(days=days - 1)
    return [start + timedelta(days=offset) for offset in range(days)]


def normalize_delta(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def classify_move(delta_count: int, efficiency: float, delivery: float) -> str:
    if delta_count >= 3 and efficiency >= 85:
        return "surging"
    if delta_count > 0:
        return "rising"
    if delta_count < 0:
        return "cooling"
    if delivery >= 90:
        return "steady"
    return "watch"


def build_dashboard_payload(runs: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    run_times = [parse_ts(run["timestamp"]) for run in runs]
    last_run_at = max(run_times)
    board_end_day = datetime.combine(last_run_at.date(), datetime.min.time(), tzinfo=timezone.utc)
    days_30 = daily_window(board_end_day, 30)
    days_21 = daily_window(board_end_day, 21)
    days_14 = daily_window(board_end_day, 14)
    current_7_start = board_end_day - timedelta(days=6)
    previous_7_start = board_end_day - timedelta(days=13)
    previous_7_end = board_end_day - timedelta(days=7)

    skill_runs: dict[str, list[dict]] = defaultdict(list)
    challenge_counts: Counter[str] = Counter()
    challenge_skills: dict[str, set[str]] = defaultdict(set)
    recent_runs: list[dict] = []

    for run in runs:
        ts = parse_ts(run["timestamp"])
        run["_dt"] = ts
        recent_runs.append(run)
        for skill in run.get("skills", []):
            skill_runs[skill].append(run)
        for challenge in run.get("challenge_tags", []):
            challenge_counts[challenge] += 1
            for skill in run.get("skills", []):
                challenge_skills[challenge].add(skill)

    total_runs = len(runs)
    total_skills = len(skill_runs)
    active_7d_runs = sum(1 for run in runs if run["_dt"].date() >= current_7_start.date())

    entries = []
    for skill, items in skill_runs.items():
        items = sorted(items, key=lambda item: item["_dt"])
        total = len(items)
        current_7 = sum(1 for item in items if item["_dt"].date() >= current_7_start.date())
        previous_7 = sum(
            1
            for item in items
            if previous_7_start.date() <= item["_dt"].date() <= previous_7_end.date()
        )
        delta_count = current_7 - previous_7
        delta_pct = normalize_delta(current_7, previous_7)
        efficiency = avg([float(item["efficiency_score"]) for item in items])
        recent_efficiency = avg(
            [float(item["efficiency_score"]) for item in items if item["_dt"].date() >= current_7_start.date()]
        ) or efficiency
        delivery = avg([OUTCOME_SCORES.get(item["outcome"], 0.0) for item in items]) * 100
        friction = avg([float(item["friction_score"]) for item in items])
        duration = avg([float(item["duration_minutes"]) for item in items])
        last_seen = items[-1]["_dt"]
        daily_counts = Counter(item["_dt"].date().isoformat() for item in items)
        sparkline = [daily_counts.get(day.date().isoformat(), 0) for day in days_14]
        chart_series = [daily_counts.get(day.date().isoformat(), 0) for day in days_21]
        momentum = round(
            (delta_count * 8)
            + ((recent_efficiency - efficiency) * 0.8)
            + (delivery - 80) * 0.35
            - (friction * 2.4),
            1,
        )
        rank_score = round(
            (total * 1.4)
            + (current_7 * 4.8)
            + (efficiency * 0.48)
            + (delivery * 0.32)
            + max(delta_count, 0) * 5
            - (friction * 3.5)
            - (duration * 0.22),
            1,
        )
        entries.append(
            {
                "skill": skill,
                "total_runs": total,
                "runs_7d": current_7,
                "runs_prev_7d": previous_7,
                "delta_count": delta_count,
                "delta_pct": round(delta_pct, 1),
                "efficiency": round(efficiency, 1),
                "recent_efficiency": round(recent_efficiency, 1),
                "delivery": round(delivery, 1),
                "friction": round(friction, 1),
                "duration": round(duration, 1),
                "rank_score": rank_score,
                "momentum": momentum,
                "state": classify_move(delta_count, efficiency, delivery),
                "usage_share": round((total / total_runs) * 100, 1),
                "sparkline": sparkline,
                "chart_series": chart_series,
                "last_seen": iso(last_seen),
            }
        )

    entries.sort(key=lambda item: (-item["rank_score"], -item["runs_7d"], item["skill"]))
    for index, entry in enumerate(entries, start=1):
        entry["rank"] = index

    top_chart_skills = entries[:4]
    challenge_items = [
        {
            "challenge": challenge,
            "hits": count,
            "skills": sorted(challenge_skills[challenge]),
        }
        for challenge, count in challenge_counts.most_common(8)
    ]
    recent_items = [
        {
            "timestamp": run["timestamp"],
            "skills": run.get("skills", []),
            "outcome": run["outcome"],
            "efficiency": float(run["efficiency_score"]),
            "task": run["task"],
        }
        for run in sorted(recent_runs, key=lambda item: item["timestamp"], reverse=True)[:12]
    ]
    movers_up = sorted(entries, key=lambda item: (-item["delta_count"], -item["delta_pct"], -item["rank_score"]))[:6]
    movers_down = sorted(entries, key=lambda item: (item["delta_count"], item["delta_pct"], -item["rank_score"]))[:6]
    watchlist = sorted(
        entries,
        key=lambda item: (item["efficiency"] + item["delivery"] - item["friction"] * 18, item["rank_score"]),
    )[:6]

    payload = {
        "generated_at": iso(now),
        "last_run_at": iso(last_run_at),
        "window": {
            "chart_days": [day.date().isoformat() for day in days_21],
            "spark_days": [day.date().isoformat() for day in days_14],
        },
        "overview": {
            "total_runs": total_runs,
            "active_skills": total_skills,
            "runs_7d": active_7d_runs,
            "avg_efficiency": round(avg([float(run["efficiency_score"]) for run in runs]), 1),
            "avg_delivery": round(
                avg([OUTCOME_SCORES.get(run["outcome"], 0.0) for run in runs]) * 100, 1
            ),
            "leader": entries[0]["skill"] if entries else "n/a",
        },
        "skills": entries,
        "leaders": entries[:12],
        "chart_leaders": [
            {
                "skill": entry["skill"],
                "series": entry["chart_series"],
                "rank_score": entry["rank_score"],
            }
            for entry in top_chart_skills
        ],
        "movers_up": movers_up,
        "movers_down": movers_down,
        "watchlist": watchlist,
        "challenges": challenge_items,
        "recent_runs": recent_items,
    }
    return payload


def render_html(payload: dict) -> str:
    bootstrap_json = json.dumps(payload, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codex Skill Exchange</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2307101c'/%3E%3Cpath d='M14 43V21h8.5l7.1 12.6L36.7 21H45v22h-5.8V30.8l-7.1 12.1h-5L20 30.8V43Z' fill='%2356d7ff'/%3E%3C/svg%3E">
  <style>
    :root {{
      --bg: #06111f;
      --bg-soft: rgba(12, 28, 48, 0.82);
      --panel: rgba(9, 22, 38, 0.78);
      --panel-strong: rgba(6, 16, 30, 0.92);
      --line: rgba(110, 176, 255, 0.16);
      --cyan: #56d7ff;
      --cyan-soft: #83e5ff;
      --green: #49f2a5;
      --red: #ff5e7a;
      --amber: #ffc76a;
      --text: #edf6ff;
      --muted: #8ba5bf;
      --violet: #7d8bff;
      --pink: #d06cff;
      --glow: 0 0 32px rgba(86, 215, 255, 0.18);
    }}

    * {{ box-sizing: border-box; }}

    html, body {{
      margin: 0;
      min-height: 100%;
      background:
        radial-gradient(circle at top right, rgba(65, 118, 255, 0.22), transparent 30%),
        radial-gradient(circle at bottom left, rgba(73, 242, 165, 0.12), transparent 28%),
        linear-gradient(180deg, #07101c 0%, #040911 100%);
      color: var(--text);
      font-family: "Avenir Next", "IBM Plex Sans", "Segoe UI", sans-serif;
    }}

    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(98, 145, 215, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(98, 145, 215, 0.05) 1px, transparent 1px);
      background-size: 32px 32px;
      mask-image: linear-gradient(180deg, rgba(255,255,255,0.7), rgba(255,255,255,0.15));
    }}

    .shell {{
      max-width: 1540px;
      margin: 0 auto;
      padding: 28px;
    }}

    .masthead {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 22px;
      align-items: end;
      margin-bottom: 18px;
    }}

    .title-block {{
      padding: 18px 0 6px;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--cyan-soft);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.22em;
      margin-bottom: 12px;
    }}

    .pulse {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--green);
      box-shadow: 0 0 0 0 rgba(73, 242, 165, 0.55);
      animation: pulse 1.8s infinite;
    }}

    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(73, 242, 165, 0.55); }}
      70% {{ box-shadow: 0 0 0 16px rgba(73, 242, 165, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(73, 242, 165, 0); }}
    }}

    h1 {{
      margin: 0;
      font-size: clamp(2.4rem, 5vw, 4.6rem);
      letter-spacing: -0.05em;
      line-height: 0.95;
    }}

    .subtitle {{
      margin: 12px 0 0;
      max-width: 720px;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.5;
    }}

    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}

    .metric {{
      background: linear-gradient(180deg, rgba(18, 38, 63, 0.84), rgba(7, 15, 26, 0.94));
      border: 1px solid rgba(120, 180, 255, 0.12);
      padding: 16px 18px;
      min-height: 108px;
      box-shadow: var(--glow);
    }}

    .metric-label {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 11px;
    }}

    .metric-value {{
      margin-top: 14px;
      font-size: clamp(1.6rem, 3vw, 2.7rem);
      font-weight: 700;
      letter-spacing: -0.04em;
    }}

    .metric-note {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.86rem;
    }}

    .board {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(360px, 0.78fr);
      gap: 22px;
      align-items: start;
    }}

    .panel {{
      background: linear-gradient(180deg, var(--panel), var(--panel-strong));
      border: 1px solid rgba(120, 180, 255, 0.12);
      box-shadow: var(--glow);
      overflow: hidden;
    }}

    .panel-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 16px 18px;
      border-bottom: 1px solid rgba(120, 180, 255, 0.1);
    }}

    .panel-title {{
      font-size: 0.84rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--muted);
    }}

    .panel-value {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      color: var(--cyan-soft);
      font-size: 0.84rem;
    }}

    .hero-chart-wrap {{
      padding: 18px;
      min-height: 410px;
    }}

    .hero-chart {{
      width: 100%;
      height: 320px;
      display: block;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-top: 14px;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      font-size: 0.88rem;
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      box-shadow: 0 0 18px currentColor;
    }}

    .ticker-panel {{
      display: grid;
      gap: 0;
    }}

    .ticker-section {{
      padding: 16px 18px 18px;
      border-bottom: 1px solid rgba(120, 180, 255, 0.08);
    }}

    .ticker-section:last-child {{
      border-bottom: 0;
    }}

    .ticker-label {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-size: 0.74rem;
    }}

    .ticker-list {{
      display: grid;
      gap: 10px;
    }}

    .ticker-item {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      padding: 10px 0;
      border-bottom: 1px dashed rgba(120, 180, 255, 0.08);
      font-size: 0.93rem;
    }}

    .ticker-item:last-child {{
      border-bottom: 0;
      padding-bottom: 0;
    }}

    .ticker-main {{
      font-weight: 600;
    }}

    .ticker-sub {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.8rem;
    }}

    .delta {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      font-weight: 700;
      white-space: nowrap;
    }}

    .delta.up {{ color: var(--green); }}
    .delta.down {{ color: var(--red); }}
    .delta.flat {{ color: var(--amber); }}

    .lower-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.6fr) minmax(340px, 0.9fr);
      gap: 22px;
      margin-top: 22px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }}

    thead th {{
      text-align: left;
      padding: 12px 14px;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--muted);
      border-bottom: 1px solid rgba(120, 180, 255, 0.08);
    }}

    tbody td {{
      padding: 13px 14px;
      border-bottom: 1px solid rgba(120, 180, 255, 0.06);
      vertical-align: middle;
    }}

    tbody tr {{
      transition: background 160ms ease, transform 160ms ease;
    }}

    tbody tr:hover {{
      background: rgba(28, 58, 92, 0.28);
    }}

    .rank-cell {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      color: var(--cyan-soft);
      width: 52px;
    }}

    .skill-name {{
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .skill-state {{
      margin-top: 5px;
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--muted);
    }}

    .mono {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
    }}

    .spark {{
      width: 128px;
      height: 34px;
      display: block;
    }}

    .stack {{
      display: grid;
      gap: 18px;
    }}

    .compact-table tbody td {{
      padding: 11px 14px;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border: 1px solid rgba(120, 180, 255, 0.12);
      color: var(--muted);
      font-size: 0.74rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
    }}

    .tape {{
      display: grid;
      gap: 10px;
      padding: 18px;
    }}

    .tape-item {{
      display: grid;
      grid-template-columns: 150px minmax(0, 1fr) auto;
      gap: 14px;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px dashed rgba(120, 180, 255, 0.08);
    }}

    .tape-item:last-child {{
      border-bottom: 0;
      padding-bottom: 0;
    }}

    .tape-time {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      color: var(--muted);
      font-size: 0.82rem;
    }}

    .tape-task {{
      font-weight: 600;
    }}

    .tape-skills {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 0.8rem;
    }}

    .footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.82rem;
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
    }}

    @media (max-width: 1180px) {{
      .masthead,
      .board,
      .lower-grid {{
        grid-template-columns: 1fr;
      }}

      .meta-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 760px) {{
      .shell {{
        padding: 18px;
      }}

      .meta-grid {{
        grid-template-columns: 1fr;
      }}

      thead {{
        display: none;
      }}

      tbody tr,
      .tape-item {{
        display: block;
      }}

      tbody td {{
        display: block;
        padding: 8px 14px;
        border-bottom: 0;
      }}

      tbody tr {{
        border-bottom: 1px solid rgba(120, 180, 255, 0.08);
        padding: 8px 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="masthead">
      <div class="title-block">
        <div class="eyebrow"><span class="pulse"></span> live codex skill exchange</div>
        <h1>Skill Market Board</h1>
        <p class="subtitle">
          A live ranked view of skill usage, delivery quality, and momentum. Think of it as a terminal for which skills are carrying weight, which ones are heating up, and where the next upgrade pressure is building.
        </p>
      </div>
      <div class="meta-grid" id="metricGrid"></div>
    </section>

    <section class="board">
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title">Usage Momentum</div>
          <div class="panel-value" id="chartLabel">Tracking top skills across the last 21 days</div>
        </div>
        <div class="hero-chart-wrap">
          <svg class="hero-chart" id="heroChart" viewBox="0 0 960 320" preserveAspectRatio="none"></svg>
          <div class="legend" id="legend"></div>
        </div>
      </section>

      <aside class="panel ticker-panel">
        <section class="ticker-section">
          <div class="ticker-label"><span>Top Risers</span><span class="badge">7d flow</span></div>
          <div class="ticker-list" id="moversUp"></div>
        </section>
        <section class="ticker-section">
          <div class="ticker-label"><span>Cooling</span><span class="badge">watch</span></div>
          <div class="ticker-list" id="moversDown"></div>
        </section>
        <section class="ticker-section">
          <div class="ticker-label"><span>Pressure Queue</span><span class="badge">upgrade signals</span></div>
          <div class="ticker-list" id="watchlist"></div>
        </section>
      </aside>
    </section>

    <section class="lower-grid">
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title">Ranked Skills</div>
          <div class="panel-value">usage + delivery + momentum</div>
        </div>
        <div style="overflow:auto;">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Skill</th>
                <th>Runs</th>
                <th>7D</th>
                <th>Chg</th>
                <th>Eff</th>
                <th>Delivery</th>
                <th>Momentum</th>
                <th>Trend</th>
              </tr>
            </thead>
            <tbody id="leaderboard"></tbody>
          </table>
        </div>
      </section>

      <section class="stack">
        <section class="panel">
          <div class="panel-head">
            <div class="panel-title">Challenge Pressure</div>
            <div class="panel-value">hotspots by repeated friction</div>
          </div>
          <div style="overflow:auto;">
            <table class="compact-table">
              <thead>
                <tr>
                  <th>Challenge</th>
                  <th>Hits</th>
                  <th>Skills</th>
                </tr>
              </thead>
              <tbody id="challengeBoard"></tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head">
            <div class="panel-title">Recent Tape</div>
            <div class="panel-value" id="tapeLabel">latest tracked turns</div>
          </div>
          <div class="tape" id="recentTape"></div>
        </section>
      </section>
    </section>

    <footer class="footer">
      <div id="lastUpdated">Last update: booting…</div>
      <div id="refreshMode">Mode: embedded snapshot</div>
    </footer>
  </div>

  <script>
    const BOOTSTRAP_DATA = {bootstrap_json};
    const DASHBOARD_JSON_URL = "./skill-dashboard.json";
    const PALETTE = ["#56d7ff", "#49f2a5", "#ffc76a", "#d06cff", "#7d8bff", "#ff5e7a"];
    let currentData = BOOTSTRAP_DATA;

    function fmt(value, digits = 1) {{
      return Number(value).toFixed(digits);
    }}

    function pct(value) {{
      const sign = value > 0 ? "+" : "";
      return `${{sign}}${{fmt(value, 1)}}%`;
    }}

    function monoDate(value) {{
      const date = new Date(value);
      return date.toLocaleString([], {{
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      }});
    }}

    function deltaClass(value) {{
      if (value > 0) return "up";
      if (value < 0) return "down";
      return "flat";
    }}

    function escapeHtml(value) {{
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
    }}

    function sparklineSvg(points, color) {{
      const width = 128;
      const height = 34;
      const max = Math.max(...points, 1);
      const min = Math.min(...points, 0);
      const range = Math.max(max - min, 1);
      const coords = points.map((value, index) => {{
        const x = (index / Math.max(points.length - 1, 1)) * width;
        const y = height - (((value - min) / range) * (height - 6) + 3);
        return [x, y];
      }});
      const line = coords.map(([x, y]) => `${{x.toFixed(1)}},${{y.toFixed(1)}}`).join(" ");
      return `
        <svg class="spark" viewBox="0 0 ${{width}} ${{height}}" preserveAspectRatio="none">
          <polyline fill="none" stroke="rgba(120,180,255,0.12)" stroke-width="1" points="0,${{height-1}} ${{width}},${{height-1}}"></polyline>
          <polyline fill="none" stroke="${{color}}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" points="${{line}}"></polyline>
        </svg>
      `;
    }}

    function buildHeroChart(data) {{
      const svg = document.getElementById("heroChart");
      const series = data.chart_leaders || [];
      const labels = data.window.chart_days || [];
      const width = 960;
      const height = 320;
      const pad = {{ top: 24, right: 24, bottom: 28, left: 42 }};
      const maxValue = Math.max(
        1,
        ...series.flatMap(item => item.series)
      );

      const toX = (index) => pad.left + (index / Math.max(labels.length - 1, 1)) * (width - pad.left - pad.right);
      const toY = (value) => height - pad.bottom - (value / maxValue) * (height - pad.top - pad.bottom);

      const gridLines = [0, 0.25, 0.5, 0.75, 1].map(step => {{
        const y = pad.top + (1 - step) * (height - pad.top - pad.bottom);
        return `<line x1="${{pad.left}}" y1="${{y}}" x2="${{width - pad.right}}" y2="${{y}}" stroke="rgba(120,180,255,0.08)" stroke-width="1" />`;
      }}).join("");

      const paths = series.map((item, index) => {{
        const color = PALETTE[index % PALETTE.length];
        const d = item.series.map((value, pointIndex) => `${{pointIndex === 0 ? "M" : "L"}}${{toX(pointIndex).toFixed(1)}},${{toY(value).toFixed(1)}}`).join(" ");
        const finalX = toX(item.series.length - 1);
        const finalY = toY(item.series[item.series.length - 1] || 0);
        return `
          <path d="${{d}}" fill="none" stroke="${{color}}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"></path>
          <circle cx="${{finalX}}" cy="${{finalY}}" r="5.5" fill="${{color}}" />
          <circle cx="${{finalX}}" cy="${{finalY}}" r="13" fill="${{color}}" opacity="0.12" />
        `;
      }}).join("");

      const xTicks = labels.filter((_, index) => index % 5 === 0 || index === labels.length - 1).map((label, index) => {{
        const absoluteIndex = labels.indexOf(label);
        return `<text x="${{toX(absoluteIndex)}}" y="${{height - 8}}" fill="rgba(198,219,255,0.45)" font-size="11" text-anchor="middle">${{label.slice(5)}}</text>`;
      }}).join("");

      svg.innerHTML = `
        <rect x="0" y="0" width="${{width}}" height="${{height}}" fill="transparent"></rect>
        ${{gridLines}}
        ${{paths}}
        ${{xTicks}}
      `;

      document.getElementById("legend").innerHTML = series.map((item, index) => `
        <span class="legend-item">
          <span class="legend-dot" style="background:${{PALETTE[index % PALETTE.length]}}; color:${{PALETTE[index % PALETTE.length]}};"></span>
          <span>${{escapeHtml(item.skill)}} <span style="color:var(--muted)">· rank ${{item.rank_score}}</span></span>
        </span>
      `).join("");
    }}

    function renderMetrics(data) {{
      const metrics = [
        {{ label: "Active skills", value: data.overview.active_skills, note: `${{data.overview.total_runs}} tracked runs` }},
        {{ label: "7D volume", value: data.overview.runs_7d, note: `Leader: ${{data.overview.leader}}` }},
        {{ label: "Avg efficiency", value: `${{fmt(data.overview.avg_efficiency)}}`, note: `${{fmt(data.overview.avg_delivery)}}% delivery index` }},
        {{ label: "Last run", value: monoDate(data.last_run_at), note: "auto-sync + live board" }},
      ];

      document.getElementById("metricGrid").innerHTML = metrics.map(metric => `
        <div class="metric">
          <div class="metric-label">${{metric.label}}</div>
          <div class="metric-value">${{metric.value}}</div>
          <div class="metric-note">${{metric.note}}</div>
        </div>
      `).join("");
    }}

    function renderTicker(targetId, items, mode) {{
      document.getElementById(targetId).innerHTML = items.map(item => {{
        let deltaValue = mode === "watch"
          ? `${{fmt(item.friction, 1)}} friction`
          : pct(item.delta_pct);
        let deltaNumeric = mode === "down" ? -Math.abs(item.delta_pct) : item.delta_pct;
        if (mode === "watch") deltaNumeric = -Math.abs(item.friction);
        return `
          <div class="ticker-item">
            <div>
              <div class="ticker-main">${{escapeHtml(item.skill)}}</div>
              <div class="ticker-sub">7D runs: ${{item.runs_7d}} · eff ${{fmt(item.efficiency)}} · state ${{item.state}}</div>
            </div>
            <div class="delta ${{deltaClass(deltaNumeric)}}">${{escapeHtml(deltaValue)}}</div>
          </div>
        `;
      }}).join("");
    }}

    function renderLeaderboard(data) {{
      document.getElementById("leaderboard").innerHTML = data.leaders.map((item, index) => {{
        const sparkColor = item.delta_count > 0 ? "var(--green)" : item.delta_count < 0 ? "var(--red)" : "var(--cyan)";
        return `
          <tr>
            <td class="rank-cell">${{item.rank}}</td>
            <td>
              <div class="skill-name">${{escapeHtml(item.skill)}}</div>
              <div class="skill-state">${{escapeHtml(item.state)}} · score ${{fmt(item.rank_score)}}</div>
            </td>
            <td class="mono">${{item.total_runs}}</td>
            <td class="mono">${{item.runs_7d}}</td>
            <td><span class="delta ${{deltaClass(item.delta_pct)}}">${{pct(item.delta_pct)}}</span></td>
            <td class="mono">${{fmt(item.efficiency)}}</td>
            <td class="mono">${{fmt(item.delivery)}}%</td>
            <td><span class="delta ${{deltaClass(item.momentum)}}">${{item.momentum > 0 ? "+" : ""}}${{fmt(item.momentum)}}</span></td>
            <td>${{sparklineSvg(item.sparkline, sparkColor)}}</td>
          </tr>
        `;
      }}).join("");
    }}

    function renderChallenges(data) {{
      document.getElementById("challengeBoard").innerHTML = data.challenges.map(item => `
        <tr>
          <td>
            <div class="skill-name">${{escapeHtml(item.challenge)}}</div>
          </td>
          <td class="mono">${{item.hits}}</td>
          <td style="color:var(--muted)">${{escapeHtml(item.skills.slice(0, 4).join(", "))}}${{item.skills.length > 4 ? " +" + (item.skills.length - 4) : ""}}</td>
        </tr>
      `).join("");
    }}

    function renderTape(data) {{
      document.getElementById("recentTape").innerHTML = data.recent_runs.map(item => `
        <div class="tape-item">
          <div class="tape-time">${{monoDate(item.timestamp)}}</div>
          <div>
            <div class="tape-task">${{escapeHtml(item.task)}}</div>
            <div class="tape-skills">${{escapeHtml(item.skills.join(", "))}}</div>
          </div>
          <div class="delta ${{item.outcome === "success" ? "up" : item.outcome === "failed" ? "down" : "flat"}}">${{item.outcome}} · ${{fmt(item.efficiency)}}</div>
        </div>
      `).join("");
    }}

    function renderFooter(data, mode) {{
      document.getElementById("lastUpdated").textContent = `Generated ${{monoDate(data.generated_at)}} · last tracked run ${{monoDate(data.last_run_at)}}`;
      document.getElementById("refreshMode").textContent = mode;
    }}

    function renderBoard(data, mode = "embedded snapshot") {{
      currentData = data;
      renderMetrics(data);
      buildHeroChart(data);
      renderTicker("moversUp", data.movers_up, "up");
      renderTicker("moversDown", data.movers_down, "down");
      renderTicker("watchlist", data.watchlist, "watch");
      renderLeaderboard(data);
      renderChallenges(data);
      renderTape(data);
      renderFooter(data, mode);
    }}

    async function refreshJson() {{
      if (!location.protocol.startsWith("http")) {{
        renderFooter(currentData, "file snapshot · auto reload every 60s");
        return;
      }}
      try {{
        const response = await fetch(`${{DASHBOARD_JSON_URL}}?ts=${{Date.now()}}`, {{ cache: "no-store" }});
        if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
        const data = await response.json();
        renderBoard(data, "live polling · refresh every 20s");
      }} catch (error) {{
        renderFooter(currentData, "live polling paused · using last good snapshot");
      }}
    }}

    renderBoard(BOOTSTRAP_DATA, location.protocol.startsWith("http") ? "live polling · refresh every 20s" : "file snapshot · auto reload every 60s");
    setInterval(refreshJson, 20000);
    if (!location.protocol.startsWith("http")) {{
      setTimeout(() => location.reload(), 60000);
    }}
  </script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    input_paths = get_input_paths(args.input)
    if not input_paths:
        raise SystemExit("No input logs found. Pass --input or create telemetry logs first.")
    runs = load_runs(input_paths)
    payload = build_dashboard_payload(runs)

    html_output = Path(args.html_output).expanduser().resolve()
    json_output = Path(args.json_output).expanduser().resolve()
    html_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.parent.mkdir(parents=True, exist_ok=True)

    json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    html_output.write_text(render_html(payload), encoding="utf-8")

    print(f"Wrote dashboard json -> {json_output}")
    print(f"Wrote dashboard html -> {html_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
