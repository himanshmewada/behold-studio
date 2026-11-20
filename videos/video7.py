"""
THE AREA YOU CAN COUNT  ·  16:9 YouTube video  ·  1920x1080  ·  ~4 min
=====================================================================
Pick's theorem: A = I + B/2 - 1, proved by triangulation and an angle ledger.
Why counting dots measures area in the plane — and why it dies in 3D.

THE MATHEMATICS (every on-screen number is computed, then asserted)
------------------------------------------------------------------
Shoelace        A = |sum x_i y_{i+1} - x_{i+1} y_i| / 2      (exact integers)
Boundary dots   B = sum gcd(|dx|, |dy|) over edges
Interior dots   I by exact ray-casting over the bounding box
Atoms           fan triangulation + recursive splitting at every extra
                lattice point, until each triangle is primitive.
                Every atom: det = 1, area 1/2, no extra lattice points.
Lemma           two atoms form a parallelogram; its lattice translates tile
                the plane with EXACTLY one dot per tile (checked 9/9).
Angle ledger    pi*T = 2*pi*I + pi*(B-2)   (per-dot angle sums verified)
                => T = 2I + B - 2  =>  A = T/2 = I + B/2 - 1
Credits         each dot's area credit = (its angle sum) / 2*pi;
                interior 1, straight-edge 1/2, corners fractional; sum = A.
Reeve tetrahedra (0,0,0),(1,0,0),(0,1,0),(1,1,r): volume r/6 with exactly
                FOUR lattice points for every r (verified by exhaustive scan).

LAYOUT RULES (house style)
--------------------------
* HUD chip on HUD_Y; progress rail on RAIL_Y; column only via stack().
* Long copy wrapped, never shrunk; \tfrac inline, \frac on display.
* One .animate chain per mobject per play(); updaters cleared before FadeOut.
* Every act fades its own panel; no DecimalNumber (static Integer swaps).
* Recolour only what carries meaning: CYAN = interior, MAGENTA = boundary,
  GOLD = the answer, ACID = verdicts.

SETUP / RENDER
--------------
pip install manim "manim-voiceover[gtts]" numpy
manim -pql videos/video7.py TheAreaYouCanCount   # draft
manim -pqh videos/video7.py TheAreaYouCanCount   # 1080p + narration
PREVIEW = True -> 854x480.  No voiceover lib? Renders as a paced silent cut.
"""

from contextlib import contextmanager
from math import gcd
import re
import numpy as np
from manim import *

# ------------------------------------------------------------------- format
PREVIEW = False
FPS = 30
config.pixel_width = 854 if PREVIEW else 1920
config.pixel_height = 480 if PREVIEW else 1080
config.frame_rate = FPS

# ---------------------------------------------------------------- narration
USE_VOICEOVER = True
TRANSCRIPTION_MODEL = None
try:
    from manim_voiceover import VoiceoverScene as _VOScene
    from manim_voiceover.services.gtts import GTTSService
except Exception:
    _VOScene, GTTSService = None, None

SILENT = (not USE_VOICEOVER) or (_VOScene is None)
if SILENT:

    class _SilentTracker:
        def __init__(self, scene, duration):
            self._scene, self.duration, self._t0 = scene, duration, scene._clock

        def get_remaining_duration(self):
            return max(0.0, self.duration - (self._scene._clock - self._t0))

        def time_until_end(self):
            return self.get_remaining_duration()

    class _SilentScene(Scene):
        _clock = 0.0

        def set_speech_service(self, *a, **k):
            pass

        def play(self, *args, **kwargs):
            self._clock += kwargs.get("run_time", 1.0)
            return super().play(*args, **kwargs)

        def wait(self, duration=DEFAULT_WAIT_TIME, *args, **kwargs):
            self._clock += duration
            return super().wait(duration, *args, **kwargs)

        @contextmanager
        def voiceover(self, text="", **kwargs):
            words = len(re.findall(r"[A-Za-z0-9']+", text))
            yield _SilentTracker(self, max(1.5, words / 2.55))

    _SilentScene.__module__ = "_silent_fallback"
    Base = _SilentScene
else:
    Base = _VOScene

# ------------------------------------------------------------------ palette
BG = "#07070f"
SURFACE = "#15152a"
EDGE = "#2b2b48"
INK = "#f1eff9"
DIM = "#8f8bad"
BLUE = "#4d7cff"
CYAN = "#2ee6d6"
MAGENTA = "#ff2d95"
GOLD = "#ffc233"
ACID = "#b6ff3d"

# ------------------------------------------------------------- layout grid
HUD_Y = 3.80
COL_TOP = 3.02
COL_L = 0.35
COL_W = 6.40
RAIL_Y, RAIL_X0, RAIL_X1 = -3.74, -6.55, 6.55
CHAPTERS = [
    (0.00, "01 / THE QUESTION"),
    (0.14, "02 / THE RECIPE"),
    (0.30, "03 / ATOMS OF AREA"),
    (0.50, "04 / THE ANGLE LEDGER"),
    (0.70, "05 / THE COUNT"),
    (0.88, "06 / WHERE IT BREAKS"),
]

