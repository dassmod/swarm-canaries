"""Build the slide deck PDF.

Owner: Dastan.

Run:
  .venv/bin/python scripts/13_build_slides.py

Reads report/assets/cone_ground.png, cone_single.png (run scripts/11_cover_cone.py first) and the figures in results/.
The numbers on the slides come from results/robust_*.csv and report/draft.md.

Layout: margins of 64 px, one header band, one content band centred on its height, one foot line. Evidence
slides use a 962 px main column and a 446 px note column. Statement slides share one text edge at x = 720.

Writes:
  report/slides.html                                       the page Chrome prints
  report/The_Monitor_Was_Reading_the_Credits_slides.pdf    the deck
"""

import math
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

for name in ("cone_ground", "cone_single"):
    Image.open(OUT / "assets" / f"{name}.png").convert("RGB").save(OUT / "assets" / f"{name}.jpg", quality=90)

CSS = """
@page{size:1600px 900px;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1600px}
body{font-family:"Geist",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.s{width:1600px;height:900px;position:relative;overflow:hidden;break-after:page}
.s:last-child{break-after:auto}
.d{color:#fff}.d .m{color:#ffffff9c}
.g{background:url(assets/cone_ground.jpg) 0 0/1600px 900px}
.o{background:url(assets/cone_single.jpg) 0 0/1600px 900px}
.w{background:#fff;color:#211f1c}.w .m{color:#211f1c8c}
.m{font:400 19px/28px "Geist Mono",monospace}
.tag{position:absolute;right:64px;top:56px}
.pn{position:absolute;right:64px;bottom:52px}
.foot{position:absolute;bottom:52px}
h2{font-weight:500;letter-spacing:-.024em}
.w h2{position:absolute;left:64px;top:48px;width:1180px;font-size:48px;line-height:56px}
.content{position:absolute;left:64px;right:64px;top:190px;bottom:104px;display:grid;align-items:center}
.split{grid-template-columns:962px 446px;column-gap:64px}
.halves{grid-template-columns:1fr 1fr;column-gap:64px}
.content img,.content svg{width:100%;display:block}
.note{font-size:26px;line-height:37px;font-weight:300;color:#211f1cc4}
.note p{margin-bottom:26px}.note p:last-child{margin-bottom:0}
.w b{font-weight:500;color:#211f1c}
.lab{font:400 19px/28px "Geist Mono",monospace;color:#211f1c8c;margin-bottom:18px}
.row{border-top:1px solid #211f1c26;padding:18px 0 20px;font-size:25px;line-height:35px;font-weight:300;color:#211f1cc4}
.row b{display:block;font-size:30px;line-height:40px;margin-bottom:2px}
.head{position:absolute;left:720px;width:816px;bottom:486px;font-size:60px;line-height:68px}
.under{position:absolute;left:720px;width:816px;top:486px}
.sub{font-size:34px;line-height:46px;font-weight:300;color:#ffffffe0}
.facts{display:grid;grid-template-columns:150px 1fr;row-gap:16px;align-items:baseline}
.facts b{font-size:36px;font-weight:400}.facts span{font-size:24px;line-height:32px;font-weight:300}
.nums{display:grid;grid-template-columns:1fr 1fr;column-gap:32px}
.nums b{font-size:74px;line-height:88px;font-weight:400;letter-spacing:-.03em;display:block;white-space:nowrap}
.nums span{font-size:24px;line-height:32px;font-weight:300;color:#ffffffd9}
.title{position:absolute;left:1096px;width:440px}
table{border-collapse:collapse;width:100%;font-size:30px;line-height:40px}
th{font:400 19px/28px "Geist Mono",monospace;color:#211f1c8c;text-align:left;padding:0 20px 14px 0;border-bottom:1.5px solid #211f1c}
td{padding:20px 20px 20px 0;border-bottom:1px solid #211f1c26;font-weight:300}
td:first-child{font-weight:400}
.lead{font-size:26px;line-height:37px;font-weight:300;color:#211f1cc4}
.bar{display:grid;grid-template-columns:320px 1fr;align-items:center;margin-top:34px;font-size:26px;line-height:34px;font-weight:300}
.track{display:flex;align-items:center;gap:16px;font-size:34px;font-weight:400}
.fill{height:44px;background:#211f1c}
"""
FONT = (
    '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600'
    '&family=Geist+Mono:wght@400&display=block" rel="stylesheet">'
)


def white(tag, title, layout, body, number):
    return (
        f'<section class="s w"><div class="tag m">({tag})</div><h2>{title}</h2>'
        f'<div class="content {layout}">{body}</div><div class="pn m">{number}</div></section>'
    )


def dark(tag, head, under, number, foot=""):
    foot_html = f'<div class="foot m" style="left:720px">{foot}</div>' if foot else ""
    return (
        f'<section class="s d o"><div class="tag m">({tag})</div><h2 class="head">{head}</h2>'
        f'<div class="under">{under}</div>{foot_html}<div class="pn m">{number}</div></section>'
    )


