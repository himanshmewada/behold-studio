"""
THE SUM THAT NEVER MOVES  ·  YouTube Short  ·  1080x1920  ·  ~60 s
==================================================================
Viviani's theorem: from any point inside an equilateral triangle, the three
perpendicular distances to the sides always add up to the altitude.

THE MATHEMATICS (every on-screen number is computed, then asserted)
------------------------------------------------------------------
Triangle        side s, altitude h = s*sqrt(3)/2, inradius h/3
Signed distance d_i(P) = (P - U_i) . n_i     with n_i the INWARD unit normal
Identity        n_1 + n_2 + n_3 = 0  ->  d_1+d_2+d_3 is constant on the WHOLE
                plane, not just inside. Evaluated at the centroid it is h.
Area proof      [PBC] + [PCA] + [PAB] = [ABC]
                (s/2)d_1 + (s/2)d_2 + (s/2)d_3 = (s/2)h  ->  cancel s/2
Outside         one d_i goes negative; the signed sum is still exactly h
Generalisation  regular n-gon: sum of distances = n * apothem
Live bar        three stacked segments, height d_1+d_2+d_3, whose top sits
                exactly level with the apex for every position of P

LAYOUT RULES (house style)
--------------------------
* ONE stack() call per zone, top-anchored from real mobject heights.
* Long copy goes through wrap(); fit() is a width clamp of last resort.
* \tfrac inline in stacked rows; \frac only on stand-alone display lines.
* One .animate chain per mobject per play().
* Every live updater is cleared before any FadeOut; DecimalNumber is
  pre-synced with .update(0) and pinned to a captured anchor so it cannot
  drift or resize mid-fade.
* Each act clears the previous act's panel. Recolour carries meaning only:
  CYAN / GOLD / MAGENTA are the three distances, RED is a negative distance,
  ACID is the invariant total.

SHORTS SAFE ZONE
----------------
All type stays above y = -4.6 and inside x in [-3.9, 3.9], clear of the
right-edge buttons and the bottom caption block.

SETUP / RENDER
--------------
pip install manim "manim-voiceover[gtts]" numpy
manim -pql videos/video8.py TheSumThatNeverMoves   # 540x960 draft
manim -pqh videos/video8.py TheSumThatNeverMoves   # 1080x1920 + narration
PREVIEW = True -> 540x960.  No voiceover lib? Renders as a paced silent cut.
"""

from contextlib import contextmanager
import re
import numpy as np
from manim import *

# ------------------------------------------------------------------- format
PREVIEW = False
FPS = 30
config.pixel_width = 540 if PREVIEW else 1080
config.pixel_height = 960 if PREVIEW else 1920
config.frame_width = 9
config.frame_height = 16
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
GOLD = "#ffc233"
MAGENTA = "#ff2d95"
ACID = "#b6ff3d"
RED = "#ff5252"
SIX = [CYAN, "#3aa0ff", BLUE, "#a06bff", MAGENTA, GOLD]

# --------------------------------------------------------------- layout grid
COL_W = 8.20
TOP_TOP = 7.05
BOT_TOP = -1.05

# ----------------------------------------------------------------- geometry
SIDE = 5.50
H = SIDE * np.sqrt(3.0) / 2.0
RC = SIDE / np.sqrt(3.0)
RI = H / 3.0
TRI_C = np.array([-0.75, 1.15, 0.0])

VERTS = [
    TRI_C + RC * np.array([np.cos(a), np.sin(a), 0.0])
    for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)
]
VA, VB, VC = VERTS  # apex, bottom-left, bottom-right
SIDES = [(VB, VC, CYAN), (VA, VB, GOLD), (VC, VA, MAGENTA)]

BAR_X, BAR_W = 3.25, 0.70
BAR_Y0 = VB[1]
ARROW_X = 2.62
LOOP_R = 1.12
EPS = 0.20


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


def path_point(u):
    a = TAU * u
    return TRI_C + LOOP_R * np.array([np.cos(a), np.sin(a), 0.0])


FREEZE_U = 1.22
PF = path_point(FREEZE_U)
_mid_ca = 0.5 * (VC + VA)
P_OUT = _mid_ca - 1.10 * NORMALS[2]