# --------------------------------------------------------------- the stage
U = 0.56  # screen units per lattice step
STAGE_C = np.array([-3.55, -0.20, 0.0])
LC = np.array([4.0, 3.5])  # lattice coords mapped to STAGE_C


def S(p):
    return STAGE_C + U * np.array([p[0] - LC[0], p[1] - LC[1], 0.0])


# ------------------------------------------------------------------- math
HERO = [(0, 0), (7, 1), (8, 4), (5, 7), (1, 6), (0, 3)]
RECT = [(0, 0), (4, 0), (4, 3), (0, 3)]
TRI = [(0, 0), (4, 0), (0, 3)]
LSHAPE = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)]


def shoelace(poly):
    s = 0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def on_seg(a, b, p):
    if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) != 0:
        return False
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[
        1
    ] <= max(a[1], b[1])


def classify(p, poly):
    n = len(poly)
    for i in range(n):
        if on_seg(poly[i], poly[(i + 1) % n], p):
            return "B"
    x, y = p
    inside = False
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        if (ay > y) != (by > y):
            xin = ax + (y - ay) * (bx - ax) / (by - ay)
            if x < xin:
                inside = not inside
    return "I" if inside else None


def boundary_points(poly):
    pts = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        g = gcd(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for t in range(g):
            pts.append((a[0] + (b[0] - a[0]) * t // g, a[1] + (b[1] - a[1]) * t // g))
    return pts


def lattice_stats(poly):
    A = shoelace(poly)
    Bpts = boundary_points(poly)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    Ipts = [
        (x, y)
        for x in range(min(xs), max(xs) + 1)
        for y in range(min(ys), max(ys) + 1)
        if classify((x, y), poly) == "I"
    ]
    return A, Ipts, Bpts


def det2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def tri_extras(a, b, c):
    """Lattice points of the triangle other than its vertices."""
    out = []
    xs, ys = [a[0], b[0], c[0]], [a[1], b[1], c[1]]
    for x in range(min(xs), max(xs) + 1):
        for y in range(min(ys), max(ys) + 1):
            p = (x, y)
            if p in (a, b, c):
                continue
            d1, d2, d3 = det2(a, b, p), det2(b, c, p), det2(c, a, p)
            if min(d1, d2, d3) < 0:
                continue
            if d1 == 0 and on_seg(a, b, p):
                out.append(("E", p, (a, b), c))
            elif d2 == 0 and on_seg(b, c, p):
                out.append(("E", p, (b, c), a))
            elif d3 == 0 and on_seg(c, a, p):
                out.append(("E", p, (c, a), b))
            elif min(d1, d2, d3) > 0:
                out.append(("I", p, None, None))
    return out


def refine(a, b, c, out):
    ex = tri_extras(a, b, c)
    if not ex:
        out.append((a, b, c))
        return
    kind, p, edge, w = ex[0]
    if kind == "E":
        u, v = edge
        refine(u, p, w, out)
        refine(p, v, w, out)
    else:
        refine(a, b, p, out)
        refine(b, c, p, out)
        refine(c, a, p, out)


def primitive_triangulation(poly):
    out = []
    for i in range(1, len(poly) - 1):  # fan: HERO is convex (asserted)
        refine(poly[0], poly[i], poly[i + 1], out)
    return out


def angle_at(p, q, r):
    v1 = np.array(q, float) - np.array(p, float)
    v2 = np.array(r, float) - np.array(p, float)
    c = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return float(np.arccos(np.clip(c, -1.0, 1.0)))


A, IPTS, BPTS = lattice_stats(HERO)
I, B = len(IPTS), len(BPTS)
ATOMS = primitive_triangulation(HERO)
T = len(ATOMS)

# per-dot angle ledger
LEDGER = {}
for a, b, c in ATOMS:
    for p, q, r in ((a, b, c), (b, c, a), (c, a, b)):
        LEDGER[p] = LEDGER.get(p, 0.0) + angle_at(p, q, r)
CREDITS = {p: s / TAU for p, s in LEDGER.items()}

PIN, PEDGE, PCORNER = (4, 3), (6, 6), (8, 4)

# the lemma atom: nearest the stage centre, so its tiles stay on screen
LEMMA_IDX = int(
    np.argmin(
        [
            np.linalg.norm((np.array(a) + np.array(b) + np.array(c)) / 3.0 - LC)
            for a, b, c in ATOMS
        ]
    )
)


def tile_dot_counts(atom):
    a, b, c = [np.array(v, float) for v in atom]
    u, v = b - a, c - a
    inv = np.linalg.inv(np.column_stack([u, v]))
    counts = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            o = a + i * u + j * v
            corners = [o, o + u, o + v, o + u + v]
            x0 = int(np.floor(min(p[0] for p in corners)))
            x1 = int(np.ceil(max(p[0] for p in corners)))
            y0 = int(np.floor(min(p[1] for p in corners)))
            y1 = int(np.ceil(max(p[1] for p in corners)))
            cnt = 0
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    ab = inv @ (np.array([x, y], float) - o)
                    if -1e-9 <= ab[0] < 1 - 1e-9 and -1e-9 <= ab[1] < 1 - 1e-9:
                        cnt += 1
            counts.append(cnt)
    return counts


def reeve(r):
    V = [
        np.array([0, 0, 0]),
        np.array([1, 0, 0]),
        np.array([0, 1, 0]),
        np.array([1, 1, r]),
    ]
    M = np.column_stack([V[1] - V[0], V[2] - V[0], V[3] - V[0]])
    vol = abs(float(np.linalg.det(M))) / 6.0
    cnt = 0
    for x in range(2):
        for y in range(2):
            for z in range(r + 1):
                lam = np.linalg.solve(M, np.array([x, y, z], float) - V[0])
                if lam.min() > -1e-9 and lam.sum() < 1 + 1e-9:
                    cnt += 1
    return vol, cnt


def verify():
    n = len(HERO)
    assert all(
        det2(HERO[i], HERO[(i + 1) % n], HERO[(i + 2) % n]) > 0 for i in range(n)
    ), "hero must be convex for the fan"
    assert abs(A - (I + B / 2.0 - 1.0)) < 1e-12, "Pick fails on the hero"
    assert T == 2 * I + B - 2, "atom count must equal 2I + B - 2"
    for a, b, c in ATOMS:
        assert det2(a, b, c) == 1, "every atom must have area exactly 1/2"
        assert not tri_extras(a, b, c), "every atom must be primitive"
    assert abs(sum(det2(a, b, c) for a, b, c in ATOMS) / 2.0 - A) < 1e-12
    for p, s in LEDGER.items():
        kind = classify(p, HERO)
        if kind == "I":
            assert abs(s - TAU) < 1e-9, f"interior dot {p} must spend a full turn"
        elif p in HERO:
            i = HERO.index(p)
            exp = angle_at(p, HERO[i - 1], HERO[(i + 1) % n])
            assert abs(s - exp) < 1e-9, f"corner {p} must spend its own angle"
        else:
            assert abs(s - PI) < 1e-9, f"edge dot {p} must spend half a turn"
    assert abs(sum(CREDITS.values()) - A) < 1e-9, "credits must sum to the area"
    assert classify(PIN, HERO) == "I" and classify(PEDGE, HERO) == "B"
    assert PEDGE not in HERO and PCORNER in HERO
    assert all(c == 1 for c in tile_dot_counts(ATOMS[LEMMA_IDX])), "one dot per tile"
    for poly in (RECT, TRI, LSHAPE):
        a_, i_, b_ = lattice_stats(poly)
        assert abs(a_ - (len(i_) + len(b_) / 2.0 - 1.0)) < 1e-12
    for r in (1, 2, 5, 7):
        vol, cnt = reeve(r)
        assert cnt == 4 and abs(vol - r / 6.0) < 1e-9, "Reeve check fails"
    print(f"  hero: A={A:g}  I={I}  B={B}  |  {I} + {B}/2 - 1 = {I + B / 2 - 1:g}")
    print(f"  atoms: T={T}, every det=1 and primitive; T = 2I+B-2 = {2 * I + B - 2}")
    print(f"  angle ledger: {T}pi = {2 * I}pi + {B - 2}pi  [per-dot sums verified]")
    print(
        f"  credits: interior 1, edge 1/2, corners fractional; sum = {sum(CREDITS.values()):g}"
    )
    print("  parallelogram tiles: exactly one lattice dot per tile (9/9)")
    print("  cards: rectangle / right triangle / L-shape verified vs shoelace")
    print("  Reeve r=1,2,5,7: four lattice points, V=r/6  [exhaustive scan]")


verify()


# -------------------------------------------------------------- text helpers
def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def wrap(s, width=40):
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return "\n".join(out)


def txt(s, size=30, color=INK, maxw=COL_W, weight=NORMAL):
    return fit(Text(s, font_size=size, color=color, weight=weight), maxw)


def body(s, size=25, color=INK, maxw=COL_W, width=40):
    return fit(
        Text(wrap(s, width), font_size=size, color=color, line_spacing=0.9), maxw
    )


def tex(s, size=36, color=INK, maxw=COL_W):
    return fit(MathTex(s, font_size=size, color=color), maxw)


def chip(mob, color=EDGE, pad=0.18):
    box = RoundedRectangle(
        corner_radius=0.10,
        width=mob.width + 2 * pad,
        height=mob.height + 2 * pad,
        stroke_color=color,
        stroke_width=1.6,
        fill_color=SURFACE,
        fill_opacity=0.92,
    )
    box.move_to(mob.get_center())
    return VGroup(box, mob)


# ===================================================================== scene
class TheAreaYouCanCount(Base):
    # ------------------------------------------------------------- utilities
    def make_service(self):
        try:
            return GTTSService(transcription_model=TRANSCRIPTION_MODEL)
        except Exception:
            return GTTSService()

    def remaining(self, tracker):
        for name in ("get_remaining_duration", "time_until_end"):
            fn = getattr(tracker, name, None)
            if callable(fn):
                try:
                    return max(0.0, float(fn()))
                except Exception:
                    pass
        return 0.0

    def rest(self, tracker):
        left = self.remaining(tracker)
        if left > 0.05:
            self.wait(left)

    def stack(self, mobs, top=COL_TOP, left=COL_L, buff=0.30):
        y = top
        for m in mobs:
            m.move_to([left, y, 0.0], aligned_edge=UL)
            y -= m.height + buff
        return VGroup(*mobs)

    def swatch_row(self, color, label, value):
        sw = Square(side_length=0.22, fill_color=color, fill_opacity=1, stroke_width=0)
        lab = txt(label, 26, INK, 3.4)
        val = tex(value, 32, color, 2.4)
        return VGroup(sw, lab, val).arrange(RIGHT, buff=0.24)

    # ------------------------------------------------------------------- hud
    def build_hud(self):
        bg = Rectangle(width=14.4, height=8.2, stroke_width=0)
        bg.set_fill(color=["#101024", "#05050c"], opacity=1)
        self.add(bg)
        rail = Line(
            [RAIL_X0, RAIL_Y, 0],
            [RAIL_X1, RAIL_Y, 0],
            stroke_color=EDGE,
            stroke_width=4,
        )
        ticks = VGroup(
            *[
                Line(
                    [RAIL_X0 + f * (RAIL_X1 - RAIL_X0), RAIL_Y - 0.075, 0],
                    [RAIL_X0 + f * (RAIL_X1 - RAIL_X0), RAIL_Y + 0.075, 0],
                    stroke_color="#39424f",
                    stroke_width=2,
                )
                for f, _ in CHAPTERS
            ]
        )
        self.prog = ValueTracker(0.004)
        fill = Line(
            [RAIL_X0, RAIL_Y, 0],
            [RAIL_X0 + 0.05, RAIL_Y, 0],
            stroke_color=GOLD,
            stroke_width=5,
        )
        fill.add_updater(
            lambda m: m.put_start_and_end_on(
                [RAIL_X0, RAIL_Y, 0],
                [RAIL_X0 + self.prog.get_value() * (RAIL_X1 - RAIL_X0), RAIL_Y, 0],
            )
        )
        self.add(rail, ticks, fill)
        self.rail_fill = fill
        self._chap = None

    def chapter(self, i, run_time=1.0):
        frac, name = CHAPTERS[i]
        lab = txt(name, 18, DIM, 5.2).move_to([-6.55, HUD_Y, 0], aligned_edge=LEFT)
        anims = [self.prog.animate.set_value(max(0.004, frac)), FadeIn(lab)]
        if self._chap is not None:
            anims.append(FadeOut(self._chap))
        self.play(*anims, run_time=run_time)
        self._chap = lab

    # ---------------------------------------------------------------- stage
    def make_lattice(self):
        return VGroup(
            *[
                Dot(S((x, y)), radius=0.030, color=DIM, fill_opacity=0.45)
                for x in range(-1, 10)
                for y in range(-1, 9)
            ]
        )

    def make_hero(self):
        poly = Polygon(
            *[S(p) for p in HERO],
            stroke_color=GOLD,
            stroke_width=3.5,
            fill_color=BLUE,
            fill_opacity=0.10,
        )
        idots = VGroup(*[Dot(S(p), radius=0.062, color=CYAN) for p in IPTS])
        bdots = VGroup(*[Dot(S(p), radius=0.062, color=MAGENTA) for p in BPTS])
        return poly, idots, bdots

    def arcs_at(self, p, col, radius=0.20):
        g = VGroup()
        for a, b, c in ATOMS:
            if p not in (a, b, c):
                continue
            q, r = [v for v in (a, b, c) if v != p]
            v1 = np.array(q, float) - np.array(p, float)
            v2 = np.array(r, float) - np.array(p, float)
            a1 = float(np.arctan2(v1[1], v1[0]))
            a2 = float(np.arctan2(v2[1], v2[0]))
            sweep = (a2 - a1) % TAU
            if sweep > PI:
                a1, sweep = a2, TAU - sweep
            g.add(
                Arc(
                    radius=radius,
                    start_angle=a1,
                    angle=sweep,
                    arc_center=S(p),
                    stroke_color=col,
                    stroke_width=3.2,
                )
            )
        return g

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.build_hud()
        self.act_question()
        self.act_recipe()
        self.act_atoms()
        self.act_ledger()
        self.act_count()
        self.act_breaks()

    # ================================================================== ACT 1
    def act_question(self):
        self.chapter(0, run_time=0.8)
        self.lattice = self.make_lattice()
        poly, idots, bdots = self.make_hero()
        self.poly_mob, self.int_dots, self.bnd_dots = poly, idots, bdots

        head = txt("THE QUESTION", 28, GOLD, weight=BOLD)
        q = body("A polygon on a grid of dots. No ruler. Can counting be enough?")
        row_i = self.swatch_row(CYAN, "strictly inside", rf"I = {I}")
        row_b = self.swatch_row(MAGENTA, "on the edge", rf"B = {B}")
        truth = tex(rf"A = {A:g}", 52, GOLD)
        note = body(
            "the truth, from the shoelace formula on the coordinates",
            size=22,
            color=DIM,
        )
        col = self.stack([head, q, row_i, row_b, truth, note], buff=0.30)

        with self.voiceover(
            "Here is a polygon, drawn on a grid of dots. No ruler, no formula "
            "for its sides. Just one question: can you find its area by counting?"
        ) as tr:
            d = tr.duration
            self.play(FadeIn(self.lattice), run_time=d * 0.30)
            self.play(Create(poly), FadeIn(head), FadeIn(q), run_time=d * 0.55)
            self.rest(tr)

        with self.voiceover(
            "Sort the dots. Thirty seven sit strictly inside. Ten sit on the "
            "edge. And the true area, computed from the coordinates, is forty "
            "one. Hold that number."
        ) as tr:
            d = tr.duration
            self.play(
                LaggedStart(*[GrowFromCenter(p) for p in idots], lag_ratio=0.02),
                FadeIn(row_i),
                run_time=d * 0.34,
            )
            self.play(
                LaggedStart(*[GrowFromCenter(p) for p in bdots], lag_ratio=0.05),
                FadeIn(row_b),
                run_time=d * 0.26,
            )
            self.play(Write(truth), FadeIn(note), run_time=d * 0.28)
            self.rest(tr)
        self.q_col = col

    # ================================================================== ACT 2
    def act_recipe(self):
        self.chapter(1)
        ghost = VGroup(self.poly_mob, self.int_dots, self.bnd_dots)
        formula = tex(r"A \;=\; I + \frac{B}{2} - 1", 46, GOLD)
        sub = tex(rf"{A:g} \;=\; {I} + \tfrac{{{B}}}{{2}} - 1", 38, CYAN)
        claim = body(
            "Pick's theorem, 1899. Interior dots pay one. Boundary dots pay half."
        )
        self.stack([formula, sub, claim], buff=0.34)

        with self.voiceover(
            "Here is the claim. Pick's theorem, eighteen ninety nine. Area "
            "equals interior dots, plus half the boundary dots, minus one. "
            "Thirty seven plus five minus one. Forty one."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.q_col),
                ghost.animate.scale(0.40)
                .move_to([-3.55, 2.05, 0])
                .set_stroke(opacity=0.35)
                .set_fill(opacity=0.12),
                self.lattice.animate.set_fill(opacity=0.12),
                run_time=d * 0.25,
            )
            self.play(Write(formula), run_time=d * 0.30)
            self.play(Write(sub), FadeIn(claim), run_time=d * 0.30)
            self.rest(tr)
        self.ghost = ghost

        # three test cards, every count computed
        cards = VGroup()
        for poly, name, cx in (
            (RECT, "rectangle", -5.45),
            (TRI, "right triangle", -3.55),
            (LSHAPE, "L-shape", -1.65),
        ):
            a_, i_, b_ = lattice_stats(poly)
            u, cy = 0.30, -1.05
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            M = lambda p: np.array([cx + u * (p[0] - mx), cy + u * (p[1] - my), 0.0])
            grid = VGroup(
                *[
                    Dot(M((x, y)), radius=0.022, color=DIM, fill_opacity=0.4)
                    for x in range(min(xs) - 1, max(xs) + 2)
                    for y in range(min(ys) - 1, max(ys) + 2)
                ]
            )
            pm = Polygon(
                *[M(p) for p in poly],
                stroke_color=INK,
                stroke_width=2,
                fill_color=BLUE,
                fill_opacity=0.08,
            )
            di = VGroup(*[Dot(M(p), radius=0.045, color=CYAN) for p in i_])
            db = VGroup(*[Dot(M(p), radius=0.045, color=MAGENTA) for p in b_])
            nm = txt(name, 20, DIM, 1.8).next_to(pm, UP, buff=0.22)
            ct = tex(
                rf"{len(i_)} + \tfrac{{{len(b_)}}}{{2}} - 1 = {a_:g}",
                26,
                INK,
                1.9,
            ).next_to(pm, DOWN, buff=0.24)
            ck = tex(r"\checkmark", 30, ACID, 0.5).next_to(ct, DOWN, buff=0.12)
            cards.add(VGroup(grid, pm, di, db, nm, ct, ck))

        with self.voiceover(
            "Try it elsewhere. A rectangle: six inside, fourteen on the edge, "
            "twelve. A right triangle: three and eight give six. Even this L "
            "shape, with its reflex corner: five and sixteen give twelve. "
            "Every time, exact."
        ) as tr:
            d = tr.duration
            for card in cards:
                self.play(FadeIn(card, shift=UP * 0.12), run_time=d * 0.27)
            self.rest(tr)

        verdict = body(
            "Three for three. But a pattern is not a proof. Why half? Why minus one?",
            color=ACID,
        )
        self.stack([verdict], top=-1.60)
        with self.voiceover(
            "But a formula that always works is not a proof. Why half? "
            "Why minus one? For that, we cut."
        ) as tr:
            self.play(FadeIn(verdict), run_time=min(1.6, tr.duration * 0.7))
            self.rest(tr)
        self.r_col = VGroup(formula, sub, claim, verdict)
        self.cards = cards

    # ================================================================== ACT 3
    def act_atoms(self):
        self.chapter(2)
        self.poly_mob, self.int_dots, self.bnd_dots = self.make_hero()
        atom_mobs = VGroup(
            *[
                Polygon(
                    *[S(p) for p in tri],
                    stroke_color=CYAN,
                    stroke_width=1.1,
                    stroke_opacity=0.8,
                    fill_color=BLUE,
                    fill_opacity=0.05,
                )
                for tri in ATOMS
            ]
        )
        self.atom_mobs = atom_mobs

        head = txt("ATOMS OF AREA", 28, GOLD, weight=BOLD)
        cut = body("Slice along lattice lines until no piece can be sliced again.")
        half = tex(r"\text{every atom: area} = \tfrac{1}{2}", 38, CYAN)
        count = VGroup(
            txt("atoms", 22, DIM, 1.6),
            Integer(T, font_size=64, color=GOLD),
        ).arrange(RIGHT, buff=0.30)
        self.stack([head, cut, half, count], buff=0.32)

        with self.voiceover(
            "Slice the polygon along lattice lines, triangle by triangle, "
            "until no piece can be sliced again. What is left are atoms: "
            "triangles with no lattice points except their three corners. "
            "Eighty two of them."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.r_col),
                FadeOut(self.cards),
                FadeOut(self.ghost),
                self.lattice.animate.set_fill(opacity=0.45),
                run_time=d * 0.16,
            )
            self.play(
                Create(self.poly_mob),
                FadeIn(self.int_dots),
                FadeIn(self.bnd_dots),
                FadeIn(head),
                FadeIn(cut),
                run_time=d * 0.18,
            )
            self.play(
                LaggedStart(*[Create(t) for t in atom_mobs], lag_ratio=0.012),
                run_time=max(3.0, d * 0.44),
            )
            self.play(FadeIn(half), FadeIn(count), run_time=d * 0.16)
            self.rest(tr)

        # the 1/2 lemma: parallelogram tiles, one dot per tile (asserted)
        a, b, c = [np.array(v, float) for v in ATOMS[LEMMA_IDX]]
        u, v = b - a, c - a
        hi = atom_mobs[LEMMA_IDX].copy()
        hi.set_fill(GOLD, opacity=0.30).set_stroke(GOLD, width=3)
        para = Polygon(
            S(a),
            S(a + u),
            S(a + u + v),
            S(a + v),
            stroke_color=GOLD,
            stroke_width=2.5,
            fill_opacity=0,
        )
        tiles = VGroup()
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:
                    continue
                o = a + i * u + j * v
                tiles.add(
                    Polygon(
                        S(o),
                        S(o + u),
                        S(o + u + v),
                        S(o + v),
                        stroke_color=DIM,
                        stroke_width=1.3,
                        stroke_opacity=0.55,
                        fill_color=BLUE,
                        fill_opacity=0.04,
                    )
                )
        lemma = body(
            "Two atoms make a parallelogram. Whole-number slides tile the "
            "plane, one dot per tile: area one. So the atom is half.",
            size=23,
            color=DIM,
        )
        self.stack([lemma], top=-0.90)
        tchip = chip(tex(r"1\ \text{dot per tile}", 26, GOLD, 2.6), GOLD)
        tchip.move_to([-3.55, -2.85, 0])

        with self.voiceover(
            "Every atom has area exactly one half. Here is why. Two copies "
            "make a parallelogram, and whole-number slides of that "
            "parallelogram tile the plane. Every tile catches exactly one "
            "dot. One dot per unit of area means the tile has area one, "
            "so the atom is half."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(hi), run_time=d * 0.12)
            self.play(Create(para), run_time=d * 0.16)
            self.play(FadeIn(tiles), FadeIn(tchip), run_time=d * 0.24)
            self.play(FadeIn(lemma), run_time=d * 0.20)
            self.rest(tr)
        self.play(FadeOut(tiles, para, hi, tchip), run_time=0.7)
        self.a_col = VGroup(head, cut, half, count, lemma)

    # ================================================================== ACT 4
    def act_ledger(self):
        self.chapter(3)
        head = txt("THE ANGLE LEDGER", 28, GOLD, weight=BOLD)
        n1 = body("Count angles, not area. Every triangle carries pi.")
        sym = tex(r"\pi T \;=\; 2\pi I + \pi\,(B-2)", 40, INK)
        num = tex(rf"{T}\pi \;=\; {2 * I}\pi + {B - 2}\pi", 36, CYAN)
        n2 = body(
            "Interior dots spend full turns. The boundary shares the "
            "polygon's own angles.",
            size=23,
            color=DIM,
        )
        self.stack([head, n1, sym, num, n2], buff=0.30)

        rings, arc_groups, chips = VGroup(), VGroup(), VGroup()
        demos = [
            (PIN, CYAN, tex(r"2\pi \;\to\; 1", 28, CYAN, 1.8), UP),
            (PEDGE, MAGENTA, tex(r"\pi \;\to\; \tfrac{1}{2}", 28, MAGENTA, 1.8), UP),
            (
                PCORNER,
                MAGENTA,
                tex(rf"\theta \;\to\; {CREDITS[PCORNER]:.2f}", 28, MAGENTA, 2.0),
                LEFT,
            ),
        ]
        for p, col, lab, direction in demos:
            ring = Circle(radius=0.11, stroke_color=col, stroke_width=2).move_to(S(p))
            arcs = self.arcs_at(p, col)
            cp = chip(lab, col).next_to(ring, direction, buff=0.30)
            rings.add(ring)
            arc_groups.add(arcs)
            chips.add(cp)
        edge_line = Line(
            S((5, 7)),
            S((8, 4)),
            stroke_color=MAGENTA,
            stroke_width=2,
            stroke_opacity=0.8,
        )

        with self.voiceover(
            "Now count angles instead of area. Every triangle carries pi. "
            "Around an interior dot, the angles fill a full turn: two pi. "
            "Around a dot on a straight edge, they fill half a turn: pi. "
            "At a corner, just the polygon's angle."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.a_col), FadeIn(head), FadeIn(n1), run_time=d * 0.14)
            self.play(
                FadeIn(rings[0]),
                LaggedStart(*[Create(a) for a in arc_groups[0]], lag_ratio=0.08),
                FadeIn(chips[0]),
                run_time=d * 0.26,
            )
            self.play(
                FadeIn(rings[1]),
                Create(edge_line),
                LaggedStart(*[Create(a) for a in arc_groups[1]], lag_ratio=0.08),
                FadeIn(chips[1]),
                run_time=d * 0.24,
            )
            self.play(
                FadeIn(rings[2]),
                LaggedStart(*[Create(a) for a in arc_groups[2]], lag_ratio=0.08),
                FadeIn(chips[2]),
                run_time=d * 0.22,
            )
            self.rest(tr)

        verdict = body("Area is angle, divided by one full turn.", color=GOLD)
        self.stack([verdict], top=-1.90)
        with self.voiceover(
            "So the total angle is pi times the number of triangles. But it "
            "is also two pi per interior dot, plus the polygon's own angles: "
            "pi times B minus two. Two ways to count one thing."
        ) as tr:
            d = tr.duration
            self.play(Write(sym), run_time=d * 0.30)
            self.play(Write(num), run_time=d * 0.26)
            self.play(FadeIn(n2), FadeIn(verdict), run_time=d * 0.28)
            self.rest(tr)
        self.ledger_extras = VGroup(rings, arc_groups, chips, edge_line)
        self.l_col = VGroup(head, n1, sym, num, n2, verdict)

    # ================================================================== ACT 5
    def act_count(self):
        self.chapter(4)
        head = txt("THE COUNT", 28, GOLD, weight=BOLD)
        tline = tex(rf"T = 2I + B - 2 = {2 * I} + {B} - 2 = {T}", 34, INK)
        hero = tex(r"A \;=\; \frac{T}{2} \;=\; I + \frac{B}{2} - 1", 46, ACID)
        box = SurroundingRectangle(
            hero, color=ACID, buff=0.22, stroke_width=2.4, stroke_opacity=0.9
        )
        sub = tex(
            rf"{A:g} \;=\; \tfrac{{{T}}}{{2}} \;=\; {I} + {B / 2:g} - 1", 36, GOLD
        )
        row_i = self.swatch_row(CYAN, "interior: full turns", rf"{I} \times 1 = {I}")
        row_b = self.swatch_row(
            MAGENTA, "boundary shares", rf"\tfrac{{{B}}}{{2}} - 1 = {B / 2 - 1:g}"
        )
        total = body(f"total {A:g} — the shoelace agrees, exactly.", color=ACID)
        self.stack([head, tline, hero, sub, row_i, row_b, total], buff=0.28)
        box.move_to(hero.get_center())

        with self.voiceover(
            "Set them equal and divide by pi. T equals two I plus B minus "
            "two. Eighty two, exactly as counted. And since every atom is "
            "half a unit of area, the area is T over two: I plus B over "
            "two minus one."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.l_col),
                FadeOut(self.ledger_extras),
                self.atom_mobs.animate.set_stroke(opacity=0.22).set_fill(opacity=0.02),
                FadeIn(head),
                run_time=d * 0.18,
            )
            self.play(Write(tline), run_time=d * 0.22)
            self.play(Write(hero), Create(box), run_time=d * 0.30)
            self.play(Write(sub), run_time=d * 0.20)
            self.rest(tr)

        with self.voiceover(
            "That is where the half comes from: a boundary dot only ever "
            "spends half a turn. And the minus one is the polygon's angle "
            "sum, two dots short of a full share. The dots were paying "
            "for the area all along."
        ) as tr:
            d = tr.duration
            self.play(
                FadeIn(row_i),
                Indicate(self.int_dots, color=CYAN, scale_factor=1.15),
                run_time=d * 0.30,
            )
            self.play(
                FadeIn(row_b),
                Indicate(self.bnd_dots, color=MAGENTA, scale_factor=1.15),
                run_time=d * 0.30,
            )
            self.play(
                FadeIn(total),
                Flash(
                    hero, color=ACID, line_length=0.3, num_lines=18, flash_radius=2.4
                ),
                run_time=d * 0.28,
            )
            self.rest(tr)
        self.c_col = VGroup(head, tline, hero, box, sub, row_i, row_b, total)

    # ================================================================== ACT 6
    def act_breaks(self):
        self.chapter(5)

        def reeve_mob(r, base, s=1.05):
            V = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, r)]
            iso = lambda p: np.array(
                [
                    base[0] + s * (p[0] - 0.5 * p[1]),
                    base[1] + s * (0.62 * p[2] + 0.32 * p[1]),
                    0.0,
                ]
            )
            pts = [iso(p) for p in V]
            faces = VGroup(
                Polygon(
                    pts[0],
                    pts[1],
                    pts[3],
                    stroke_width=0,
                    fill_color=BLUE,
                    fill_opacity=0.08,
                ),
                Polygon(
                    pts[0],
                    pts[2],
                    pts[3],
                    stroke_width=0,
                    fill_color=BLUE,
                    fill_opacity=0.08,
                ),
            )
            edges = VGroup(
                *[
                    Line(
                        pts[i],
                        pts[j],
                        stroke_color=DIM,
                        stroke_width=2,
                        stroke_opacity=0.8,
                    )
                    for i, j in ((0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3))
                ]
            )
            dots = VGroup(*[Dot(p, radius=0.07, color=GOLD) for p in pts])
            arr = DoubleArrow(
                iso((1, 1, 0)) + RIGHT * 0.35,
                iso((1, 1, r)) + RIGHT * 0.35,
                buff=0,
                stroke_width=3,
                color=MAGENTA,
                max_tip_length_to_length_ratio=0.10,
            )
            rlab = txt(f"r = {r}", 22, MAGENTA, 1.2).next_to(arr, RIGHT, buff=0.14)
            vol, cnt = reeve(r)
            vchip = chip(tex(rf"V = \tfrac{{{r}}}{{6}}", 30, GOLD, 1.8), GOLD)
            vchip.move_to([base[0] + 0.2, -2.55, 0])
            four = txt("4 dots", 20, DIM, 1.2).next_to(vchip, DOWN, buff=0.14)
            return VGroup(faces, edges, dots, arr, rlab, vchip, four)

        t1 = reeve_mob(1, (-5.05, -1.75))
        t5 = reeve_mob(5, (-2.35, -1.75))

        head = txt("WHERE IT BREAKS", 28, GOLD, weight=BOLD)
        n1 = body("Lift one corner of a lattice tetrahedron to height r.")
        verts = tex(r"(0,0,0),\ (1,0,0),\ (0,1,0),\ (1,1,r)", 28, DIM)
        vol = tex(r"V = \tfrac{r}{6}", 44, CYAN)
        n2 = body(
            "Reeve's tetrahedra: always exactly four lattice points, "
            "volume as large as you like."
        )
        verdict = body("No counting formula survives the third dimension.", color=GOLD)
        col = self.stack([head, n1, verts, vol, n2, verdict], buff=0.30)

        with self.voiceover(
            "One last thing. This magic is flat. In three dimensions, take "
            "these four lattice points and lift the apex to height r. The "
            "volume is r over six, and the lattice points are still just "
            "four. Same dots, any volume."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.c_col),
                FadeOut(
                    VGroup(
                        self.lattice,
                        self.poly_mob,
                        self.int_dots,
                        self.bnd_dots,
                        self.atom_mobs,
                    )
                ),
                run_time=d * 0.16,
            )
            self.play(FadeIn(head), FadeIn(n1), Write(verts), run_time=d * 0.22)
            self.play(FadeIn(t1, shift=UP * 0.12), run_time=d * 0.20)
            self.play(FadeIn(t5, shift=UP * 0.12), Write(vol), run_time=d * 0.26)
            self.play(FadeIn(n2), run_time=d * 0.12)
            self.rest(tr)

        card1 = tex(r"A \;=\; I + \frac{B}{2} - 1", 62, GOLD, 9.0).move_to([0, 1.05, 0])
        card2 = txt("Pick's theorem · 1899", 28, DIM, 8.0).move_to([0, 0.05, 0])
        tag = txt("THE AREA YOU CAN COUNT", 34, INK, 9.0, weight=BOLD).move_to(
            [0, -1.15, 0]
        )
        tag.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        with self.voiceover(
            "Reeve's tetrahedra. Counting cannot measure space. But in the "
            "plane, every dot remembers its share of the area. Pick's "
            "theorem: the picture is the proof."
        ) as tr:
            self.play(FadeOut(t1), FadeOut(t5), FadeOut(col), run_time=0.9)
            self.play(Write(card1), run_time=1.2)
            self.play(FadeIn(card2), FadeIn(tag, shift=UP * 0.15), run_time=1.1)
            self.rest(tr)
        self.wait(1.6)
        self.play(self.prog.animate.set_value(1.0), run_time=1.0)
        self.rail_fill.clear_updaters()
        self.play(FadeOut(VGroup(card1, card2, tag, self._chap)), run_time=1.4)
        self.wait(0.5)
