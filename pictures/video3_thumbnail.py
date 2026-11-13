"""
thumbnail_irrational.py — YouTube thumbnails, 1280x720, computed not drawn.

    manim -s thumbnail_irrational.py ThumbnailMostIrrational   # recommended
    manim -s thumbnail_irrational.py ThumbnailCeiling          # the proof chart
    manim -s thumbnail_irrational.py ThumbnailAllOnes          # continued fraction
    manim -s thumbnail_irrational.py "*"                       # all three

PNGs land under media/images/. PREVIEW = True renders 320x180 for a feed-size
legibility check. Use -s, not -p/-q: these scenes have no animations.

THE PICTURES ARE THE ACTUAL MATHEMATICS
--------------------------------------
ThumbnailMostIrrational  a golden-angle seed head, r = c*sqrt(n),
                         theta = n * 137.5077640 deg, with the two parastichy
                         families traced. They contain EXACTLY 34 and 55
                         spirals (asserted), because seeds k, k+F, k+2F, ...
                         share a residue mod F.
ThumbnailCeiling         |x - p/q| * q^2 against log10(q) for the convergents
                         of phi, sqrt(2) and pi. phi rides the Hurwitz line
                         1/sqrt(5) = 0.4472136 and never dips; pi dives at
                         355/113. Every point is computed from the continued
                         fraction, never placed by hand.
ThumbnailAllOnes         phi = 1 + 1/(1 + 1/(1 + ...)), the continued fraction
                         made entirely of ones, with its convergents below:
                         ratios of consecutive Fibonacci numbers.
"""

import numpy as np
from manim import *

# ------------------------------------------------------------------- canvas
PREVIEW = False
config.pixel_width = 320 if PREVIEW else 1280
config.pixel_height = 180 if PREVIEW else 720
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30

# ------------------------------------------------------------------ palette
BG      = "#07070f"
INK     = "#f1eff9"
DIM     = "#8f8bad"
BLUE    = "#4d7cff"
CYAN    = "#2ee6d6"
MAGENTA = "#ff2d95"
GOLD    = "#ffc233"
ACID    = "#b6ff3d"
SEED    = ["#fff3b0", "#ffd166", "#ffa62b", "#ff6b35",
           "#ef476f", "#b5179e", "#7209b7", "#3a86ff"]

LEFT_X  = -7.30
PHI     = (1 + np.sqrt(5)) / 2
HURWITZ = 1 / np.sqrt(5)


# ------------------------------------------------------------------ helpers
def P3(p):
    """Accept (x, y) or (x, y, z); always hand manim a 3-vector."""
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def lerp_hex(h1, h2, t):
    a = np.array([int(h1[i:i + 2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i:i + 2], 16) for i in (1, 3, 5)], float)
    return "#%02x%02x%02x" % tuple(np.round(a + (b - a) * t).astype(int))


def ramp_at(u, ramp=SEED):
    x = float(np.clip(u, 0, 1)) * (len(ramp) - 1)
    i = min(int(np.floor(x)), len(ramp) - 2)
    return lerp_hex(ramp[i], ramp[i + 1], x - i)


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


def pill(s, size=26, color=ACID, tracking=0.11):
    t = tracked(s, size, color, tracking, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.16, width=t.width + 0.60, height=t.height + 0.36,
        stroke_color=color, stroke_width=1.8, stroke_opacity=0.85,
        fill_color=color, fill_opacity=0.12,
    )
    t.move_to(box.get_center())
    return VGroup(box, t)


def stack(mobs, top, x=LEFT_X, buff=0.30):
    y = top
    for m in mobs:
        m.move_to([x, y, 0.0], aligned_edge=UL)
        y -= m.height + buff
    return VGroup(*mobs)


def center_block(mobs, y, x=LEFT_X, buff=0.30):
    total = sum(m.height for m in mobs) + buff * (len(mobs) - 1)
    return stack(mobs, y + total / 2.0, x=x, buff=buff)


