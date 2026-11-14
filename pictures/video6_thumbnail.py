"""
thumbnail_fastest_fall.py — YouTube thumbnails, 1280x720, computed not drawn.
manim -s pictures/video6_thumbnail.py ThumbnailRace    # recommended
manim -s pictures/video6_thumbnail.py ThumbnailDive    # the twist angle
manim -s pictures/video6_thumbnail.py ThumbnailLight   # the proof angle
manim -s pictures/video6_thumbnail.py "*"              # all three
PREVIEW = True renders 320x180 for a feed-size legibility check. Use -s.

THE PICTURE IS THE REAL RACE
----------------------------
Cycloid solved by bisection from (theta - sin theta)/(1 - cos theta) = bx/by.
Time chips are the actual descent times: T_cyc = theta_B*sqrt(R/g),
T_line = 2L/sqrt(2 g by). The cycloid's dip below the finish is measured,
and the light-ray variant is a genuine Snell refraction through layers
whose speeds are sqrt(2 g y). Nothing is placed by hand.
"""

import numpy as np
from manim import *

PREVIEW = False
config.pixel_width = 320 if PREVIEW else 1280
config.pixel_height = 180 if PREVIEW else 720
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30

BG = "#07070f"
INK = "#f1eff9"
DIM = "#8f8bad"
BLUE = "#4d7cff"
CYAN = "#2ee6d6"
MAGENTA = "#ff2d95"
GOLD = "#ffc233"
ACID = "#b6ff3d"
LEFT_X = -7.30
G = 9.81

# figure geometry
A = np.array([0.80, 2.35, 0.0])
BX, BY = 6.3, 2.1
B = A + np.array([BX, -BY, 0.0])


def solve_cycloid(bx, by):
    f = lambda th: (th - np.sin(th)) / (1 - np.cos(th)) - bx / by
    lo, hi = 1e-9, TAU - 1e-9
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    th = 0.5 * (lo + hi)
    return th, by / (1 - np.cos(th))


TH_B, R = solve_cycloid(BX, BY)
T_CYC = TH_B * np.sqrt(R / G)
T_LINE = 2 * np.hypot(BX, BY) / np.sqrt(2 * G * BY)
DIP = 2 * R - BY
BOT = A + np.array([PI * R, -2 * R, 0.0])
assert T_CYC < T_LINE and DIP > 0
print(
    f"  theta_B={TH_B:.4f} R={R:.4f} | cycloid {T_CYC:.2f}s vs line {T_LINE:.2f}s"
    f" | dip {DIP:.3f}"
)


def cyc_point(th):
    return A + np.array([R * (th - np.sin(th)), -R * (1 - np.cos(th)), 0.0])


def cyc_curve(opacity=1.0, width=5.0, color=GOLD):
    th = np.linspace(0, TH_B, 400)
    pts = np.array([cyc_point(t) for t in th])
    m = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    m.set_points_smoothly(pts)
    return m


def P3(p):
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
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


def pill(s, size=26, color=ACID, tracking=0.11):
    t = tracked(s, size, color, tracking, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.16,
        width=t.width + 0.60,
        height=t.height + 0.36,
        stroke_color=color,
        stroke_width=1.8,
        stroke_opacity=0.85,
        fill_color=color,
        fill_opacity=0.12,
    )
    t.move_to(box.get_center())
    return VGroup(box, t)


