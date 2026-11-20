"""
thumbnail_never_moves.py — YouTube SHORT thumbnail, 1080x1920 (9:16).
manim -s pictures/video8_thumbnail.py ThumbnailConstant    # recommended
manim -s pictures/video8_thumbnail.py ThumbnailNegative    # the surprise
manim -s pictures/video8_thumbnail.py ThumbnailAlways      # the question
manim -s pictures/video8_thumbnail.py "*"                  # all three

PNGs land under media/images/. PREVIEW = True renders 540x960 for a shelf-size
legibility check. Use -s, not -p/-q: these scenes have no animations.

THE PICTURE IS THE ACTUAL THEOREM
---------------------------------
Same construction as videos/video8.py, rescaled for the vertical frame.
Signed distance d_i(P) = (P - U_i) . n_i with n_i the INWARD unit normal.
The three inward normals sum to zero, so d_1+d_2+d_3 is constant on the
whole plane; at the centroid it equals the altitude h = s*sqrt(3)/2.

The stacked bar is built from the three actual distances. Its top is
asserted to land EXACTLY level with the apex — that dashed line is the
theorem, not decoration. ThumbnailNegative pushes P outside across one
side: exactly one distance flips sign, the signed sum is still h, and
every perpendicular foot still lands on its side segment.

LAYOUT RULE
-----------
One stack() call per zone, top-anchored from real mobject heights.

SHORTS SAFE ZONE
----------------
Overlays eat the right edge and the bottom ~20%. All type stays above
y = -4.4 and inside x in [-3.9, 3.9].
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
SURFACE = "#15152a"
EDGE = "#2b2b48"
INK = "#f1eff9"
DIM = "#8f8bad"
BLUE = "#4d7cff"
CYAN = "#2ee6d6"
GOLD = "#ffc233"
MAGENTA = "#ff2d95"
ACID = "#b6ff3d"
RED = "#ff5252"

COL_W = 7.40
HEAD_TOP = 7.05
ROW_Y = -2.05
FOOT_TOP = -2.70

# ----------------------------------------------------------------- geometry
SIDE = 4.90
H = SIDE * np.sqrt(3.0) / 2.0
RC = SIDE / np.sqrt(3.0)
RI = H / 3.0
TRI_C = np.array([-0.80, -0.15, 0.0])

VERTS = [
    TRI_C + RC * np.array([np.cos(a), np.sin(a), 0.0])
    for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)
]
VA, VB, VC = VERTS
SIDES = [(VB, VC, CYAN), (VA, VB, GOLD), (VC, VA, MAGENTA)]

APEX_Y = VA[1]
BASE_Y = VB[1]
BAR_X, BAR_W = 2.60, 0.62
ARROW_X = 2.02
EPS = 0.16


def inward(U, V):
    e = V - U
    n = np.array([e[1], -e[0], 0.0])
    n /= np.linalg.norm(n)
    if np.dot(TRI_C - U, n) < 0.0:
        n = -n
    return n


NORMALS = [inward(U, V) for U, V, _ in SIDES]


def dists(P):
    return [float(np.dot(P - U, n)) for (U, V, _), n in zip(SIDES, NORMALS)]


def foot(P, U, V):
    e = V - U
    t = float(np.dot(P - U, e) / np.dot(e, e))
    return U + t * e, t


P_IN = TRI_C + 0.45 * RI * np.array([np.cos(0.9), np.sin(0.9), 0.0])
P_ASK = TRI_C + 0.55 * RI * np.array([np.cos(3.6), np.sin(3.6), 0.0])
P_OUT = 0.5 * (VC + VA) - 0.95 * NORMALS[2]

D_IN, D_ASK, D_OUT = dists(P_IN), dists(P_ASK), dists(P_OUT)


def verify():
    rng = np.random.default_rng(11)
    assert np.linalg.norm(np.sum(NORMALS, axis=0)) < 1e-12, "normals must cancel"
    assert abs(APEX_Y - (BASE_Y + H)) < 1e-12, "bar height must equal the altitude"
    for _ in range(300):
        w = rng.random(3)
        w /= w.sum()
        P = w[0] * VA + w[1] * VB + w[2] * VC
        d = dists(P)
        assert min(d) > -1e-12 and abs(sum(d) - H) < 1e-10
        assert abs(sum(0.5 * SIDE * x for x in d) - 0.5 * SIDE * H) < 1e-9
    for P in (P_IN, P_ASK, P_OUT):
        assert abs(sum(dists(P)) - H) < 1e-10, "Viviani fails at a demo point"
        for U, V, _ in SIDES:
            _, t = foot(P, U, V)
            assert -1e-9 <= t <= 1 + 1e-9, "every foot must land on its side"
    assert min(D_IN) > 0.3 and min(D_ASK) > 0.3, "demo lengths must be visible"
    assert sum(1 for x in D_OUT if x < 0) == 1, "exactly one distance flips"
    assert abs(sum(D_IN) - sum(D_OUT)) < 1e-10, "inside and outside must agree"
    print(f"  triangle: s={SIDE:.3f}  h={H:.6f}  inradius={RI:.6f}")
    print(f"  normals |n1+n2+n3| = {np.linalg.norm(np.sum(NORMALS, axis=0)):.2e}")
    print(
        f"  inside  d = {D_IN[0]:.2f}, {D_IN[1]:.2f}, {D_IN[2]:.2f} -> {sum(D_IN):.6f}"
    )
    print(
        f"  ask     d = {D_ASK[0]:.2f}, {D_ASK[1]:.2f}, {D_ASK[2]:.2f} -> {sum(D_ASK):.6f}"
    )
    print(
        f"  outside d = {D_OUT[0]:.2f}, {D_OUT[1]:.2f}, {D_OUT[2]:.2f} -> {sum(D_OUT):.6f}"
    )
    print(f"  bar top {BASE_Y + sum(D_IN):.6f} == apex {APEX_Y:.6f}  [level]")


verify()


# ------------------------------------------------------------------ helpers
def P3(p):
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


def pill(s, size=28, color=ACID):
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


def backdrop(scene, glow_at=(0.0, 0.40)):
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
            Circle(radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o).move_to(c)
            for r, o in ((4.4, 0.030), (3.3, 0.034), (2.2, 0.030))
        ]
    )
    scene.add(halo)


def right_angle(P, U, V, col):
    F, _ = foot(P, U, V)
    v = P - F
    nv = np.linalg.norm(v)
    m = VMobject(stroke_color=col, stroke_width=2.0, stroke_opacity=0.85)
    if nv < 1e-4:
        m.set_points_as_corners([F, F, F])
        return m
    v = v / nv
    e = (V - U) / np.linalg.norm(V - U)
    if np.dot(0.5 * (U + V) - F, e) < 0.0:
        e = -e
    m.set_points_as_corners([F + EPS * e, F + EPS * (e + v), F + EPS * v])
    return m


def values_row(d):
    groups = []
    for i, val in enumerate(d):
        col = RED if val < 0 else SIDES[i][2]
        sw = Square(side_length=0.22, fill_color=col, fill_opacity=1, stroke_width=0)
        lab = MathTex(rf"d_{i + 1}", font_size=30, color=col)
        num = Text(f"{val:.2f}", font_size=30, color=col, weight=BOLD)
        groups.append(VGroup(sw, lab, num).arrange(RIGHT, buff=0.16))
    row = VGroup(*groups).arrange(RIGHT, buff=0.42)
    fit(row, COL_W)
    return row.move_to([0.0, ROW_Y, 0.0])


def figure(P, bar=True):
    d = dists(P)
    tri = Polygon(
        *VERTS,
        stroke_color=INK,
        stroke_width=3.0,
        stroke_opacity=0.9,
        fill_color=BLUE,
        fill_opacity=0.07,
    )
    corners = VGroup(*[Dot(v, radius=0.05, color=DIM) for v in VERTS])
    perps, marks = VGroup(), VGroup()
    for i, (U, V, col) in enumerate(SIDES):
        F, _ = foot(P, U, V)
        c = RED if d[i] < 0 else col
        perps.add(
            DashedLine(P, F, dash_length=0.10, stroke_color=c, stroke_width=3.2)
            if d[i] < 0
            else Line(P, F, stroke_color=c, stroke_width=3.2)
        )
        marks.add(right_angle(P, U, V, c))
    pd = Dot(P, radius=0.085, color=INK)
    ring = Circle(
        radius=0.18, stroke_color=INK, stroke_width=2, stroke_opacity=0.5
    ).move_to(P)
    parts = VGroup(tri, corners, perps, marks, pd, ring)
    if not bar:
        return parts

    segs = VGroup()
    y = BASE_Y
    for i in range(3):
        seg = Rectangle(
            width=BAR_W,
            height=d[i],
            stroke_color=SIDES[i][2],
            stroke_width=1.6,
            stroke_opacity=0.9,
            fill_color=SIDES[i][2],
            fill_opacity=0.80,
        )
        seg.move_to([BAR_X, y + d[i] / 2.0, 0.0])
        segs.add(seg)
        y += d[i]
    assert abs(y - APEX_Y) < 1e-12, "the stack must reach exactly the apex"

    base_ext = DashedLine(
        [VC[0], BASE_Y, 0.0],
        [BAR_X + BAR_W / 2, BASE_Y, 0.0],
        stroke_color=DIM,
        stroke_width=1.5,
        stroke_opacity=0.6,
        dash_length=0.08,
    )
    apex_line = DashedLine(
        VA,
        [BAR_X + BAR_W / 2, APEX_Y, 0.0],
        stroke_color=ACID,
        stroke_width=1.8,
        stroke_opacity=0.8,
        dash_length=0.09,
    )
    arrow = DoubleArrow(
        [ARROW_X, BASE_Y, 0.0],
        [ARROW_X, APEX_Y, 0.0],
        buff=0,
        stroke_width=3,
        color=ACID,
        max_tip_length_to_length_ratio=0.06,
    )
    h_lab = MathTex("h", font_size=36, color=ACID).move_to([1.70, 0.55, 0.0])
    return VGroup(parts, segs, base_ext, apex_line, arrow, h_lab)


# ========================================================= 1 · THE CONSTANT
class ThumbnailConstant(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("VIVIANI'S THEOREM", 28, ACID)
        l1 = fit(Text("NEVER", font_size=150, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("MOVES", font_size=150, color=GOLD, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=HEAD_TOP, buff=0.30))
        self.add(figure(P_IN, bar=True))
        self.add(values_row(D_IN))
        eq = fit(MathTex(r"d_1+d_2+d_3 \;=\; h", font_size=52, color=GOLD), COL_W)
        foot = fit(Text("wherever the point goes", font_size=30, color=DIM), COL_W)
        self.add(stack([eq, foot], top=FOOT_TOP, buff=0.28))


# ========================================================= 2 · THE SURPRISE
class ThumbnailNegative(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("VIVIANI'S THEOREM", 28, ACID)
        l1 = fit(Text("ONE GOES", font_size=112, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("NEGATIVE", font_size=128, color=MAGENTA, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=HEAD_TOP, buff=0.30))
        self.add(figure(P_OUT, bar=False))
        self.add(values_row(D_OUT))
        eq = fit(MathTex(r"d_1+d_2+d_3 \;=\; h", font_size=52, color=GOLD), COL_W)
        foot = fit(Text("outside, and it still holds", font_size=30, color=RED), COL_W)
        self.add(stack([eq, foot], top=FOOT_TOP, buff=0.28))


# ========================================================= 3 · THE QUESTION
class ThumbnailAlways(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("VIVIANI'S THEOREM", 28, ACID)
        l1 = fit(Text("ALWAYS", font_size=132, color=INK, weight=BOLD), COL_W)
        l2 = fit(Text("THE SAME?", font_size=112, color=GOLD, weight=BOLD), COL_W)
        self.add(stack([kick, l1, l2], top=HEAD_TOP, buff=0.30))
        self.add(figure(P_ASK, bar=True))
        self.add(values_row(D_ASK))
        eq = fit(
            MathTex(r"d_1+d_2+d_3 \stackrel{?}{=} h", font_size=52, color=CYAN),
            COL_W,
        )
        foot = fit(Text("move the point anywhere", font_size=30, color=DIM), COL_W)
        self.add(stack([eq, foot], top=FOOT_TOP, buff=0.28))
