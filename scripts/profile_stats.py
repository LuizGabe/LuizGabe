"""Render notebook-style cards from public GitHub data, using only the stdlib."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = "LuizGabe"


def fetch(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "LuizGabe-profile"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
        return json.load(response)


def public_snapshot():
    profile = fetch(f"users/{USERNAME}")
    repos = []
    page = 1
    while True:
        batch = fetch(f"users/{USERNAME}/repos?type=owner&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return {"profile": profile, "repos": repos}


def render(snapshot, dark):
    profile = snapshot["profile"]
    repos = [repo for repo in snapshot["repos"] if not repo.get("private", False)]
    ink, muted, accent, line = (
        ("#e6edf3", "#a4b5ac", "#91c9ac", "#46564e") if dark
        else ("#293b34", "#576b60", "#376653", "#b8c9be")
    )
    stats = [
        (profile["public_repos"], "public repos"),
        (profile["followers"], "followers"),
        (sum(repo["stargazers_count"] for repo in repos if not repo["fork"]), "repo stars"),
    ]
    metrics = []
    for x, (value, label) in zip((80, 380, 680), stats):
        metrics.append(f'''<text x="{x}" y="143" font-size="44" font-weight="700" fill="{ink}">{value}</text>
        <text x="{x}" y="175" font-size="17" fill="{muted}">{label}</text>
        <path d="M{x} 189 q70 -5 168 0" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>''')
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="270" viewBox="0 0 1000 270" role="img" aria-labelledby="title desc">
  <title id="title">Luiz Gabriel — public GitHub profile</title>
  <desc id="desc">{stats[0][0]} public repositories, {stats[1][0]} followers and {stats[2][0]} stars on owned public repositories. Updated {updated} UTC.</desc>
  <path d="M17 22 Q480 14 981 23 L977 248 Q487 255 20 247 Z" fill="none" stroke="{line}" stroke-width="1.6"/>
  <path d="M22 27 Q480 20 973 28" fill="none" stroke="{line}" stroke-width="1" opacity="0.5"/>
  <g font-family="'Segoe UI', Arial, sans-serif">
    <text x="48" y="62" font-family="Consolas, monospace" font-size="14" letter-spacing="2" fill="{accent}">A FEW NOTES FROM GITHUB</text>
    {''.join(metrics)}
    <text x="48" y="228" font-size="12" fill="{muted}">Public data only · updated {updated} UTC</text>
    <text x="782" y="228" font-size="14" fill="{accent}">@LuizGabe ↗</text>
  </g>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Optional local JSON snapshot for offline rendering")
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8-sig")) if args.snapshot else public_snapshot()
    # Prepare both cards before writing, so failed API calls never replace a good card.
    cards = {theme: render(snapshot, theme == "dark") for theme in ("light", "dark")}
    for theme, svg in cards.items():
        (ROOT / "assets" / f"profile-stats-{theme}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    main()
