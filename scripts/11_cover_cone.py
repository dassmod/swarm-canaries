"""Project image: a network drawn as a folded surface, lit like a conic gradient.

Owner: Dastan.

Each node is a cone tip. Each edge is a bright ridge. Between two ridges the surface falls into shade.
The image is decorative and carries no data.

Run:
  .venv/bin/python scripts/11_cover_cone.py

Writes report/assets/cone_ground.png, cone_single.png, cone_white.png and cover_f.html. A browser renders the HTML to PNG.
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report" / "assets"
W, H = 3200, 1800
S = 2

# name: (x, y, weight), in a 1600 by 900 frame
NODES = {
    "hub": (940, 450, 2.6),
    "b": (560, 450, 1.0),
    "c": (660, 170, 0.8),
    "d": (680, 740, 0.8),
    "e": (290, 245, 0.8),
    "f": (250, 665, 0.8),
}
# Off-frame points give the outer nodes ridges that leave the picture.
OUTSIDE = {
    "o1": (-200, 450),
    "o2": (820, -300),
    "o3": (860, 1200),
    "o4": (-200, 60),
    "o5": (-200, 840),
    "o6": (240, -300),
    "o7": (200, 1200),
}
EDGES = [
    ("hub", "b"), ("hub", "c"), ("hub", "d"), ("b", "c"), ("b", "d"), ("b", "e"), ("b", "f"), ("c", "e"), ("d", "f"),
    ("e", "f"), ("c", "o2"), ("d", "o3"), ("b", "o1"), ("e", "o4"), ("f", "o5"), ("e", "o6"), ("f", "o7"),
]  # fmt: skip


def position(name):
    return NODES[name][:2] if name in NODES else OUTSIDE[name]


yy, xx = np.mgrid[0:H, 0:W]
xx = (xx + 0.5) / S
yy = (yy + 0.5) / S
total = np.zeros((H, W))
value = np.zeros((H, W))
for name, (x, y, weight) in NODES.items():
    angles = []
    for a, b in EDGES:
        if name in (a, b):
            other = position(b if a == name else a)
            angles.append(math.atan2(other[1] - y, other[0] - x))
    angles = np.sort(np.array(angles))
    ring = np.concatenate([angles, [angles[0] + 2 * math.pi]])
    theta = np.arctan2(yy - y, xx - x)
    theta = np.where(theta < angles[0], theta + 2 * math.pi, theta)
    k = np.clip(np.searchsorted(ring, theta, side="right") - 1, 0, len(angles) - 1)
    gap = ring[k + 1] - ring[k]
    t = (theta - ring[k]) / gap
    u = 1 - np.abs(2 * t - 1)  # 0 on a ridge, 1 in the middle of a gap
    depth = np.clip(gap / math.pi, 0, 1) ** 0.75
    f = 1 - u * depth
    d = np.hypot(xx - x, yy - y) + 1.5
    w = weight / d**3.2
    total += w
    value += w * f
v = value / total
v = v**1.7
# The light falls from left to right, as in a single conic gradient.
light = 0.3 + 0.7 * np.clip(1.08 - xx / 1500, 0, 1) ** 0.8
v = np.clip(v * light + 0.035, 0, 1)
stops = np.array([0.0, 0.32, 0.68, 1.0])
ramp = np.array([[34, 27, 28], [98, 89, 88], [176, 170, 168], [255, 255, 255]], dtype=float)
rgb = np.stack([np.interp(v, stops, ramp[:, c]) for c in range(3)], axis=-1)
rng = np.random.default_rng(0)
rgb = np.clip(rgb + rng.normal(0, 1.1, rgb.shape), 0, 255).astype(np.uint8)  # dither against banding
Image.fromarray(rgb).save(OUT / "cone_ground.png")

(OUT / "cover_f.html").write_text("""<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0}html,body{width:1600px;height:900px;overflow:hidden}
body{background:url(cone_ground.png) 0 0/1600px 900px;color:#fff;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}
.t{position:absolute;left:1120px;width:440px}
h1{font-size:42px;line-height:48px;font-weight:600;letter-spacing:-.012em}
p{font-size:24px;line-height:33px;font-weight:300;color:#ffffffd6}
p b{font-weight:500;color:#fff}
small{position:absolute;left:1120px;bottom:48px;font-size:17px;line-height:24px;font-weight:300;color:#ffffffa8}
</style></head><body>
<div class="t" style="bottom:486px"><h1>The Monitor Was<br>Reading the Credits</h1></div>
<div class="t" style="top:486px"><p><b>Canaries and proof of transfer<br>between AI agents</b><br>Dastan Modubash<br>Nikita Stanchenkov</p></div>
<small>Swarm Alignment Hackathon<br>Apart Research, 2026</small>
</body></html>
""")
# One cone for the slides that carry a statement: one tip, light to the left, shade to the right.
TIP = (620, 450)
angle = np.abs(np.arctan2(yy - TIP[1], xx - TIP[0]))
one = (angle / math.pi) ** 2.1
one = np.clip(one * (0.3 + 0.7 * np.clip(1.08 - xx / 1500, 0, 1) ** 0.5) + 0.035, 0, 1)
rgb = np.stack([np.interp(one, stops, ramp[:, c]) for c in range(3)], axis=-1)
rgb = np.clip(rgb + rng.normal(0, 1.1, rgb.shape), 0, 255).astype(np.uint8)
Image.fromarray(rgb).save(OUT / "cone_single.png")
# The same cone on white: white toward the text, soft shade away from it.
shade = (angle / math.pi) ** 2.6
white = np.stack([255 - shade * c for c in (150, 155, 158)], axis=-1)
white = np.clip(white + rng.normal(0, 0.8, white.shape), 0, 255).astype(np.uint8)
Image.fromarray(white).save(OUT / "cone_white.png")
print("wrote cone_ground.png, cone_single.png, cone_white.png and cover_f.html")