# regular n-gon payoff
NGON_N, NGON_R = 6, 2.05
NGON_C = np.array([0.0, 1.55, 0.0])
NGON_A = NGON_R * np.cos(PI / NGON_N)


def ngon_verts(n, R, center):
    return [
        center
        + R
        * np.array([np.cos(PI / 2 + TAU * k / n), np.sin(PI / 2 + TAU * k / n), 0.0])
        for k in range(n)
    ]


def ngon_dist_sum(P, verts):
    n = len(verts)
    c = np.mean(np.array(verts), axis=0)
    total = 0.0
    for i in range(n):
        U, V = verts[i], verts[(i + 1) % n]
        e = V - U
        nn = np.array([e[1], -e[0], 0.0])
        nn /= np.linalg.norm(nn)
        if np.dot(c - U, nn) < 0.0:
            nn = -nn
        total += float(np.dot(P - U, nn))
    return total


def shoelace(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i][:2]
        x2, y2 = pts[(i + 1) % len(pts)][:2]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def verify():
    rng = np.random.default_rng(7)
    assert np.linalg.norm(np.sum(NORMALS, axis=0)) < 1e-12, "inward normals must cancel"
    assert abs(H - SIDE * np.sqrt(3) / 2) < 1e-12
    assert abs(shoelace(VERTS) - 0.5 * SIDE * H) < 1e-9

    inside = []
    for _ in range(400):
        w = rng.random(3)
        w /= w.sum()
        inside.append(w[0] * VA + w[1] * VB + w[2] * VC)
    inside += [path_point(t) for t in np.linspace(0, 1, 240)]
    inside += [TRI_C, PF]
    for P in inside:
        d = dists(P)
        assert min(d) > -1e-12, "sample must be inside"
        assert abs(sum(d) - H) < 1e-10, "Viviani fails inside"
        assert abs(sum(0.5 * SIDE * x for x in d) - shoelace(VERTS)) < 1e-9
        for U, V, _ in SIDES:
            _, t = foot(P, U, V)
            assert -1e-9 <= t <= 1 + 1e-9, "interior foot must land on the side"
    assert min(min(dists(path_point(t))) for t in np.linspace(0, 1, 240)) > 0.4

    d_out = dists(P_OUT)
    assert min(d_out) < -0.5, "the outside point must flip one distance"
    assert abs(sum(d_out) - H) < 1e-10, "signed sum must survive going outside"
    for U, V, _ in SIDES:
        _, t = foot(P_OUT, U, V)
        assert -1e-9 <= t <= 1 + 1e-9, "outside demo keeps every foot on its side"
    for _ in range(200):
        P = TRI_C + rng.normal(0, 3.0, 3) * np.array([1, 1, 0])
        assert abs(sum(dists(P)) - H) < 1e-9, "the sum is constant on the whole plane"

    for n in (3, 4, 5, 6, 8):
        R = 2.4
        vs = ngon_verts(n, R, ORIGIN)
        ap = R * np.cos(PI / n)
        for _ in range(60):
            w = rng.random(n)
            w /= w.sum()
            P = np.sum(np.array(vs) * w[:, None], axis=0) * 0.85
            assert abs(ngon_dist_sum(P, vs) - n * ap) < 1e-9, f"n-gon fails at n={n}"

    print(f"  triangle: s={SIDE:.3f}  h={H:.6f}  inradius={RI:.6f}")
    print(f"  normals sum |n1+n2+n3| = {np.linalg.norm(np.sum(NORMALS, axis=0)):.2e}")
    print(
        f"  Viviani verified at {len(inside)} interior points + 200 points of the plane"
    )
    print(
        f"  frozen point d = {dists(PF)[0]:.3f}, {dists(PF)[1]:.3f}, {dists(PF)[2]:.3f}"
        f"  -> {sum(dists(PF)):.6f}"
    )
    print(
        f"  outside point d = {d_out[0]:.3f}, {d_out[1]:.3f}, {d_out[2]:.3f}"
        f"  -> {sum(d_out):.6f}  (one negative)"
    )
    print(f"  regular n-gons n=3,4,5,6,8: sum = n*apothem verified")
    print(f"  hexagon payoff: 6a = {NGON_N * NGON_A:.4f}")


verify()


# -------------------------------------------------------------- text helpers
def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def wrap(s, width=42):
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


