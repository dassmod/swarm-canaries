"""Build the report PDF from report/draft.md.

Owner: Dastan.

Run:
  .venv/bin/python scripts/12_build_report.py

Reads report/draft.md and the figures in results/.

Writes:
  report/report.html                                   the page Chrome prints
  report/The_Monitor_Was_Reading_the_Credits.pdf       the report
"""

import re
import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "report"

CSS = """
@page{size:A4;margin:16mm 21mm 17mm;
 @bottom-left{content:"The Monitor Was Reading the Credits";font:400 7.4pt "Geist Mono",monospace;color:#211f1c80}
 @bottom-right{content:counter(page);font:400 7.4pt "Geist Mono",monospace;color:#211f1c80}}
:root{--neon:#eaff3d;--ink:#211f1c;--mid:#211f1cb0;--faint:#211f1c80;--hair:#211f1c26}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Geist",sans-serif;color:var(--ink);font-size:9.6pt;line-height:14.2pt;background:#fff;
 -webkit-print-color-adjust:exact;print-color-adjust:exact}
.top{display:flex;justify-content:space-between;font:400 7.4pt/11pt "Geist Mono",monospace;color:var(--faint);
 padding-bottom:3.5mm;border-bottom:.6pt solid var(--hair)}
h1{font-size:27pt;line-height:30.5pt;font-weight:500;letter-spacing:-.022em;margin-top:6mm}
.sub{font-size:12pt;line-height:16pt;color:var(--mid);margin-top:2.2mm}
.authors{display:flex;gap:11mm;margin-top:4.5mm;font-size:9pt;line-height:12.5pt}
.authors b{font-weight:500;display:block}
.authors span{color:var(--faint);font:400 7.6pt/11.5pt "Geist Mono",monospace}
.label{font:400 7.6pt/11pt "Geist Mono",monospace;color:var(--faint);display:block;margin-bottom:1.4mm}
.abstract{margin-top:5mm;padding:3.6mm 0 2mm;border-top:.6pt solid var(--hair);border-bottom:.6pt solid var(--hair);
 font-size:9.2pt;line-height:13.4pt}
h2{font-size:12.5pt;line-height:16pt;font-weight:600;letter-spacing:-.01em;margin-top:6mm;margin-bottom:1.8mm;break-after:avoid}
h3{font-size:10.2pt;line-height:14pt;font-weight:600;margin-top:4mm;margin-bottom:1.2mm;break-after:avoid}
p{margin-bottom:2.1mm}
ul{list-style:none;margin:1mm 0 2.4mm}
li{position:relative;padding-left:4.4mm;margin-bottom:1.4mm}
li:before{content:"";position:absolute;left:0;top:1.75mm;width:1.5mm;height:1.5mm;background:var(--ink)}
b,strong{font-weight:600}
code{font:400 8.5pt "Geist Mono",monospace;background:#211f1c10;padding:0 .25em}
a{color:inherit}
blockquote{margin:2.4mm 0 3mm;padding:2.4mm 3.4mm;background:#f6f5f2;font-size:9pt;line-height:13pt;break-inside:avoid}
blockquote p{margin-bottom:1.6mm}blockquote p:last-child{margin-bottom:0}
figure{margin:3mm 0 3.4mm;break-inside:avoid}
figure img{width:100%;display:block}
.cap{font-size:8.2pt;line-height:11.4pt;color:var(--mid);margin-top:1.4mm;margin-bottom:3.2mm;break-before:avoid}
table{border-collapse:collapse;width:100%;margin:2.4mm 0 1mm;font-size:8.6pt;line-height:12pt;break-inside:avoid}
th{font-weight:600;text-align:left;border-bottom:.8pt solid var(--ink);padding:1mm 2mm 1mm 0}
td{border-bottom:.5pt solid var(--hair);padding:1mm 2mm 1mm 0;vertical-align:top}
pre{white-space:pre-wrap;font:400 7.2pt/10pt "Geist Mono",monospace;background:#f6f5f2;padding:2.4mm 3mm;margin:1.6mm 0 3mm}
pre code{background:none;padding:0;font:inherit}
.back{break-before:page}
.appendix-b table{font-size:7pt;line-height:9.6pt}
"""
FONT = (
    '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600'
    '&family=Geist+Mono:wght@400;500&display=block" rel="stylesheet">'
)


def render(text):
    # Keep the line breaks of the method blocks.
    text = re.sub(r"^(> .*\S)$", r"\1  ", text, flags=re.M)
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = re.sub(r"<p><em>((?:Figure|Table) )", r'<p class="cap"><em>\1', html)
    return re.sub(r'<p>(<img [^>]*>)</p>\s*(<p class="cap">.*?</p>)', r"<figure>\1\2</figure>", html, flags=re.S)


source = (OUT / "draft.md").read_text()
head, rest = source.split("## Abstract", 1)
abstract, body = rest.split("## 1. Introduction", 1)
title, subtitle = re.match(r"# (.*?): (.*)", head).groups()
authors = re.findall(r"^(\w[^,\n]*), (Independent, .*)$", head, flags=re.M)
author_html = "".join(f"<div><b>{n}</b><span>{a}</span></div>" for n, a in authors)
front, back = body.split("## Code and Data", 1)
b_start = back.index("## Appendix B.")
b_end = back.index("## Appendix C.")
back_html = (
    render("## Code and Data" + back[:b_start])
    + '<div class="appendix-b">'
    + render(back[b_start:b_end])
    + "</div>"
    + render(back[b_end:])
)
page = (
    f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>{FONT}<style>{CSS}</style></head><body>'
    '<div class="top"><span>(Swarm Alignment Hackathon)</span><span>With Apart Research, 2026</span></div>'
    f'<h1>{title}</h1><div class="sub">{subtitle}</div><div class="authors">{author_html}</div>'
    f'<div class="abstract"><span class="label">(Abstract)</span>{render(abstract)}</div>'
    f"{render('## 1. Introduction' + front)}"
    f'<div class="back">{back_html}</div></body></html>'
)
(OUT / "report.html").write_text(page)
target = OUT / "The_Monitor_Was_Reading_the_Credits.pdf"
subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
     f"--print-to-pdf={target}", f"file://{OUT / 'report.html'}"],
    capture_output=True, check=True,
)  # fmt: skip
print("wrote", target)
