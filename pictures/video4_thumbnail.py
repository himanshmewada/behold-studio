"""
thumbnail_breaks_fraction.py — YouTube SHORT thumbnail, 1080x1920 (9:16).

    manim -s thumbnail_breaks_fraction.py ThumbnailSquare      # recommended
    manim -s thumbnail_breaks_fraction.py ThumbnailDescent     # nested descent
    manim -s thumbnail_breaks_fraction.py ThumbnailNoFraction  # text-forward
    manim -s thumbnail_breaks_fraction.py "*"                  # all three

PNGs land under media/images/. PREVIEW = True renders 540x960 for a shelf-size
legibility check. Use -s, not -p/-q: these scenes have no animations.

THE PICTURE IS THE ACTUAL PROOF
------------------------------
Tennenbaum's dissection, drawn to scale from a = sqrt(2)*b:
    big square       side A
    two b-squares    side B = A/sqrt(2), in opposite corners
    overlap          side 2B - A, centred              (counted twice)
    two gaps         side A - B, other two corners     (missed entirely)
Because 2B^2 = A^2, the double-count must cancel the gaps:
    (2b - a)^2 = 2(a - b)^2
Same equation, smaller integers -> infinite descent -> contradiction.
Each descent shrinks by exactly sqrt(2) - 1 = 0.41421356...
Both identities are asserted at build time, not eyeballed.

SHORTS SAFE ZONE
----------------
Shorts overlays sit along the right edge and the bottom ~20%. All type here
stays above y = -4.4 (77% down) and inside x in [-3.9, 3.9].
"""

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
INK = "#f1eff9"
DIM = "#8f8bad"
BLUE = "#4d7cff"
CYAN = "#00e5d0"
MAGENTA = "#ff2d95"
GOLD = "#ffc233"
ACID = "#b6ff3d"
LEVELS = ["#4d7cff", "#00e5d0", "#b6ff3d", "#ffc233", "#ff2d95", "#a06bff"]

SHRINK = np.sqrt(2) - 1
COL_W = 7.40


# ------------------------------------------------------------------ helpers
def P3(p):
    """Accept (x, y) or (x, y, z); always hand manim a 3-vector."""
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
    """Width clamp without deprecated setters."""
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def tracked(s, size, color, tracking=0.10, weight=NORMAL, space=0.30):
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


def pill(s, size=30, color=ACID, tracking=0.12):
    t = tracked(s, size, color, tracking, weight=BOLD)
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


def stack(mobs, top, buff=0.34):
    """Centre-aligned column from real heights. Rows cannot collide."""
    y = top
    for m in mobs:
        m.move_to([0.0, y, 0.0], aligned_edge=UP)
        y -= m.height + buff
    return VGroup(*mobs)


def backdrop(scene, glow_at=(0.0, 0.30)):
    c = P3(glow_at)
    bg = Rectangle(width=9.4, height=16.4, stroke_width=0)
    bg.set_fill(color=["#141430", "#05050c"], opacity=1)
    scene.add(bg)

    lattice = VGroup()
    for i in range(-9, 10):
        for j in range(-16, 17):
            p = np.array([i * 0.5, j * 0.5, 0.0])
            if abs(p[0]) < 4.6 and abs(p[1]) < 8.1:
                lattice.add(Dot(p, radius=0.018, color=DIM, fill_opacity=0.14))
    scene.add(lattice)

    halo = VGroup(
        *[
            Square(
                side_length=s, stroke_width=0, fill_color=BLUE, fill_opacity=o
            ).move_to(c)
            for s, o in ((8.6, 0.030), (7.0, 0.036), (5.8, 0.040))
        ]
    )
    scene.add(halo)


# ----------------------------------------------------------------- geometry
def dissection(A, center):
    """Exact corner placement for the Tennenbaum figure."""
    C = P3(center)
    B = A / np.sqrt(2.0)
    d = (A - B) / 2.0
    g = {
        "A": A,
        "B": B,
        "C": C,
        "s1": C + np.array([-d, d, 0.0]),
        "s2": C + np.array([d, -d, 0.0]),
        "ov": 2.0 * B - A,
        "gap": A - B,
        "gTR": C + np.array([B / 2, B / 2, 0.0]),
        "gBL": C - np.array([B / 2, B / 2, 0.0]),
    }
    assert abs(2 * B**2 - A**2) < 1e-9, "2b^2 must equal a^2"
    assert abs(g["ov"] ** 2 - 2 * g["gap"] ** 2) < 1e-9, "(2b-a)^2 must equal 2(a-b)^2"
    assert abs(g["ov"] / A - SHRINK) < 1e-12, "descent ratio must be sqrt(2)-1"
    return g