def txt(s, size=40, color=INK, maxw=COL_W, weight=NORMAL):
    return fit(Text(s, font_size=size, color=color, weight=weight), maxw)


def body(s, size=32, color=INK, maxw=COL_W, width=42):
    return fit(
        Text(wrap(s, width), font_size=size, color=color, line_spacing=0.85), maxw
    )


def tex(s, size=44, color=INK, maxw=COL_W):
    return fit(MathTex(s, font_size=size, color=color), maxw)


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


def set_bar(m, x, y0, y1, w=BAR_W):
    y1 = max(y1, y0 + 1e-4)
    m.set_points_as_corners(
        [
            np.array([x - w / 2, y0, 0.0]),
            np.array([x + w / 2, y0, 0.0]),
            np.array([x + w / 2, y1, 0.0]),
            np.array([x - w / 2, y1, 0.0]),
            np.array([x - w / 2, y0, 0.0]),
        ]
    )


def make_bar(col):
    return Rectangle(
        width=BAR_W,
        height=1.0,
        stroke_color=col,
        stroke_width=1.6,
        stroke_opacity=0.9,
        fill_color=col,
        fill_opacity=0.80,
    )


# ===================================================================== scene
class TheSumThatNeverMoves(Base):
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

    # ------------------------------------------------------------- live rig
    def set_perp(self, m, i, P):
        U, V, col = SIDES[i]
        F, _ = foot(P, U, V)
        if np.linalg.norm(P - F) < 1e-5:
            F = F + NORMALS[i] * 1e-5
        m.put_start_and_end_on(P, F)
        neg = float(np.dot(P - U, NORMALS[i])) < 0.0
        m.set_stroke(color=RED if neg else col, width=3.4, opacity=0.95)

    def set_mark(self, m, i, P):
        U, V, col = SIDES[i]
        F, _ = foot(P, U, V)
        v = P - F
        nv = np.linalg.norm(v)
        if nv < 1e-4:
            m.set_points_as_corners([F, F, F])
            return
        v = v / nv
        e = V - U
        e = e / np.linalg.norm(e)
        if np.dot(0.5 * (U + V) - F, e) < 0.0:
            e = -e
        m.set_points_as_corners([F + EPS * e, F + EPS * (e + v), F + EPS * v])
        neg = float(np.dot(P - U, NORMALS[i])) < 0.0
        m.set_stroke(color=RED if neg else col, width=2.0, opacity=0.85)

    def bind(self, Pfun, bar=False):
        """Clear then re-attach: repeated acts can never stack updaters."""
        self.pdot.clear_updaters()
        self.pring.clear_updaters()
        self.pdot.add_updater(lambda m: m.move_to(Pfun()))
        self.pring.add_updater(lambda m: m.move_to(Pfun()))
        for i in range(3):
            self.perps[i].clear_updaters()
            self.marks[i].clear_updaters()
            self.perps[i].add_updater(lambda m, i=i: self.set_perp(m, i, Pfun()))
            self.marks[i].add_updater(lambda m, i=i: self.set_mark(m, i, Pfun()))
            self.nums[i].clear_updaters()

            def nu(m, i=i):
                d = dists(Pfun())[i]
                m.set_value(d)
                m.set_color(RED if d < 0 else SIDES[i][2])
                m.move_to(self.anchors[i])

            self.nums[i].add_updater(nu)
            self.nums[i].update(0)
        self.total.clear_updaters()

        def tu(m):
            m.set_value(sum(dists(Pfun())))
            m.move_to(self.total_anchor)

        self.total.add_updater(tu)
        self.total.update(0)
        if bar:
            for i in range(3):
                self.segs[i].clear_updaters()

                def su(m, i=i):
                    d = dists(Pfun())
                    lo = BAR_Y0 + sum(d[:i])
                    set_bar(m, BAR_X, lo, lo + d[i])

                self.segs[i].add_updater(su)

    def unbind(self, bar=False):
        for m in [
            self.pdot,
            self.pring,
            self.total,
            *self.perps,
            *self.marks,
            *self.nums,
        ]:
            m.clear_updaters()
        if bar:
            for m in self.segs:
                m.clear_updaters()

    def d_row(self, i, value):
        col = SIDES[i][2]
        sw = Square(side_length=0.26, fill_color=col, fill_opacity=1, stroke_width=0)
        lab = tex(rf"d_{i + 1}", 34, col, 1.0)
        num = DecimalNumber(value, num_decimal_places=2, font_size=40, color=col)
        return VGroup(sw, lab, num).arrange(RIGHT, buff=0.28), num

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.act_stage()
        self.act_hook()
        self.act_drift()
        self.act_proof()
        self.act_cancel()
        self.act_outside()
        self.act_general()

    # ------------------------------------------------------------------ stage
    def act_stage(self):
        bg = Rectangle(width=9.4, height=16.4, stroke_width=0)
        bg.set_fill(color=["#141430", "#05050c"], opacity=1)
        self.add(bg)
        lattice = VGroup()
        for i in range(-9, 10):
            for j in range(-16, 17):
                p = np.array([i * 0.5, j * 0.5, 0.0])
                if abs(p[0]) < 4.6 and abs(p[1]) < 8.1:
                    lattice.add(Dot(p, radius=0.017, color=DIM, fill_opacity=0.13))
        self.add(lattice)
        halo = VGroup(
            *[
                Circle(
                    radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o
                ).move_to(TRI_C)
                for r, o in ((4.6, 0.030), (3.5, 0.034), (2.4, 0.030))
            ]
        )
        self.add(halo)
        self.halo = halo

    # ------------------------------------------------------------------- hook
    def act_hook(self):
        tri = Polygon(
            *VERTS,
            stroke_color=INK,
            stroke_width=3.2,
            stroke_opacity=0.9,
            fill_color=BLUE,
            fill_opacity=0.07,
        )
        corners = VGroup(*[Dot(v, radius=0.055, color=DIM) for v in VERTS])
        self.tri = tri

        P0 = path_point(0.0)
        d0 = dists(P0)
        self.pdot = Dot(P0, radius=0.10, color=INK)
        self.pring = Circle(
            radius=0.21, stroke_color=INK, stroke_width=2, stroke_opacity=0.55
        ).move_to(P0)
        self.perps = VGroup(
            *[
                Line(P0, P0, stroke_color=SIDES[i][2], stroke_width=3.4)
                for i in range(3)
            ]
        )
        self.marks = VGroup(
            *[VMobject(stroke_color=SIDES[i][2], stroke_width=2.0) for i in range(3)]
        )
        for i in range(3):
            self.set_perp(self.perps[i], i, P0)
            self.set_mark(self.marks[i], i, P0)

        kick = pill("VIVIANI'S THEOREM", 28, ACID)
        head = txt("Three distances. One point.", 42, INK, weight=BOLD)
        self.top_hook = stack([kick, head], top=TOP_TOP, buff=0.34)

        rows, nums = [], []
        for i in range(3):
            r, n = self.d_row(i, d0[i])
            rows.append(r)
            nums.append(n)
        self.nums = nums
        note = body("Drop a perpendicular from the point to each side.", color=DIM)
        self.bot_hook = stack(rows + [note], top=BOT_TOP, buff=0.30)
        self.rows = VGroup(*rows)
        self.anchors = [n.get_center().copy() for n in nums]

        self.total = DecimalNumber(H, num_decimal_places=2, font_size=42, color=ACID)
        self.total_anchor = np.array([0.0, -6.0, 0.0])

        with self.voiceover(
            "Pick any point inside this triangle. Drop a perpendicular to each "
            "of the three sides. Three lengths, three colours."
        ) as tr:
            d = tr.duration
            self.play(Create(tri), FadeIn(corners), run_time=d * 0.26)
            self.play(FadeIn(kick), FadeIn(head), run_time=d * 0.16)
            self.play(FadeIn(self.pdot), FadeIn(self.pring), run_time=d * 0.12)
            for i in range(3):
                self.play(
                    Create(self.perps[i]),
                    Create(self.marks[i]),
                    FadeIn(rows[i], shift=RIGHT * 0.15),
                    run_time=d * 0.13,
                )
            self.play(FadeIn(note), run_time=d * 0.07)
            self.rest(tr)
        self.corners = corners
        self.note_hook = note

    # ------------------------------------------------------------------ drift
    def act_drift(self):
        head = txt("Now move the point.", 42, GOLD, weight=BOLD)
        self.top_drift = stack([head], top=TOP_TOP - 0.96)

        d0 = dists(path_point(0.0))
        self.segs = VGroup(*[make_bar(SIDES[i][2]) for i in range(3)])
        for i in range(3):
            lo = BAR_Y0 + sum(d0[:i])
            set_bar(self.segs[i], BAR_X, lo, lo + d0[i])

        base_line = DashedLine(
            [BAR_X - 0.55, BAR_Y0, 0.0],
            [BAR_X + 0.55, BAR_Y0, 0.0],
            stroke_color=DIM,
            stroke_width=1.6,
            dash_length=0.08,
        )
        apex_line = DashedLine(
            VA,
            [BAR_X + 0.55, VA[1], 0.0],
            stroke_color=ACID,
            stroke_width=1.8,
            stroke_opacity=0.75,
            dash_length=0.09,
        )
        arrow = DoubleArrow(
            [ARROW_X, BAR_Y0, 0.0],
            [ARROW_X, BAR_Y0 + H, 0.0],
            buff=0,
            stroke_width=3,
            color=ACID,
            max_tip_length_to_length_ratio=0.055,
        )
        h_lab = tex("h", 38, ACID, 0.6).move_to([2.28, 2.20, 0.0])

        sw = Square(side_length=0.26, fill_color=ACID, fill_opacity=1, stroke_width=0)
        lab = txt("total", 32, ACID, 1.8)
        total_row = VGroup(sw, lab, self.total).arrange(RIGHT, buff=0.28)
        eq = tex(r"=\;h", 36, ACID, 1.2)
        total_row = VGroup(total_row, eq).arrange(RIGHT, buff=0.24)
        self.bot_drift = stack([total_row], top=BOT_TOP - 1.98)
        self.total_anchor = self.total.get_center().copy()
        self.total.update(0)

        u = ValueTracker(0.0)
        self.bind(lambda: path_point(u.get_value()), bar=True)

        with self.voiceover(
            "Every length changes. But watch the stack on the right: the total "
            "never moves. It is always exactly the altitude."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.top_hook),
                FadeOut(self.note_hook),
                FadeIn(head),
                run_time=d * 0.12,
            )
            self.play(
                FadeIn(self.segs),
                FadeIn(base_line),
                FadeIn(total_row),
                run_time=d * 0.16,
            )
            self.play(
                Create(arrow), FadeIn(h_lab), Create(apex_line), run_time=d * 0.14
            )
            self.play(
                u.animate.set_value(1.0), run_time=max(4.0, d * 0.44), rate_func=linear
            )
            self.play(
                u.animate.set_value(FREEZE_U),
                run_time=max(1.2, d * 0.14),
                rate_func=linear,
            )
            self.rest(tr)

        self.unbind(bar=True)
        self.bar_grp = VGroup(self.segs, base_line, apex_line, arrow, h_lab)
        self.total_row = total_row
        self.head_drift = head

    # ------------------------------------------------------------------ proof
    def act_proof(self):
        P = PF
        d = dists(P)
        subs = VGroup(
            Polygon(P, VB, VC, stroke_width=0, fill_color=CYAN, fill_opacity=0.26),
            Polygon(P, VA, VB, stroke_width=0, fill_color=GOLD, fill_opacity=0.26),
            Polygon(P, VC, VA, stroke_width=0, fill_color=MAGENTA, fill_opacity=0.26),
        )
        spokes = VGroup(
            *[
                Line(P, v, stroke_color=INK, stroke_width=2.0, stroke_opacity=0.75)
                for v in VERTS
            ]
        )
        head = txt("Same base. Three heights.", 42, GOLD, weight=BOLD)
        self.top_proof = stack([head], top=TOP_TOP - 0.96)

        rows = []
        for i in range(3):
            col = SIDES[i][2]
            sw = Square(
                side_length=0.26, fill_color=col, fill_opacity=1, stroke_width=0
            )
            form = tex(rf"\tfrac{{1}}{{2}}\,s\,d_{i + 1}", 34, col, 2.6)
            val = tex(rf"= {0.5 * SIDE * d[i]:.2f}", 34, INK, 2.2)
            rows.append(VGroup(sw, form, val).arrange(RIGHT, buff=0.26))
        whole = tex(
            rf"\text{{whole triangle}} = {shoelace(VERTS):.2f}", 32, ACID, COL_W
        )
        note = body("Together they fill it exactly. No gaps, no overlap.", color=DIM)
        self.bot_proof = stack(rows + [whole, note], top=BOT_TOP, buff=0.28)

        with self.voiceover(
            "Here is the whole proof. Join the point to the three corners. "
            "Three triangles, all with the same base, and their areas fill the "
            "whole triangle."
        ) as tr:
            d_ = tr.duration
            self.play(
                FadeOut(self.bar_grp),
                FadeOut(self.total_row),
                FadeOut(self.rows),
                FadeOut(self.head_drift),
                FadeIn(head),
                run_time=d_ * 0.16,
            )
            self.play(
                LaggedStart(*[Create(s) for s in spokes], lag_ratio=0.12),
                run_time=d_ * 0.20,
            )
            for i in range(3):
                self.play(
                    FadeIn(subs[i]),
                    FadeIn(rows[i], shift=RIGHT * 0.15),
                    run_time=d_ * 0.15,
                )
            self.play(FadeIn(whole), FadeIn(note), run_time=d_ * 0.19)
            self.rest(tr)
        self.subs, self.spokes = subs, spokes
        self.head_proof = head

    # ----------------------------------------------------------------- cancel
    def act_cancel(self):
        d = dists(PF)
        head = txt("Cancel the base.", 42, GOLD, weight=BOLD)
        self.top_cancel = stack([head], top=TOP_TOP - 0.96)

        line1 = tex(
            r"\tfrac{1}{2}s\,d_1+\tfrac{1}{2}s\,d_2+\tfrac{1}{2}s\,d_3"
            r"=\tfrac{1}{2}s\,h",
            36,
            INK,
            COL_W,
        )
        line2 = tex(r"d_1+d_2+d_3 \;=\; h", 60, ACID, COL_W)
        box = SurroundingRectangle(
            line2, color=ACID, buff=0.24, stroke_width=2.6, stroke_opacity=0.9
        )
        nums = tex(rf"{d[0]:.2f}+{d[1]:.2f}+{d[2]:.2f}={sum(d):.2f}", 34, DIM, COL_W)
        self.bot_cancel = stack([line1, line2, nums], top=BOT_TOP - 0.20, buff=0.36)
        box.move_to(line2.get_center())

        with self.voiceover(
            "Area is base times height over two. The base is the same every "
            "time, so cancel it. The three heights must add to the altitude."
        ) as tr:
            d_ = tr.duration
            self.play(
                FadeOut(self.bot_proof),
                FadeOut(self.head_proof),
                self.subs.animate.set_fill(opacity=0.12),
                FadeIn(head),
                run_time=d_ * 0.16,
            )
            self.play(Write(line1), run_time=d_ * 0.30)
            self.play(Write(line2), Create(box), run_time=d_ * 0.30)
            self.play(
                FadeIn(nums),
                Flash(
                    line2, color=ACID, line_length=0.30, num_lines=18, flash_radius=2.4
                ),
                run_time=d_ * 0.24,
            )
            self.rest(tr)
        self.head_cancel = head
        self.box_cancel = box

    # ---------------------------------------------------------------- outside
    def act_outside(self):
        head = txt("Now step outside.", 42, MAGENTA, weight=BOLD)
        self.top_out = stack([head], top=TOP_TOP - 0.96)

        dnow = dists(PF)
        rows, nums = [], []
        for i in range(3):
            r, n = self.d_row(i, dnow[i])
            rows.append(r)
            nums.append(n)
        self.nums = nums
        sw = Square(side_length=0.26, fill_color=ACID, fill_opacity=1, stroke_width=0)
        total_row = VGroup(sw, txt("total", 32, ACID, 1.8), self.total).arrange(
            RIGHT, buff=0.28
        )
        total_row = VGroup(total_row, tex(r"=\;h", 36, ACID, 1.2)).arrange(
            RIGHT, buff=0.24
        )
        note = body("One distance counts negative. The total still holds.", color=RED)
        self.bot_out = stack(rows + [total_row, note], top=BOT_TOP, buff=0.28)
        self.anchors = [n.get_center().copy() for n in nums]
        self.total_anchor = self.total.get_center().copy()
        self.total.update(0)

        v = ValueTracker(0.0)
        self.bind(lambda: PF + v.get_value() * (P_OUT - PF))

        with self.voiceover(
            "One distance goes negative. Count it as negative and the total "
            "still holds. It never breaks."
        ) as tr:
            d_ = tr.duration
            self.play(
                FadeOut(self.bot_cancel),
                FadeOut(self.box_cancel),
                FadeOut(self.head_cancel),
                FadeOut(self.subs),
                FadeOut(self.spokes),
                FadeIn(head),
                run_time=d_ * 0.20,
            )
            self.play(
                LaggedStart(
                    *[FadeIn(r, shift=RIGHT * 0.15) for r in rows], lag_ratio=0.10
                ),
                FadeIn(total_row),
                run_time=d_ * 0.22,
            )
            self.play(
                v.animate.set_value(1.0), run_time=max(2.4, d_ * 0.40), rate_func=smooth
            )
            self.play(FadeIn(note), run_time=d_ * 0.14)
            self.rest(tr)
        self.unbind()
        self.head_out = head

    # ---------------------------------------------------------------- general
    def act_general(self):
        verts = ngon_verts(NGON_N, NGON_R, NGON_C)
        a = NGON_A
        P = NGON_C + 0.34 * a * np.array([np.cos(0.7), np.sin(0.7), 0.0])
        poly = Polygon(
            *verts,
            stroke_color=INK,
            stroke_width=2.6,
            stroke_opacity=0.85,
            fill_color=BLUE,
            fill_opacity=0.06,
        )
        rays = VGroup()
        for i in range(NGON_N):
            U, V = verts[i], verts[(i + 1) % NGON_N]
            F, _ = foot(P, U, V)
            rays.add(
                Line(P, F, stroke_color=SIX[i], stroke_width=3.0, stroke_opacity=0.95)
            )
        pd = Dot(P, radius=0.085, color=INK)
        total = ngon_dist_sum(P, verts)
        assert abs(total - NGON_N * a) < 1e-9

        head = txt("Any regular polygon.", 42, GOLD, weight=BOLD)
        self.top_gen = stack([head], top=TOP_TOP - 0.96)

        chip = tex(rf"\sum d_i = 6a = {total:.2f}", 38, ACID, COL_W)
        formula = tex(r"\sum_{i=1}^{n} d_i \;=\; n\,a", 48, INK, COL_W)
        sub = body(
            "n sides, n distances, one fixed total: n times the apothem.", color=DIM
        )
        self.bot_gen = stack([chip, formula, sub], top=-0.95, buff=0.30)

        with self.voiceover(
            "And any regular polygon does the same. N sides, n distances, "
            "one fixed total: n times the apothem."
        ) as tr:
            d_ = tr.duration
            self.play(
                FadeOut(self.bot_out),
                FadeOut(self.head_out),
                FadeOut(self.tri),
                FadeOut(self.corners),
                FadeOut(self.perps),
                FadeOut(self.marks),
                FadeOut(self.pdot),
                FadeOut(self.pring),
                run_time=d_ * 0.20,
            )
            self.play(FadeIn(head), Create(poly), run_time=d_ * 0.22)
            self.play(
                FadeIn(pd),
                LaggedStart(*[Create(r) for r in rays], lag_ratio=0.08),
                run_time=d_ * 0.28,
            )
            self.play(FadeIn(chip), Write(formula), run_time=d_ * 0.20)
            self.play(FadeIn(sub), run_time=d_ * 0.10)
            self.rest(tr)

        name = txt("VIVIANI'S THEOREM", 56, INK, COL_W, weight=BOLD)
        name.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        who = txt("Vincenzo Viviani · 1622–1703", 28, DIM, COL_W)
        tag = tex(r"d_1+d_2+d_3=h", 52, GOLD, 6.0)
        cards = stack([name, who, tag], top=-1.15, buff=0.34)

        with self.voiceover("The point moves. The sum never does.") as tr:
            self.play(
                FadeOut(poly),
                FadeOut(rays),
                FadeOut(pd),
                FadeOut(self.bot_gen),
                FadeOut(self.top_gen),
                run_time=0.9,
            )
            self.play(FadeIn(name, scale=0.9), run_time=1.0)
            self.play(FadeIn(who), Write(tag), run_time=1.1)
            self.rest(tr)
        self.wait(1.0)
        self.play(FadeOut(VGroup(cards, self.halo)), run_time=1.3)
        self.wait(0.4)
