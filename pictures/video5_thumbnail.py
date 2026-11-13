"""
thumbnail_pascal.py — YouTube SHORT thumbnail, 1080x1920 (9:16).

    manim -s thumbnail_pascal.py ThumbnailHidden       # recommended
    manim -s thumbnail_pascal.py ThumbnailParity       # the rule as a question
    manim -s thumbnail_pascal.py ThumbnailDimension    # the payoff number
    manim -s thumbnail_pascal.py "*"                   # all three

PNGs land under media/images/. PREVIEW = True renders 540x960 for a shelf-size
legibility check. Use -s, not -p/-q: these scenes have no animations.

LAYOUT RULE
-----------
One stack() call per zone, top-anchored from real mobject heights. Never mix a
centre-anchored move_to with a top-anchored stack in the same region.

THE PICTURE IS THE REAL CONSTRUCTION
-----------------------------------
Cell (n,k) is lit iff C(n,k) is odd, which by Lucas mod 2 is exactly (k AND n)
== k. Every bit is cross-checked against math.comb at import. In the coloured
variant, rows 0..31 are the top copy and rows 32..63 split at k = 32 into the
left and right copies -- 243 odd cells each (3^5), asserted. Only ODD cells
take a hue; even cells stay dark so the fractal's holes survive.

SHORTS SAFE ZONE
----------------
Type stays above y = -3.8 and inside x in [-3.9, 3.9], clear of the right-edge
buttons and the bottom caption block.
"""

from math import comb
import numpy as np
from manim import *

# ------------------------------------------------------------------- canvas
PREVIEW = False
config.pixel_width = 540 if PREVIEW else 1080
config.pixel_height = 960 if PREVIEW else 1920
config.frame_width = 9
config.frame_height = 16
config.frame_rate = 30

# ------------------------------------------------------------------ palette
BG = "#07070f"
SURFACE = "#15152a"
EDGE = "#2b2b48"
INK = "#f1eff9"
DIM = "#8f8bad"
GOLD = "#ffc233"
CYAN = "#00e5d0"
MAGENTA = "#ff2d95"
ACID = "#b6ff3d"
THIRDS = ["#ffc233", "#00e5d0", "#ff2d95"]

N_ROWS = 64
COL_W = 7.40
HEAD_TOP = 7.10
FOOT_TOP = -3.35
GAP_TOP = 3.05  # gasket apex
PITCH = 0.108


# ------------------------------------------------------------------ helpers
def P3(p):
    """Accept (x, y) or (x, y, z); always hand manim a 3-vector."""
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def tracked(s, size, color, tracking=0.12, weight=BOLD, space=0.30):
    g, x = VGroup(), 0.0
    for ch in s:
        if ch == " ":
            x += space + tracking
            continue
        m = Text(ch, font_size=size, color=color, weight=weight)
        m.move_to([x, 0.0, 0.0], aligned_edge=LEFT)
        g.add(m)
        x += m.width + tracking
    return g.move_to(ORIGIN)


def pill(s, size=30, color=ACID):
    t = tracked(s, size, color)
    box = RoundedRectangle(
        corner_radius=0.18,
        width=t.width + 0.70,
        height=t.height + 0.42,
        stroke_color=color,
        stroke_width=2.0,
        stroke_opacity=0.85,
        fill_color=color,
        fill_opacity=0.12,
    )
    t.move_to(box.get_center())
    return VGroup(box, t)


def stack(mobs, top, buff=0.30):
    """The ONLY layout primitive: top-anchored, driven by real heights."""
    y = top
    for m in mobs:
        m.move_to([0.0, y, 0.0], aligned_edge=UP)
        y -= m.height + buff
    return VGroup(*mobs)


