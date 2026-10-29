#!/usr/bin/env python3
"""FreeModel Radar — static site + README leaderboard generator.

Reads the daily OpenRouter free-model scan report (freetoken-bots.json,
produced by the existing local-freetoken-bots radar.py scan — public
catalogue data only, no OpenRouter API calls are made here) and
programmatically generates:

  - index.html  Today's free-model leaderboard (static, CF Pages ready)
  - data.json   Machine-readable copy of exactly the same numbers
  - README.md   GitHub-repo leaderboard section (between RADAR markers)

Zero manual transcription: every number on the page comes from the
report file, and counts are asserted consistent before anything is
written. Models whose parameter size has not been verified are always
labelled "unverified" — never presented as verified.

Usage:
  python3 gen_site.py                     # default report path
  python3 gen_site.py --report /path/to/freetoken-bots.json
  python3 gen_site.py --prev /path/to/yesterday.json
  python3 gen_site.py --emit-readme-segment   # print README table only

History / day-over-day diff:
  Each run archives a snapshot of the report it used into
  history/<checked-date>.json (idempotent per date). The diff section
  compares against --prev if given, else the newest archived snapshot
  whose date is earlier than the current report's date. If no earlier
  snapshot exists, the site states plainly that this is the first day
  and there is no comparison yet.
"""
import argparse
import html
import json
import shutil
import sys
from pathlib import Path

DEFAULT_REPORT = Path.home() / ".pi" / "agent" / "freetoken-bots.json"
HERE = Path(__file__).resolve().parent

STATUS_VERIFIED = "verified_eligible"
STATUS_NEEDS = "unverified_needs_parameter_verification"
STATUS_UNKNOWN = "unverified_unknown"

STATUS_LABEL = {
    STATUS_VERIFIED: "verified — eligible (tools supported, >=100B verified)",
    STATUS_NEEDS: "unverified — parameter size not verified",
    STATUS_UNKNOWN: "unverified — parameter status unknown (listed free, no verification data)",
}


def load_report(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("checked_at", "free_ids", "free_count"):
        if key not in data:
            raise AssertionError(f"report {path} missing required field: {key}")
    return data


def build_models(report):
    """Join free_ids with eligible / needs_parameter_verification data."""
    free_ids = list(report["free_ids"])
    free_count = int(report["free_count"])

    # Hard assertions: the report must be internally consistent,
    # otherwise fail closed and generate nothing.
    assert free_count == len(free_ids), (
        f"free_count ({free_count}) != len(free_ids) ({len(free_ids)})")
    assert len(set(free_ids)) == len(free_ids), "free_ids contains duplicates"

    ctx = {}
    status = {}
    params_b = {}
    for m in report.get("eligible", []):
        ctx[m["id"]] = m.get("context_length")
        status[m["id"]] = STATUS_VERIFIED
        params_b[m["id"]] = m.get("parameters_b")
    for m in report.get("needs_parameter_verification", []):
        ctx.setdefault(m["id"], m.get("context_length"))
        status.setdefault(m["id"], STATUS_NEEDS)
    for mid in status:
        assert mid in free_ids, f"verification entry {mid} not in free_ids"

    models = []
    for mid in sorted(free_ids):
        models.append({
            "id": mid,
            "context_length": ctx.get(mid),  # None = not in scan data, shown as unknown
            "parameters_b": params_b.get(mid),
            "verification_status": status.get(mid, STATUS_UNKNOWN),
            "verified": status.get(mid) == STATUS_VERIFIED,
        })
    assert len(models) == free_count, (
        f"built {len(models)} model rows, report free_count is {free_count}")
    return models


def find_prev(report, explicit_prev, history_dir):
    """Return (prev_report_dict_or_None, source_description)."""
    if explicit_prev:
        return load_report(explicit_prev), str(explicit_prev)
    cur_date = report["checked_at"][:10]
    candidates = []
    hdir = Path(history_dir)
    if hdir.is_dir():
        for f in sorted(hdir.glob("*.json")):
            try:
                r = load_report(f)
            except Exception:
                continue
            if r["checked_at"][:10] < cur_date:
                candidates.append((r["checked_at"], r, str(f)))
    if candidates:
        candidates.sort(key=lambda t: t[0])
        _, r, src = candidates[-1]
        return r, src
    return None, None


def compute_changes(report, prev):
    cur = set(report["free_ids"])
    if prev is None:
        return {"is_first_day": True, "prev_checked_at": None,
                "added": [], "removed": []}
    old = set(prev["free_ids"])
    return {"is_first_day": False, "prev_checked_at": prev["checked_at"],
            "added": sorted(cur - old), "removed": sorted(old - cur)}


def fmt_ctx(v):
    return f"{v:,}" if isinstance(v, int) else "unknown"


def render_table_rows(models):
    rows = []
    for m in models:
        badge = "verified" if m["verified"] else "unverified"
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(m['id'])}</code></td>"
            f"<td>{fmt_ctx(m['context_length'])}</td>"
            f"<td><span class=\"badge badge-{badge}\">{badge}</span> "
            f"{html.escape(STATUS_LABEL[m['verification_status']])}</td>"
            "</tr>")
    return "\n".join(rows)