def backdrop(scene, glow_at=(3.9, 0.1)):
    c = P3(glow_at)
    bg = Rectangle(width=16.4, height=9.4, stroke_width=0)
    bg.set_fill(color=["#141430", "#05050c"], opacity=1)
    scene.add(bg)

    lattice = VGroup()
    for i in range(-16, 17):
        for j in range(-9, 10):
            p = np.array([i * 0.5, j * 0.5, 0.0])
            if abs(p[0]) < 8.1 and abs(p[1]) < 4.6:
                lattice.add(Dot(p, radius=0.014, color=DIM, fill_opacity=0.13))
    scene.add(lattice)

    halo = VGroup(*[
        Circle(radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o).move_to(c)
        for r, o in ((4.4, 0.045), (3.4, 0.05), (2.4, 0.045))
    ])
    scene.add(halo)


# ------------------------------------------------------------------- math
def convergents(cf, count):
    out = []
    for i in range(1, count + 1):
        terms = cf[:i]
        p, q = terms[-1], 1
        for a in reversed(terms[:-1]):
            p, q = a * p + q, p
        out.append((p, q))
    return out


CF_PHI = [1] * 12
CF_SQ2 = [1] + [2] * 8
CF_PI  = [3, 7, 15, 1, 292, 1, 1]


def quality(pairs, x):
    return [(q, abs(x - p / q) * q * q) for p, q in pairs]


# ------------------------------------------------------------------- marks
def seed_head(target, R, n=430):
    C = P3(target)
    turns = 1 / PHI ** 2
    c = R / np.sqrt(n - 1)
    dr = 0.40 * c * np.sqrt(PI)
    k = np.arange(n, dtype=float)
    r, a = c * np.sqrt(k), TAU * turns * k
    pts = np.column_stack([C[0] + r * np.cos(a), C[1] + r * np.sin(a), np.zeros(n)])

    fams = VGroup()
    for step, col in ((34, CYAN), (55, MAGENTA)):
        fam = VGroup()
        for j in range(step):
            idx = np.arange(j, n, step)
            if len(idx) < 3:
                continue
            cur = VMobject(stroke_color=col, stroke_width=1.4, stroke_opacity=0.30)
            cur.set_points_smoothly(pts[idx])
            fam.add(cur)
        assert len(fam) == step, f"expected {step} spirals, built {len(fam)}"
        print(f"  parastichy family F={step}: {len(fam)} spirals")
        fams.add(fam)

    dots = VGroup(*[
        Dot(pts[i], radius=dr, color=ramp_at(i / (n - 1)), stroke_width=0)
        for i in range(n)
    ])
    ring = Circle(radius=R * 1.03, stroke_color=DIM, stroke_width=1.2,
                  stroke_opacity=0.22).move_to(C)
    return VGroup(ring, fams, dots)