def diagram():
    """Shared board in the middle. Every line starts and ends at the centre of an edge."""
    ink = "#211f1c"
    line = f'stroke="{ink}" stroke-width="1.6" fill="none" marker-end="url(#a)"'
    board_mid, radius = 190, 40
    parts = [
        f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0 0L10 5L0 10z" fill="{ink}"/></marker></defs>'
    ]
    for name, y, end in (("A", 60, 150), ("B", 190, 190), ("C", 320, 230)):
        dx, dy = 278 - 44, end - y
        length = math.hypot(dx, dy)
        x1, y1 = 44 + radius * dx / length, y + radius * dy / length
        parts.append(f'<circle cx="44" cy="{y}" r="{radius}" fill="#f1efea"/>')
        parts.append(f'<text x="44" y="{y + 9}" text-anchor="middle" font-size="26" fill="{ink}">{name}</text>')
        parts.append(f'<path d="M{x1:.1f} {y1:.1f}L278 {end}" {line}/>')
    parts += [
        f'<rect x="280" y="110" width="240" height="160" fill="{ink}"/>',
        f'<text x="400" y="{board_mid - 4}" text-anchor="middle" font-size="28" fill="#fff">Shared board</text>',
        f'<text x="400" y="{board_mid + 32}" text-anchor="middle" font-size="20" fill="#ffffffb0">read, post</text>',
        f'<path d="M520 {board_mid}L720 {board_mid}" {line}/>',
        f'<rect x="722" y="110" width="240" height="160" fill="none" stroke="{ink}" stroke-width="1.6"/>',
        f'<text x="842" y="{board_mid - 4}" text-anchor="middle" font-size="28" fill="{ink}">Reports</text>',
        f'<text x="842" y="{board_mid + 32}" text-anchor="middle" font-size="20" fill="#211f1c8c">all a detector sees</text>',
        f'<path d="M400 270L400 398" stroke="{ink}" stroke-width="1.6" fill="none" stroke-dasharray="6 6" marker-end="url(#a)"/>',
        '<text x="416" y="340" font-size="20" fill="#211f1c8c">every read and post</text>',
        '<rect x="280" y="400" width="240" height="120" fill="#eaff3d"/>',
        f'<text x="400" y="456" text-anchor="middle" font-size="26" font-weight="500" fill="{ink}">The log</text>',
        f'<text x="400" y="490" text-anchor="middle" font-size="20" fill="{ink}">written by the code</text>',
        f'<path d="M842 270L842 460L522 460" {line}/>',
        f'<text x="681" y="418" text-anchor="middle" font-size="20" fill="{ink}">detectors are scored</text>',
        f'<text x="681" y="446" text-anchor="middle" font-size="20" fill="{ink}">against the log</text>',
    ]
    return f'<svg viewBox="0 0 962 540" font-family="Geist, sans-serif">{"".join(parts)}</svg>'


def bars():
    rows = [
        ("Cite, nobody hides", 99, 135),
        ("Hard stealth", 15, 135),
        ("Told ids are checked", 3, 135),
        ("No board (control)", 0, 134),
    ]
    out = '<div><div class="lead">Reports that hold an id from another agent. Every report still cited its own.</div>'
    for label, n, total in rows:
        fill = f'<div class="fill" style="width:{int(n / 135 * 440)}px"></div>' if n else ""
        out += f'<div class="bar"><span>{label}</span><div class="track">{fill}{n} of {total}</div></div>'
    return out + "</div>"


def row(title, text):
    return f'<div class="row"><b>{title}</b>{text}</div>'