def render_changes_html(changes):
    if changes["is_first_day"]:
        return ("<p><strong>First day — no comparison available.</strong> "
                "This site was generated for the first time from the scan "
                "report above, so there is no yesterday report to diff "
                "against yet. A snapshot of today's report has been "
                "archived; from tomorrow on, models added / removed will "
                "be listed here automatically.</p>")
    parts = [f"<p>Compared with the previous report "
             f"({html.escape(changes['prev_checked_at'])}): "
             f"<strong>{len(changes['added'])} added</strong>, "
             f"<strong>{len(changes['removed'])} removed</strong>.</p>"]
    if changes["added"]:
        parts.append("<h3>Added</h3><ul>" + "".join(
            f"<li><code>{html.escape(x)}</code></li>" for x in changes["added"]) + "</ul>")
    if changes["removed"]:
        parts.append("<h3>Removed</h3><ul>" + "".join(
            f"<li><code>{html.escape(x)}</code></li>" for x in changes["removed"]) + "</ul>")
    if not changes["added"] and not changes["removed"]:
        parts.append("<p>No changes since the previous report.</p>")
    return "\n".join(parts)


def render_index(report, models, changes):
    checked = html.escape(report["checked_at"])
    n_verified = sum(1 for m in models if m["verified"])
    n_unverified = len(models) - n_verified
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FreeModel Radar — OpenRouter free models, updated from the daily scan</title>
<meta name="description" content="Daily leaderboard of free models on OpenRouter, generated programmatically from a daily scan. Unverified models are labelled unverified.">
<style>
body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;max-width:960px;margin:0 auto;padding:24px 16px 64px;color:#16181d;line-height:1.55}}
h1{{margin-bottom:4px}} .sub{{color:#555;margin-top:0}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}
.card{{border:1px solid #ddd;border-radius:10px;padding:12px 18px;min-width:140px}}
.card b{{font-size:26px;display:block}}
table{{border-collapse:collapse;width:100%;margin:12px 0 32px}}
th,td{{border:1px solid #ddd;padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f5f5f7}} code{{font-size:13px;word-break:break-all}}
.badge{{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600}}
.badge-verified{{background:#e2f5e4;color:#14632a}}
.badge-unverified{{background:#fdf0e0;color:#8a4b00}}
#pro{{border:2px solid #16181d;border-radius:12px;padding:20px 24px;margin-top:40px}}
.btn{{display:inline-block;background:#16181d;color:#fff;padding:10px 22px;border-radius:8px;text-decoration:none;font-weight:600}}
footer{{color:#777;font-size:13px;margin-top:48px}}
</style>
</head>
<body>
<h1>FreeModel Radar</h1>
<p class="sub">Free models on OpenRouter — generated automatically from the daily scan report. No hand-edited lists.</p>

<div class="cards">
<div class="card"><b>{len(models)}</b>free models today</div>
<div class="card"><b>{n_verified}</b>verified eligible</div>
<div class="card"><b>{n_unverified}</b>unverified</div>
</div>
<p>Scan checked at: <strong>{checked}</strong> (source: <code>freetoken-bots.json</code> daily scan of the public OpenRouter catalogue). A model is only called <em>verified</em> when the scan could confirm its parameter size (&ge;100B) and tool support. Everything else is honestly labelled <strong>unverified</strong>. Context length is shown as <em>unknown</em> when the scan has no data for that model — it is never guessed.</p>

<h2>Today's free-model leaderboard</h2>
<table>
<thead><tr><th>Model ID</th><th>Context length (tokens)</th><th>Parameter verification status</th></tr></thead>
<tbody>
{render_table_rows(models)}
</tbody>
</table>

<h2>Changes vs. previous report</h2>
{render_changes_html(changes)}

<section id="pro">
<h2>FreeModel Radar Pro — $3/month</h2>
<p>Never miss a free model again:</p>
<ul>
<li><strong>Instant add/remove alerts</strong> — get notified as soon as the daily scan detects a free model being listed or delisted on OpenRouter.</li>
<li><strong>Full change history</strong> — searchable archive of every listing change the radar has recorded, not just today's board.</li>
</ul>
<p>Free tier above always stays free: today's leaderboard and yesterday's diff. Pro adds the alerts and the history archive.</p>
<p><a class="btn" href="GUMROAD_LINK_PLACEHOLDER">Subscribe on Gumroad — $3/month</a></p>
<p><small>Checkout is not connected yet — the button above is a placeholder until the Gumroad product goes live.</small></p>
</section>

<footer>
<p>Data: daily automated scan of the public OpenRouter model catalogue (scan report <code>checked_at</code> shown above). Listings change without notice; a model appearing here means it was listed as free at scan time, not that it is guaranteed to stay free or to suit any particular workload. Parameter status marked unverified has not been independently confirmed.</p>
</footer>
</body>
</html>
"""


def render_readme_segment(report, models, changes):
    """Markdown leaderboard segment — what the GitHub repo README shows."""
    lines = []
    lines.append(f"**Last scan:** {report['checked_at']} · "
                 f"**Free models:** {len(models)} · "
                 f"**Verified eligible:** {sum(1 for m in models if m['verified'])} · "
                 f"**Unverified:** {sum(1 for m in models if not m['verified'])}")
    lines.append("")
    lines.append("| Model ID | Context length (tokens) | Parameter verification status |")
    lines.append("|---|---|---|")
    for m in models:
        lines.append(f"| `{m['id']}` | {fmt_ctx(m['context_length'])} | "
                     f"{STATUS_LABEL[m['verification_status']]} |")
    lines.append("")
    if changes["is_first_day"]:
        lines.append("**Changes:** first day — no previous report to compare against yet.")
    else:
        lines.append(f"**Changes vs. {changes['prev_checked_at']}:** "
                     f"{len(changes['added'])} added, {len(changes['removed'])} removed.")
        for x in changes["added"]:
            lines.append(f"- Added: `{x}`")
        for x in changes["removed"]:
            lines.append(f"- Removed: `{x}`")
    return "\n".join(lines) + "\n"


README_TEMPLATE = """# FreeModel Radar

Daily leaderboard of **free models on OpenRouter**, generated programmatically
from an automated daily scan of the public OpenRouter catalogue.
No hand-edited lists; models whose parameter size could not be verified are
labelled **unverified**.

<!-- RADAR:START -->
{segment}<!-- RADAR:END -->

## Regenerate

```bash
python3 gen_site.py --report /path/to/freetoken-bots.json
```

`gen_site.py` rewrites `index.html`, `data.json` and the leaderboard
section of this README (between the `RADAR:START` / `RADAR:END` markers),
and prints the README segment on its own with `--emit-readme-segment`.

## Pro alerts ($3/month)

Instant add/remove alerts + the full change-history archive:
see the `#pro` section of the generated site. (Gumroad checkout link is a
placeholder until the product is connected.)
"""


def update_readme(outdir, report, models, changes):
    segment = render_readme_segment(report, models, changes)
    path = Path(outdir) / "README.md"
    if path.exists() and "<!-- RADAR:START -->" in path.read_text(encoding="utf-8"):
        text = path.read_text(encoding="utf-8")
        pre, rest = text.split("<!-- RADAR:START -->", 1)
        _, post = rest.split("<!-- RADAR:END -->", 1)
        text = (pre + "<!-- RADAR:START -->\n" + segment +
                "<!-- RADAR:END -->" + post)
    else:
        text = README_TEMPLATE.replace("{segment}", segment)
    path.write_text(text, encoding="utf-8")
    return segment


def archive_snapshot(report, history_dir):
    hdir = Path(history_dir)
    hdir.mkdir(parents=True, exist_ok=True)
    dest = hdir / f"{report['checked_at'][:10]}.json"
    if not dest.exists():
        dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return dest


def main():
    ap = argparse.ArgumentParser(description="FreeModel Radar generator")
    ap.add_argument("--report", default=str(DEFAULT_REPORT),
                    help="path to freetoken-bots.json scan report")
    ap.add_argument("--prev", default=None,
                    help="path to previous report for diff (default: newest earlier snapshot in history/)")
    ap.add_argument("--outdir", default=str(HERE), help="output directory")
    ap.add_argument("--history-dir", default=str(HERE / "history"))
    ap.add_argument("--emit-readme-segment", action="store_true",
                    help="print only the README leaderboard segment and exit")
    args = ap.parse_args()

    report = load_report(args.report)
    models = build_models(report)  # asserts counts; fail closed on mismatch
    prev, prev_src = find_prev(report, args.prev, args.history_dir)
    changes = compute_changes(report, prev)

    if args.emit_readme_segment:
        sys.stdout.write(render_readme_segment(report, models, changes))
        return 0

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Archive today's snapshot AFTER diff lookup, so tomorrow can compare.
    snap = archive_snapshot(report, args.history_dir)

    data = {
        "checked_at": report["checked_at"],
        "free_count": int(report["free_count"]),
        "verified_count": sum(1 for m in models if m["verified"]),
        "unverified_count": sum(1 for m in models if not m["verified"]),
        "models": models,
        "changes": changes,
        "prev_source": prev_src,
    }
    assert data["free_count"] == len(data["models"])

    (outdir / "data.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (outdir / "index.html").write_text(
        render_index(report, models, changes), encoding="utf-8")
    update_readme(outdir, report, models, changes)

    print(f"report_checked_at={report['checked_at']}")
    print(f"free_count={data['free_count']} models_written={len(models)} "
          f"verified={data['verified_count']} unverified={data['unverified_count']}")
    print(f"changes: first_day={changes['is_first_day']} "
          f"added={len(changes['added'])} removed={len(changes['removed'])} "
          f"prev_source={prev_src}")
    print(f"snapshot_archived={snap}")
    print(f"wrote: {outdir / 'index.html'}, {outdir / 'data.json'}, {outdir / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
