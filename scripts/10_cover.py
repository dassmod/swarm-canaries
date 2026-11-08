"""Three project image options, each drawn from the real run logs.

Owner: Dastan.

Run:
  .venv/bin/python scripts/10_cover.py

Reads data/runs, data/monitor and results/robust_recall.csv. All three use the cite cell on the plain board.

Writes report/assets/cover_a.html, cover_b.html, cover_c.html, cover_d.html and cover_e.html. A browser renders them to PNG.
  a: every agent is a dot; each used transfer is a smear; a line is a transfer the blind monitor flagged
  b: a circle cut at the share of transfers the blind monitor saw, by area
  c: one tile per run, one strip per report, each block is a cited id coloured by the agent that owned it
  d: a mix of the three: one tile per used transfer, packed in a disc and cut at the share the monitor saw
  e: a soft connected network with one neon node (decorative, carries no data)
"""

import csv
import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ground_truth import agent_info, ground_truth, load_run, reports  # noqa: E402

COND = "board=on,push=off,share=off,n=3,cite=on"
OUT = ROOT / "report" / "assets"
FONTS = (
    '<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500'
    '&family=Newsreader:opsz,wght@72,400&display=block" rel="stylesheet">'
)
ID = re.compile(r"\b(?:data|sh)-[A-Z0-9]+\b")

runs = []
for p in sorted((ROOT / "data" / "runs").glob("*.jsonl")):
    rows, meta = load_run(p)
    if meta["condition"] == COND:
        flags = json.loads((ROOT / "data" / "monitor" / f"{meta['run_id']}.json").read_text())["flags"]
        runs.append((meta, reports(rows), set(ground_truth(rows, meta)["used"]), {(f["src"], f["dst"]) for f in flags}))
row = next(
    r
    for r in csv.DictReader(open(ROOT / "results" / "robust_recall.csv"))
    if r["condition"] == COND and r["detector"] == "monitor_blind"
)
caught, used = int(row["caught"]), int(row["used"])
share = caught / used