def chip(s, color=GOLD, size=30):
    t = Text(s, font_size=size, color=color, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.14,
        width=t.width + 0.44,
        height=t.height + 0.26,
        stroke_color=color,
        stroke_width=1.8,
        stroke_opacity=0.9,
        fill_color=BG,
        fill_opacity=0.85,
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
    halo = VGroup(
        *[
            Circle(radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o).move_to(c)
            for r, o in ((4.4, 0.045), (3.4, 0.05), (2.4, 0.045))
        ]
    )
    scene.add(halo)


def endpoints(scene):
    ceiling = DashedLine(
        A + LEFT * 0.3,
        A + RIGHT * (BX + 0.5),
        stroke_color=DIM,
        stroke_width=1.5,
        stroke_opacity=0.45,
        dash_length=0.09,
    )
    a = Dot(A, radius=0.07, color=INK)
    b = Circle(radius=0.15, stroke_color=GOLD, stroke_width=3).move_to(B)
    scene.add(ceiling, a, b)
    return b


# ============================================================ 1 · THE RACE
class ThumbnailRace(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("THE 1696 CHALLENGE", 26, ACID)
        l1 = fit(Text("FASTEST", font_size=150, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("WAY DOWN", font_size=150, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("not the straight line", font_size=38, color=INK), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))
        endpoints(self)
        line = Line(A, B, stroke_color=DIM, stroke_width=2.5, stroke_opacity=0.7)
        cyc = cyc_curve()
        glow = cyc.copy().set_stroke(width=16, opacity=0.15)
        bead = Dot(cyc_point(2.7), radius=0.13, color=GOLD)
        self.add(line, glow, cyc, bead)
        c_line = chip(f"{T_LINE:.2f} s", DIM, 30).move_to(
            0.5 * (A + B) + np.array([-0.3, 0.55, 0])
        )
        c_cyc = chip(f"{T_CYC:.2f} s", GOLD, 34).move_to(
            [BOT[0] + 1.05, BOT[1] - 0.45, 0]
        )
        cap = Text("same start · same finish · same gravity", font_size=24, color=DIM)
        cap.move_to([3.95, -2.35, 0])
        self.add(c_line, c_cyc, cap)


# ============================================================ 2 · THE TWIST
class ThumbnailDive(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("THE FASTEST PATH", 26, ACID)
        l1 = fit(Text("IT DIVES", font_size=140, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("BELOW", font_size=170, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("…and still wins", font_size=40, color=INK), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))
        b = endpoints(self)
        fin = Text("finish", font_size=24, color=GOLD).next_to(b, UP, buff=0.16)
        line = Line(A, B, stroke_color=DIM, stroke_width=2.0, stroke_opacity=0.45)
        cyc = cyc_curve()
        hline = DashedLine(
            [BOT[0] - 1.0, B[1], 0],
            [B[0] + 0.6, B[1], 0],
            stroke_color=DIM,
            stroke_width=1.5,
            dash_length=0.08,
        )
        band = Rectangle(
            width=3.6, height=DIP, stroke_width=0, fill_color=MAGENTA, fill_opacity=0.14
        ).move_to([0.5 * (BOT[0] + B[0]), B[1] - DIP / 2, 0])
        arr = DoubleArrow(
            [BOT[0], B[1], 0],
            [BOT[0], BOT[1], 0],
            buff=0,
            stroke_width=4,
            color=MAGENTA,
            max_tip_length_to_length_ratio=0.14,
        )
        lab = chip(f"+{DIP:.2f} deeper", MAGENTA, 28).next_to(arr, LEFT, buff=0.22)
        cap = Text("depth buys speed", font_size=26, color=DIM)
        cap.move_to([3.95, -2.35, 0])
        self.add(line, band, hline, cyc, arr, lab, fin, cap)


# ============================================================ 3 · THE PROOF
class ThumbnailLight(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("BERNOULLI'S TRICK", 26, ACID)
        l1 = fit(Text("LIGHT", font_size=150, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("KNOWS", font_size=150, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("Snell's law picks the curve", font_size=36, color=INK), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))
        n = 10
        D = 2 * R
        ys = np.linspace(0, D, n + 1)
        vm = np.sqrt(2 * G * 0.5 * (ys[:-1] + ys[1:]))

        def X(k):
            s = k * vm
            return float(np.sum(np.diff(ys) * s / np.sqrt(1 - s * s)))

        lo, hi = 1e-12, 0.999999 / vm.max()
        for _ in range(160):
            mid = 0.5 * (lo + hi)
            if X(mid) < PI * R:
                lo = mid
            else:
                hi = mid
        k = 0.5 * (lo + hi)
        s = k * vm
        xs = np.concatenate([[0.0], np.cumsum(np.diff(ys) * s / np.sqrt(1 - s * s))])
        bands = VGroup()
        for i in range(n):
            bands.add(
                Rectangle(
                    width=6.9,
                    height=ys[i + 1] - ys[i],
                    stroke_width=0,
                    fill_color=BLUE,
                    fill_opacity=0.05 + 0.11 * (i + 1) / n,
                ).move_to([3.95, A[1] - 0.5 * (ys[i] + ys[i + 1]), 0])
            )
        pts = np.column_stack([A[0] + xs, A[1] - ys, np.zeros(n + 1)])
        ray = VMobject(stroke_color=CYAN, stroke_width=4.5)
        ray.set_points_as_corners(pts)
        th = np.linspace(0, PI, 200)
        half = np.array([cyc_point(t) for t in th])
        dash = VMobject(stroke_color=GOLD, stroke_width=3.0, stroke_opacity=0.9)
        dash.set_points_smoothly(half)
        dash = DashedVMobject(dash, num_dashes=26, dashed_ratio=0.55)
        endpoints(self)
        law = MathTex(r"\frac{\sin\theta}{v} = \text{const}", font_size=38, color=ACID)
        law.move_to([3.95, -1.75, 0])
        cap = Text("the fastest slide is a light ray", font_size=24, color=DIM)
        cap.move_to([3.95, -2.35, 0])
        self.add(bands, dash, ray, law, cap)
        print(
            f"  light variant: n={n}, k={k:.5f} (true {1 / (2 * np.sqrt(G * R)):.5f})"
        )