slides = [
    '<section class="s d g"><div class="tag m">(Swarm Alignment Hackathon)</div>'
    '<h2 class="title" style="bottom:486px;font-size:58px;line-height:64px">The Monitor<br>Was Reading<br>the Credits</h2>'
    '<div class="title sub" style="top:486px;font-size:27px;line-height:36px">Canaries and proof of transfer between AI agents</div>'
    '<div class="foot m" style="left:1096px">Dastan Modubash<br>Nikita Stanchenkov</div></section>',
    dark(
        "The problem",
        '<span style="font-size:56px;line-height:64px">If you can read only what each agent reports, can you prove that information moved?</span>',
        '<div class="facts"><b>1,200</b><span>agents found a message board nobody sanctioned</span>'
        "<b>70,000</b><span>messages and files, the record investigators needed</span>"
        "<b>1</b><span>report per agent, what an operator usually has</span></div>",
        2,
        "First two figures: METR, 2026",
    ),
    white(
        "The test",
        "To test it, you need the truth.",
        "split",
        diagram() + '<div class="note"><p><b>Three engineers, one outage.</b> Shared logs point to a wrong cause.</p>'
        "<p><b>The answer needs two private slices.</b> No agent holds both.</p>"
        "<p><b>465 runs.</b> One open model, four detectors that read reports.</p></div>",
        3,
    ),
    white(
        "What we measure",
        "Reading is not using. Using is not understanding.",
        "halves",
        '<div><div class="lab">(Levels of transfer, A to B)</div>'
        + row("Read", "B read a post with A's information")
        + row("Used", "A unique fact of A is in B's report")
        + row("Integrated", "The fact is part of a whole answer")
        + '</div><div><div class="lab">(Detectors, reports only)</div>'
        + row("Token canary", "Another agent's marked token in a report")
        + row("Fact canary", "Another agent's unique fact in a report")
        + row("LLM monitor", "Blind, redacted, or informed of who got what")
        + "</div>",
        4,
    ),
    dark(
        "First result",
        "The blind monitor caught 98%.",
        '<div class="sub">Sounds great.<br>But what was it reading?</div>',
        5,
    ),
    white(
        "Names",
        "It was reading the credits.",
        "split",
        '<img src="../results/fig2_names.png">'
        '<div class="note"><p>"Engineer B found 90 connections." No token, but a name.</p>'
        "<p><b>Names it: 94 to 100%.</b><br><b>Does not: 13 to 25%.</b></p>"
        "<p>Whiskers: 95% intervals over runs. Observational.</p></div>",
        6,
    ),
    dark(
        "One line in the format",
        "Cite the ids of log lines.<br>Nobody was asked to hide.",
        '<div class="nums"><div><b>98 to 14%</b><span>blind monitor<br>10% on a second model</span></div>'
        "<div><b>9 to 100%</b><span>token canary<br>we ordered agents to carry it</span></div></div>",
        7,
    ),
    white(
        "The flip",
        "The detectors trade places.",
        "split",
        '<img src="../results/fig1_detectors.png">'
        '<div class="note"><p>Reports naming another engineer: <b>72% to 5%</b>.</p>'
        "<p>In <b>28 of 45</b> cite runs the monitor said no communication at all.</p>"
        "<p>Removing the ids gave back only 14 to 25%.</p></div>",
        8,
    ),
    white(
        "Agents who hide",
        "A marked banknote works until someone knows it is marked.",
        "split",
        bars() + '<div class="note"><p>Token canary:<br><b>53%</b> under hard stealth, <b>12%</b> when told.</p>'
        "<p>Small numbers: 34 and 26 transfers. Wide intervals.</p></div>",
        9,
    ),
    white(
        "The price of tuning",
        "Low false alarms are not free.",
        "",
        "<div><table><tr><th>Monitor</th><th>Recall, plain</th><th>Recall, cite</th><th>False alarms, no board</th></tr>"
        "<tr><td>Careful prompt, qwen</td><td>98%</td><td>14%</td><td>1.7% of pairs (3 of 180)</td></tr>"
        "<tr><td>Careful prompt, gemma</td><td>99%</td><td>10%</td><td>5.0% (9 of 180)</td></tr>"
        "<tr><td>Neutral prompt, qwen</td><td>100%</td><td>36%</td><td>13.9% (25 of 180)</td></tr></table>"
        '<div class="lead" style="margin-top:44px">They live in two sentences of the prompt. Without them, <b>15 of 30</b> no-board runs held a false flag. Recall under cite still reached only 36%.</div></div>',
        10,
    ),
    dark(
        "What held up",
        "Not clever.<br>Just bookkeeping.",
        '<div class="sub">Who got what, and does the report match. The informed monitor held at '
        '<b style="font-weight:500">77 to 79%</b> when agents hid.</div>',
        11,
        "It works only where the operator knows what it handed out.",
    ),
    white(
        "What would make us wrong",
        "We would rather name it than cover it.",
        "halves",
        "<div>"
        + row("One agent model", "A second monitor, not second agents")
        + row("Cite is a protocol", "Agents cited because we said so")
        + row("Stealth is an instruction", "Not a learned goal")
        + "</div><div>"
        + row("Small cells", "15 to 45 runs. Follow-ups chosen after seeing data")
        + row("Used is a string match", "A paraphrase is not counted")
        + row("Channel was known", "No hidden channel tested")
        + "</div>",
        12,
    ),
    '<section class="s d g"><div class="tag m">(The Bookkeepers)</div>'
    '<h2 class="title" style="bottom:486px;font-size:46px;line-height:54px">A monitor sees what agents declare.</h2>'
    '<div class="title sub" style="top:486px;font-size:30px;line-height:40px">A canary sees what they agree to carry.</div>'
    '<div class="foot m" style="left:1096px">github.com/dassmod/swarm-canaries<br>Dastan Modubash, Nikita Stanchenkov</div></section>',
]
page = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The Monitor Was Reading the Credits</title>'
    f"{FONT}<style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
)
(OUT / "slides.html").write_text(page)
target = OUT / "The_Monitor_Was_Reading_the_Credits_slides.pdf"
subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
     "--virtual-time-budget=9000", f"--print-to-pdf={target}", f"file://{OUT / 'slides.html'}"],
    capture_output=True, check=True,
)  # fmt: skip
print("wrote", target)