def page(bg, body):
    return (
        f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>*{{margin:0}}html,body{{width:1600px;height:900px;'
        f'background:{bg};overflow:hidden}}</style></head><body><svg width="1600" height="900" viewBox="0 0 1600 900" '
        f'font-family="Geist Mono, monospace">{body}</svg></body></html>'
    )


def cover_a():
    rng = random.Random(7)
    ink = "#0b0b0b"
    ghost, lines, dots = [], [], []
    cols = 9
    order = list(range(len(runs)))
    for k, i in enumerate(order):
        meta, _, u, f = runs[i]
        cx = 150 + (k % cols) * 150 + rng.uniform(-30, 30) + (75 if (k // cols) % 2 else 0)
        cy = 110 + (k // cols) * 136 + rng.uniform(-26, 26)
        turn = rng.uniform(0, 6.28)
        pos = {
            a: (
                cx + 40 * math.cos(turn + j * 2.09 + rng.uniform(-0.4, 0.4)),
                cy + 40 * math.sin(turn + j * 2.09 + rng.uniform(-0.4, 0.4)),
            )
            for j, a in enumerate(meta["agents"])
        }
        for s, d in u:
            (x1, y1), (x2, y2) = pos[s], pos[d]
            ghost.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
            if (s, d) in f:
                for off in (-1.6, 0, 1.6):
                    lines.append(
                        f'<line x1="{x1 + off:.1f}" y1="{y1 + off:.1f}" x2="{x2 + off:.1f}" y2="{y2 - off:.1f}"/>'
                    )
        for x, y in pos.values():
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11"/>')
    body = (
        '<defs><filter id="b" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter></defs>'
        f'<g filter="url(#b)" stroke="#000" stroke-opacity=".30" stroke-width="16" stroke-linecap="round">{"".join(ghost)}</g>'
        f'<g stroke="{ink}" stroke-width=".9">{"".join(lines)}</g><g fill="{ink}">{"".join(dots)}</g>'
        f'<text x="64" y="858" font-size="20" fill="#3a3a3a">Every smear is a real transfer. A line is one the monitor saw: {caught} of {used}.</text>'
        '<text x="1536" y="858" font-size="20" fill="#3a3a3a" text-anchor="end">The Monitor Was Reading the Credits</text>'
    )
    return page("#e4e4e4", body)


def cap_height(f):
    """Height of the circular cap that holds share f of the disc area, for radius 1."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        h = (lo + hi) / 2
        a = math.acos(1 - h)
        area = (a - math.sin(a) * math.cos(a)) / math.pi
        lo, hi = (h, hi) if area < f else (lo, h)
    return lo


def cover_b():
    r = 290
    line_y = 330
    cy = line_y + r * (1 - cap_height(share))
    ink = "#2f2f2f"
    body = (
        '<defs><filter id="b" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="30"/></filter>'
        f'<clipPath id="up"><rect x="0" y="0" width="1600" height="{line_y}"/></clipPath>'
        f'<clipPath id="down"><rect x="0" y="{line_y}" width="1600" height="600"/></clipPath></defs>'
        f'<g clip-path="url(#down)"><circle cx="800" cy="{cy:.1f}" r="{r - 16}" fill="{ink}" fill-opacity=".72" filter="url(#b)"/></g>'
        f'<circle cx="800" cy="{cy:.1f}" r="{r}" fill="{ink}" clip-path="url(#up)"/>'
        f'<line x1="240" y1="{line_y}" x2="1360" y2="{line_y}" stroke="{ink}" stroke-width="2"/>'
        f'<text x="64" y="74" font-size="22" fill="{ink}" fill-opacity=".75">The Monitor Was Reading the Credits</text>'
        f'<text x="240" y="196" font-family="Newsreader, serif" font-size="104" fill="{ink}">{share:.0%}</text>'
        f'<text x="244" y="240" font-size="24" fill="{ink}">transfers the monitor saw</text>'
        f'<text x="1360" y="770" text-anchor="end" font-family="Newsreader, serif" font-size="104" fill="{ink}">{1 - share:.0%}</text>'
        f'<text x="1356" y="814" text-anchor="end" font-size="24" fill="{ink}">moved, and it did not</text>'
        f'<text x="64" y="858" font-size="20" fill="{ink}" fill-opacity=".75">{used} logged transfers, by area. One report format. Nobody told to hide.</text>'
    )
    return page("#adc7cb", body)


def cover_c():
    color = {"A": "#e8532f", "B": "#23549c", "C": "#f4c430"}
    shared = "#3a3350"
    tile, gap = 134, 8
    out = []
    for k, (meta, reps, _, _) in enumerate(sorted(runs, key=lambda x: (x[0]["scenario"]["name"], x[0]["seed"]))):
        col, rw = k % 9, k // 9
        x0 = 112 + col * (tile + gap) + (71 if rw % 2 else 0)
        y0 = 56 + rw * (tile + gap)
        info = agent_info(meta["scenario"], meta["agents"])
        owner = {t: a for a, i in info.items() for t in i["data"]}
        w = tile / 3
        for j, a in enumerate(meta["agents"]):
            ids = ID.findall(reps.get(a, ""))
            h = tile / max(len(ids), 1)
            for n, t in enumerate(ids):
                fill = color[owner[t]] if t in owner else shared
                out.append(
                    f'<rect x="{x0 + j * w:.2f}" y="{y0 + n * h:.2f}" width="{w + 0.4:.2f}" height="{h + 0.4:.2f}" fill="{fill}"/>'
                )
    ink = "#2b2720"
    body = (
        "".join(out)
        + f'<text x="112" y="806" font-size="20" fill="{ink}">One tile is a run. One strip is a report. One block is a cited log line,</text>'
        + f'<text x="112" y="836" font-size="20" fill="{ink}">coloured by the agent it came from. The dark blocks were shared with all.</text>'
        + f'<text x="1488" y="836" font-size="20" fill="{ink}" text-anchor="end">The Monitor Was Reading the Credits</text>'
    )
    return page("#eadfc4", body)


def cover_d():
    """Mix of a, b and c: one tile per used transfer, packed in a disc and cut at the share the monitor saw."""
    color = {"A": "#e8532f", "B": "#23549c", "C": "#f4c430"}
    seen, missed = [], []
    for _meta, _reps, u, f in runs:
        for pair in sorted(u):
            (seen if pair in f else missed).append(pair)
    rng = random.Random(3)
    rng.shuffle(seen)
    rng.shuffle(missed)
    pitch = 46
    n = len(seen) + len(missed)
    radius = pitch * math.sqrt(n / math.pi)
    rows = round(2 * radius / pitch)
    widths = [
        max(1, round(2 * math.sqrt(max(radius**2 - ((i + 0.5) * pitch - radius) ** 2, 0)) / pitch)) for i in range(rows)
    ]
    # Rows above the line hold exactly the seen tiles, rows below exactly the missed tiles.
    top = 3
    widths[:top] = [4, 7, len(seen) - 11]
    i = len(widths) - 1
    while sum(widths) != n:
        widths[i] += 1 if sum(widths) < n else -1
        i = i - 1 if i > top else len(widths) - 1
    ink = "#211f1c"
    gap = 16
    y0 = 450 - (rows * pitch + gap) / 2 + 8
    line_y = y0 + top * pitch + gap / 2 - 2
    crisp, soft = [], []
    pool = iter(seen + missed)
    for r, w in enumerate(widths):
        x0 = 800 - w * pitch / 2
        y = y0 + r * pitch + (gap if r >= top else 0)
        for c in range(w):
            s, d = next(pool)
            x = x0 + c * pitch
            size = pitch - 4
            inner = size * rng.uniform(0.35, 0.62)
            target = crisp if r < top else soft
            target.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" fill="{color[s]}"/>')
            target.append(
                f'<rect x="{x:.1f}" y="{y + size - inner:.1f}" width="{size}" height="{inner:.1f}" fill="{color[d]}"/>'
            )
            a, b = (x + 10, y + 12), (x + size - 10, y + size - 12)
            if r < top:
                target.append(
                    f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{ink}" stroke-width="1.6"/>'
                )
            for px, py in (a, b):
                target.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{ink}"/>')
    body = (
        '<defs><filter id="b" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="10"/></filter>'
        f'<clipPath id="down"><rect x="0" y="{line_y}" width="1600" height="900"/></clipPath></defs>'
        f'<g clip-path="url(#down)"><g filter="url(#b)" opacity=".82">{"".join(soft)}</g></g>'
        f'{"".join(crisp)}<line x1="100" y1="{line_y:.1f}" x2="1500" y2="{line_y:.1f}" stroke="{ink}" stroke-width="2"/>'
        f'<text x="64" y="74" font-size="22" fill="{ink}" fill-opacity=".75">The Monitor Was Reading the Credits</text>'
        f'<text x="100" y="{line_y - 74:.0f}" font-family="Newsreader, serif" font-size="104" fill="{ink}">{share:.0%}</text>'
        f'<text x="104" y="{line_y - 30:.0f}" font-size="24" fill="{ink}">transfers the monitor saw</text>'
        f'<text x="1500" y="770" text-anchor="end" font-family="Newsreader, serif" font-size="104" fill="{ink}">{1 - share:.0%}</text>'
        f'<text x="1496" y="814" text-anchor="end" font-size="24" fill="{ink}">moved, and it did not</text>'
        f'<text x="64" y="858" font-size="20" fill="{ink}" fill-opacity=".75">One tile is one logged transfer: {used} in all. Colours are sender and receiver.</text>'
    )
    return page("#e9e3d4", body)


def cover_e():
    """A soft connected network with one neon node, for the project image. Decorative: it carries no data."""
    rng = random.Random(21)
    ink = "#17171a"
    nodes = []
    while len(nodes) < 30:
        x, y = rng.uniform(430, 1540), rng.uniform(70, 800)
        wave = 250 + 120 * math.sin((x - 400) / 230)
        if abs(y - wave - (x - 430) * 0.17) > 175 or (x < 1010 and y > 470):
            continue
        if all(math.hypot(x - a, y - b) > 92 for a, b in nodes):
            nodes.append((x, y))
    edges = set()
    for i, a in enumerate(nodes):
        near = sorted((math.hypot(a[0] - b[0], a[1] - b[1]), j) for j, b in enumerate(nodes) if j != i)
        for _, j in near[:3]:
            edges.add((min(i, j), max(i, j)))
    links = {i: set() for i in range(len(nodes))}
    for a, b in edges:
        links[a].add(b)
        links[b].add(a)
    target = min(range(len(nodes)), key=lambda i: math.hypot(nodes[i][0] - 1067, nodes[i][1] - 300))
    start = min(range(len(nodes)), key=lambda i: nodes[i][0])
    seen, frontier = {start: None}, [start]
    while frontier and target not in seen:
        now = frontier.pop(0)
        for nxt in sorted(links[now]):
            if nxt not in seen:
                seen[nxt] = now
                frontier.append(nxt)
    spine, at = set(), target
    while at is not None and seen.get(at) is not None:
        spine.add((min(at, seen[at]), max(at, seen[at])))
        at = seen[at]

    def curve(a, b, bow):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        nx, ny = -dy, dx
        c1 = (x1 + dx * 0.36 + nx * bow, y1 + dy * 0.36 + ny * bow)
        c2 = (x2 - dx * 0.36 - nx * bow * 0.72, y2 - dy * 0.36 - ny * bow * 0.72)
        return f"M{x1:.1f} {y1:.1f}C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {x2:.1f} {y2:.1f}"

    sharp, haze = [], []
    for a, b in sorted(edges):
        base = 0.26 * (1 if math.sin(nodes[a][0] / 170 + nodes[b][1] / 240) > 0 else -1)
        main = (a, b) in spine
        for k in range(5 if main else 3):
            opacity = (0.95 if main else 0.5) * (0.62**k)
            width = 1.5 if main and k == 0 else 0.8
            sharp.append(
                f'<path d="{curve(nodes[a], nodes[b], base * (1 + 0.42 * k))}" stroke-width="{width}" stroke-opacity="{opacity:.2f}"/>'
            )
        haze.append(f'<path d="{curve(nodes[a], nodes[b], base)}"/>')
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(3, 6.5):.1f}" fill="{ink}"/>'
        for i, (x, y) in enumerate(nodes)
        if i != target
    )
    tx, ty = nodes[target]
    far = "".join(
        f'<circle cx="{rng.uniform(760, 1600):.0f}" cy="{rng.uniform(20, 880):.0f}" r="{rng.uniform(14, 42):.0f}"/>'
        for _ in range(9)
    )
    title = ["The Monitor", "Was Reading", "the Credits"]
    style = 'font-family="Fraunces, serif" font-weight="300" letter-spacing="-3" style="font-variation-settings:\'SOFT\' 100,\'WONK\' 0,\'opsz\' 144"'
    lines = "".join(
        f'<text x="84" y="{560 + i * 118}" font-size="124" fill="{ink}" {style}>{t}</text>' for i, t in enumerate(title)
    )
    body = (
        '<defs><filter id="b" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="16"/></filter>'
        '<filter id="c" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="30"/></filter>'
        '<filter id="n" x="-150%" y="-150%" width="400%" height="400%"><feGaussianBlur stdDeviation="20"/></filter>'
        '<linearGradient id="f" x1="0" x2="1" y1="0" y2="0"><stop offset=".3" stop-color="#000"/><stop offset=".62" stop-color="#fff"/></linearGradient>'
        '<mask id="m"><rect width="1600" height="900" fill="url(#f)"/></mask></defs>'
        f'<g mask="url(#m)"><g filter="url(#c)" fill="{ink}" opacity=".085">{far}</g>'
        f'<g filter="url(#b)" fill="none" stroke="{ink}" stroke-width="20" opacity=".1" transform="translate(-60 34) scale(1.05)">{"".join(haze)}</g></g>'
        f'<g fill="none" stroke="{ink}" stroke-linecap="round">{"".join(sharp)}</g>{dots}'
        f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="46" fill="#eaff3d" opacity=".75" filter="url(#n)"/>'
        f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="19" fill="#eaff3d" stroke="{ink}" stroke-width="1.4"/>'
        f"{lines}"
        f'<text x="88" y="848" font-size="21" fill="{ink}" fill-opacity=".62">Canaries and proof of transfer between AI agents</text>'
    )
    fonts = (
        '<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400'
        '&family=Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1&display=block" rel="stylesheet">'
    )
    return page("#fbfbf9", body).replace(FONTS, fonts)


OUT.mkdir(exist_ok=True)
for name, fn in (("a", cover_a), ("b", cover_b), ("c", cover_c), ("d", cover_d), ("e", cover_e)):
    (OUT / f"cover_{name}.html").write_text(fn())
print(f"{len(runs)} runs, {caught} of {used} caught ({share:.1%})")