def backdrop(scene, glow_at=(0.0, 0.10)):
    c = P3(glow_at)
    bg = Rectangle(width=9.4, height=16.4, stroke_width=0)
    bg.set_fill(color=["#141430", "#05050c"], opacity=1)
    scene.add(bg)

    lattice = VGroup()
    for i in range(-9, 10):
        for j in range(-16, 17):
            p = np.array([i * 0.5, j * 0.5, 0.0])
            if abs(p[0]) < 4.6 and abs(p[1]) < 8.1:
                lattice.add(Dot(p, radius=0.017, color=DIM, fill_opacity=0.13))
    scene.add(lattice)

    halo = VGroup(
        *[
            Circle(radius=r, stroke_width=0, fill_color=GOLD, fill_opacity=o).move_to(c)
            for r, o in ((4.4, 0.030), (3.3, 0.034), (2.2, 0.030))
        ]
    )
    scene.add(halo)


# --------------------------------------------------------- verified parity
def verify():
    for n in range(N_ROWS):
        row = [comb(n, k) % 2 for k in range(n + 1)]
        assert row == [1 if (k & n) == k else 0 for k in range(n + 1)], n
        assert sum(row) == 2 ** bin(n).count("1"), n
    for m in range(1, 7):
        total = sum(comb(n, k) % 2 for n in range(2**m) for k in range(n + 1))
        assert total == 3**m, m
    print(f"  Lucas mod 2 verified against math.comb for all {N_ROWS} rows")
    print(f"  dimension log3/log2 = {np.log(3) / np.log(2):.7f}")


verify()


def gasket(colored=False, top_y=GAP_TOP, pitch=PITCH):
    row_h = pitch * np.sqrt(3) / 2
    cell = pitch * 0.90
    flat, evens = VGroup(), VGroup()
    thirds = [VGroup(), VGroup(), VGroup()]

    for n in range(N_ROWS):
        for k in range(n + 1):
            odd = (k & n) == k
            pos = np.array([(k - n / 2.0) * pitch, top_y - n * row_h, 0.0])
            if odd:
                idx = 0 if n < 32 else (1 if k < 32 else 2)
                col = THIRDS[idx] if colored else GOLD
            else:
                idx, col = None, SURFACE
            c = Square(
                side_length=cell,
                stroke_width=0,
                fill_color=col,
                fill_opacity=0.95 if odd else 0.55,
            ).move_to(pos)
            flat.add(c)
            if odd:
                thirds[idx].add(c)
            else:
                evens.add(c)

    assert [len(t) for t in thirds] == [243, 243, 243], [len(t) for t in thirds]
    print(
        f"  gasket: {len(flat)} cells, {len(flat) - len(evens)} odd, "
        f"thirds 243/243/243 (3^5 each)"
    )
    return flat


# ============================================================ 1 · THE HIDDEN
class ThumbnailHidden(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("PASCAL'S TRIANGLE", 30, ACID)
        l1 = fit(Text("HIDDEN", font_size=132, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("FRACTAL", font_size=132, color=GOLD, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=HEAD_TOP, buff=0.30))

        self.add(gasket(colored=False))

        foot = fit(Text("colour the odd numbers", font_size=34, color=CYAN), COL_W)
        self.add(stack([foot], top=FOOT_TOP))


# ============================================================= 2 · THE RULE
class ThumbnailParity(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("PASCAL'S TRIANGLE", 30, ACID)
        l1 = fit(Text("ODD OR", font_size=128, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("EVEN?", font_size=128, color=GOLD, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=HEAD_TOP, buff=0.30))

        self.add(gasket(colored=False))

        foot = fit(Text("that's the entire rule", font_size=34, color=CYAN), COL_W)
        self.add(stack([foot], top=FOOT_TOP))


# ======================================================== 3 · THE DIMENSION
class ThumbnailDimension(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("PASCAL'S TRIANGLE", 30, ACID)
        hero = fit(Text("1.585", font_size=190, color=GOLD, weight=BOLD), COL_W)
        sub = fit(Text("DIMENSIONS", font_size=78, color=INK, weight=BOLD), COL_W)
        self.add(stack([kick, hero, sub], top=HEAD_TOP, buff=0.28))

        self.add(gasket(colored=True))

        foot = fit(MathTex(r"\frac{\log 3}{\log 2}", font_size=52, color=CYAN), 3.0)
        self.add(stack([foot], top=FOOT_TOP))