def hurwitz_chart(target):
    C = P3(target)
    LX = float(np.log10(230))
    ax = Axes(x_range=[0, LX, 1], y_range=[0, 1.0, 0.2],
              x_length=6.2, y_length=3.8, tips=False,
              axis_config={"stroke_color": DIM, "stroke_width": 2,
                           "tick_size": 0.05, "include_numbers": False}).move_to(C)
    P = lambda q, v: ax.c2p(float(np.log10(q)), v)

    ceil = DashedLine(P(1, HURWITZ), P(230, HURWITZ), color=GOLD,
                      stroke_width=2, stroke_opacity=0.7, dash_length=0.09)
    ceil_lab = MathTex(r"\tfrac{1}{\sqrt{5}}", font_size=26, color=GOLD)
    ceil_lab.next_to(ceil, LEFT, buff=0.10)

    series = [
        (quality(convergents(CF_PHI, 10)[2:], PHI), GOLD, r"\varphi"),
        (quality(convergents(CF_SQ2, 6)[1:], np.sqrt(2)), CYAN, r"\sqrt{2}"),
        (quality(convergents(CF_PI, 4), PI), MAGENTA, r"\pi"),
    ]
    plots, labels = VGroup(), VGroup()
    for data, col, name in series:
        pts = [P(q, v) for q, v in data]
        seg = VGroup(*[Line(pts[i], pts[i + 1], stroke_color=col,
                            stroke_width=2.6, stroke_opacity=0.9)
                       for i in range(len(pts) - 1)])
        dd = VGroup(*[Dot(p, radius=0.045, color=col) for p in pts])
        plots.add(VGroup(seg, dd))
        labels.add(MathTex(name, font_size=30, color=col).next_to(pts[-1], UR, buff=0.08))

    xlabels = VGroup(*[
        Text(s, font_size=18, color=DIM).next_to(P(q, 0), DOWN, buff=0.12)
        for q, s in ((1, "1"), (10, "10"), (100, "100"))
    ])
    ylab = MathTex(r"\left|x-\tfrac{p}{q}\right|\cdot q^2", font_size=24, color=DIM)
    ylab.next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
    xlab = Text("denominator q", font_size=18, color=DIM).next_to(ax, DOWN, buff=0.30)

    never = Text("never dips", font_size=24, color=GOLD, weight=BOLD)
    never.next_to(P(20, HURWITZ), UP, buff=0.14)

    return VGroup(ax, ceil, ceil_lab, plots, labels, xlabels, ylab, xlab, never)


def continued_fraction(target):
    cf = MathTex(r"\varphi = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}}",
                 font_size=64, color=GOLD)
    fit(cf, 4.6)
    cf.move_to(P3(target))
    return cf


# ====================================================== 1 · MOST IRRATIONAL
class ThumbnailMostIrrational(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(3.9, 0.1))

        kick = pill("THE GOLDEN RATIO", 26, ACID)
        l1 = fit(Text("MOST", font_size=150, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("IRRATIONAL", font_size=150, color=GOLD, weight=BOLD), 6.9)
        foot = fit(MathTex(r"\varphi = 1.6180339887\ldots", font_size=40, color=CYAN), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))

        self.add(seed_head((3.9, 0.1), 2.55))
        cap = Text("34 and 55 spirals, from one angle", font_size=24, color=DIM)
        cap.move_to([3.9, -2.95, 0.0])
        self.add(cap)


# ========================================================== 2 · THE CEILING
class ThumbnailCeiling(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(3.6, -0.1))

        kick = pill("THE GOLDEN RATIO", 26, ACID)
        l1 = fit(Text("MOST", font_size=150, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("IRRATIONAL", font_size=150, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("it never beats the line", font_size=38, color=INK), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))

        self.add(hurwitz_chart((3.6, -0.1)))


# ========================================================= 3 · ALL ONES
class ThumbnailAllOnes(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(3.9, 0.3))

        kick = pill("THE GOLDEN RATIO", 26, ACID)
        l1 = fit(Text("ALL", font_size=150, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("ONES", font_size=150, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("the worst possible recipe", font_size=38, color=INK), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))

        self.add(continued_fraction((3.9, 0.35)))

        conv = MathTex(r"\tfrac{1}{1},\ \tfrac{2}{1},\ \tfrac{3}{2},\ \tfrac{5}{3},"
                       r"\ \tfrac{8}{5},\ \tfrac{13}{8},\ \tfrac{21}{13},\ \tfrac{34}{21}",
                       font_size=32, color=CYAN)
        fit(conv, 5.6)
        conv.move_to([3.9, -2.55, 0.0])
        clab = Text("its best guesses are Fibonacci ratios", font_size=20, color=DIM)
        clab.move_to([3.9, -2.05, 0.0])
        self.add(conv, clab)

        # receipt: the convergents of phi really are consecutive Fibonacci ratios
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        dens = [q for _, q in convergents(CF_PHI, 10)]
        assert dens == fib[:len(dens)], dens
        print("  phi convergent denominators:", dens)