def figure(g, labels=True, lab_scale=1.0):
    A, B, C = g["A"], g["B"], g["C"]

    big = Square(
        side_length=A,
        stroke_color=BLUE,
        stroke_width=4,
        fill_color=BLUE,
        fill_opacity=0.08,
    ).move_to(C)
    s1 = Square(
        side_length=B,
        stroke_color=GOLD,
        stroke_width=3,
        fill_color=GOLD,
        fill_opacity=0.20,
    ).move_to(g["s1"])
    s2 = Square(
        side_length=B,
        stroke_color=GOLD,
        stroke_width=3,
        fill_color=GOLD,
        fill_opacity=0.20,
    ).move_to(g["s2"])

    ov_glow = Square(
        side_length=g["ov"] * 1.5, stroke_width=0, fill_color=MAGENTA, fill_opacity=0.14
    ).move_to(C)
    ov = Square(
        side_length=g["ov"],
        stroke_color=MAGENTA,
        stroke_width=3,
        fill_color=MAGENTA,
        fill_opacity=0.45,
    ).move_to(C)
    gTR = Square(
        side_length=g["gap"],
        stroke_color=CYAN,
        stroke_width=3,
        fill_color=CYAN,
        fill_opacity=0.34,
    ).move_to(g["gTR"])
    gBL = Square(
        side_length=g["gap"],
        stroke_color=CYAN,
        stroke_width=3,
        fill_color=CYAN,
        fill_opacity=0.34,
    ).move_to(g["gBL"])

    parts = VGroup(big, s1, s2, ov_glow, gTR, gBL, ov)

    if not labels:
        return parts

    twice = MathTex(r"\times 2", font_size=int(56 * lab_scale), color=INK).move_to(C)
    m1 = Text("missed", font_size=int(28 * lab_scale), color=INK).move_to(g["gTR"])
    m2 = Text("missed", font_size=int(28 * lab_scale), color=INK).move_to(g["gBL"])
    a_lab = MathTex(r"a", font_size=int(48 * lab_scale), color=BLUE)
    a_lab.move_to(C + np.array([-(A / 2 + 0.42), 0.0, 0.0]))
    b_lab = MathTex(r"b", font_size=int(48 * lab_scale), color=GOLD)
    b_lab.move_to(C + np.array([-(A - B) / 2, A / 2 + 0.42, 0.0]))
    return VGroup(parts, twice, m1, m2, a_lab, b_lab)


def nested(center, A, levels=6):
    """Concentric a-squares: the descent, shrinking by sqrt(2)-1 each level."""
    C, s, g = P3(center), A, VGroup()
    for i in range(levels):
        g.add(
            Square(
                side_length=s,
                stroke_color=LEVELS[i % len(LEVELS)],
                stroke_width=3.2 if i == 0 else 2.4,
                stroke_opacity=0.95 if i == 0 else 0.80,
                fill_opacity=0,
            ).move_to(C)
        )
        s *= SHRINK
    print(
        f"  descent: {levels} levels, sides "
        + ", ".join(f"{A * SHRINK**i:.3f}" for i in range(levels))
    )
    return g


# ============================================================ 1 · THE SQUARE
class ThumbnailSquare(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(0.0, 0.30))

        kick = pill("ONE PICTURE PROOF", 30, ACID)
        hero = fit(
            MathTex(r"\sqrt{2} \neq \frac{a}{b}", font_size=170, color=GOLD), COL_W
        )
        self.add(stack([kick, hero], top=7.05, buff=0.46))

        g = dissection(5.80, (0.0, 0.30))
        self.add(figure(g))
        print(
            f"  figure: a={g['A']:.3f} b={g['B']:.3f} "
            f"overlap={g['ov']:.3f} gap={g['gap']:.3f}"
        )

        eq = fit(MathTex(r"(2b-a)^2 = 2(a-b)^2", font_size=54, color=CYAN), COL_W)
        eq.move_to([0.0, -3.55, 0.0])
        foot = fit(
            Text("smaller whole numbers, forever", font_size=34, color=DIM), COL_W
        )
        foot.move_to([0.0, -4.35, 0.0])
        self.add(eq, foot)


# =========================================================== 2 · THE DESCENT
class ThumbnailDescent(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(0.0, -0.60))

        kick = pill("ONE PICTURE PROOF", 30, ACID)
        l1 = fit(Text("SMALLER", font_size=150, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("FOREVER", font_size=150, color=GOLD, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=7.05, buff=0.32))

        g = dissection(5.60, (0.0, -0.60))
        base = figure(g, labels=False)
        base.set_stroke(opacity=0.30).set_fill(opacity=0.10)
        self.add(base, nested((0.0, -0.60), 5.60, levels=6))

        ratio = fit(
            MathTex(r"\sqrt{2}-1 = 0.41421\ldots", font_size=50, color=CYAN), COL_W
        )
        ratio.move_to([0.0, -3.95, 0.0])
        foot = fit(Text("every step, smaller integers", font_size=32, color=DIM), COL_W)
        foot.move_to([0.0, -4.60, 0.0])
        self.add(ratio, foot)


# ======================================================== 3 · NO FRACTION FITS
class ThumbnailNoFraction(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(0.0, -2.20))

        kick = pill("ONE PICTURE PROOF", 30, ACID)
        l1 = fit(Text("NO", font_size=132, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("FRACTION", font_size=152, color=GOLD, weight=BOLD), COL_W)
        l3 = fit(Text("FITS.", font_size=152, color=GOLD, weight=BOLD), COL_W)
        m = fit(MathTex(r"\sqrt{2} \neq \frac{a}{b}", font_size=76, color=CYAN), 5.0)
        self.add(stack([kick, l1, l2, l3, m], top=7.05, buff=0.28))

        g = dissection(3.80, (0.0, -2.20))
        self.add(figure(g, labels=True, lab_scale=0.72))
        print(
            f"  figure: a={g['A']:.3f} b={g['B']:.3f} "
            f"overlap={g['ov']:.3f} gap={g['gap']:.3f}"
        )
