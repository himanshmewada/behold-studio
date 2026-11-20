# Video script 9
"""
THE CIRCLES THAT KISS  ·  16:9 YouTube video  ·  1920x1080  ·  ~4 min 40 s
=========================================================================
Descartes' circle theorem, the flip that generates the Apollonian gasket,
and the miracle that every bend in an integral packing is a whole number.

THE MATHEMATICS (exact integer arithmetic, asserted at import)
-------------------------------------------------------------
Bend            k = 1/r, SIGNED: an enclosing circle carries k < 0.
Descartes       (k1+k2+k3+k4)^2 = 2(k1^2+k2^2+k3^2+k4^2)
Complex form    with w = k*z:  (w1+w2+w3+w4)^2 = 2(w1^2+w2^2+w3^2+w4^2)
Quadratic       k4 = s +/- 2*sqrt(k1k2 + k2k3 + k3k1),  s = k1+k2+k3
The flip        the two roots sum to 2s, so knowing one circle gives the
                other for free, with NO square root:
                    k_new = 2(k1+k2+k3) - k_old
                    w_new = 2(w1+w2+w3) - w_old
Tangency        for any tangent pair in a configuration: |zi - zj| = |1/ki + 1/kj|
Seed            k = (-1, 2, 2, 3),  w = (0, -1, 1, 2i)   -> Gaussian integers.
                Every flip is an integer combination, so EVERY bend in the
                packing is an integer, forever. Verified exactly, not to 1e-9.
Coverage        disc area pi, circle area pi/k^2  ->  covered fraction = sum 1/k^2
                over k > 0. Rises toward 1; the residual dust has zero area.

LAYOUT RULES (house style)
--------------------------
* HUD chip on HUD_Y, progress rail on RAIL_Y, column only via stack().
* Long copy wrapped, never shrunk; \tfrac inline, \frac on display lines.
* One .animate chain per mobject per play(); updaters cleared before FadeOut.
* No DecimalNumber: counters are static Texts swapped by ReplacementTransform.
* Every act fades its own panel. Recolour carries meaning only:
  BLUE seed, GOLD the answer, CYAN the flip, then one hue per generation.

SETUP / RENDER
--------------
pip install manim "manim-voiceover[gtts]" numpy
manim -pql videos/video9.py TheCirclesThatKiss   # draft
manim -pqh videos/video9.py TheCirclesThatKiss   # 1080p + narration
PREVIEW = True -> 854x480.  No voiceover lib? Renders as a paced silent cut.
"""

from contextlib import contextmanager
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
GEN = [BLUE, CYAN, "#3aa0ff", ACID, MAGENTA, "#a06bff"]

# ------------------------------------------------------------- layout grid
HUD_Y = 3.80
COL_TOP = 3.02
COL_L = 0.55
COL_W = 6.20
RAIL_Y, RAIL_X0, RAIL_X1 = -3.74, -6.55, 6.55
CHAPTERS = [
    (0.00, "01 / THE GAP"),
    (0.15, "02 / BEND, NOT RADIUS"),
    (0.31, "03 / THE EQUATION"),
    (0.50, "04 / THE FLIP"),
    (0.66, "05 / THE GASKET"),
    (0.88, "06 / WHOLE NUMBERS, FOREVER"),
]

# ------------------------------------------------------------------- stage
STAGE_C = np.array([-3.55, -0.15, 0.0])
SCALE = 2.85
MIN_R = 0.010  # screen radius below which a circle is sub-pixel


def S(z):
    return STAGE_C + SCALE * np.array([z.real, z.imag, 0.0])


# --------------------------------------------------------------- the packing
DEPTH = 5
K = [-1, 2, 2, 3]  # signed bends (ints)
W = [0j, complex(-1, 0), complex(1, 0), complex(0, 2)]  # w = k*z, Gaussian ints
Z = [w / k for w, k in zip(W, K)]
LEVELS = [[0, 1, 2, 3]]
QUADS = [(0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 3, 1), (1, 2, 3, 0)]


def build(depth):
    tasks = list(QUADS)
    for _ in range(depth):
        nxt, level = [], []
        for a, b, c, d in tasks:
            kn = 2 * (K[a] + K[b] + K[c]) - K[d]
            wn = 2 * (W[a] + W[b] + W[c]) - W[d]
            i = len(K)
            K.append(kn)
            W.append(wn)
            Z.append(wn / kn)
            level.append(i)
            QUADS.append((a, b, c, i))
            nxt += [(a, b, i, c), (a, c, i, b), (b, c, i, a)]
        LEVELS.append(level)
        tasks = nxt


build(DEPTH)
ANS_IDX = next(i for i in LEVELS[1] if K[i] == 15)
FLIP_IDX = next(i for i in LEVELS[1] if Z[i].imag < -0.5)
COVERAGE = []
_run = 0.0
for lvl in LEVELS:
    _run += sum(1.0 / (K[i] * K[i]) for i in lvl if K[i] > 0)
    COVERAGE.append(_run)
DRAWABLE = [i for i in range(len(K)) if SCALE / abs(K[i]) >= MIN_R]


def descartes(ks):
    s = sum(ks)
    return s * s - 2 * sum(k * k for k in ks)


def cdescartes(ws):
    s = sum(ws)
    return s * s - 2 * sum(w * w for w in ws)


def touch_point(i, j):
    ri = 1.0 / K[i]
    d = Z[j] - Z[i]
    return Z[i] + ri * d / abs(d)


def verify():
    assert descartes(K[:4]) == 0, "seed must satisfy Descartes exactly"
    assert cdescartes(W[:4]) == 0, "seed must satisfy complex Descartes exactly"
    for i in range(len(K)):
        assert isinstance(K[i], int), "every bend must be an integer"
        assert W[i].real == int(W[i].real) and W[i].imag == int(W[i].imag), (
            "every bend-centre must be a Gaussian integer"
        )
    worst = 0.0
    for a, b, c, d in QUADS:
        q = (a, b, c, d)
        assert descartes([K[i] for i in q]) == 0, "Descartes must be exact"
        assert cdescartes([W[i] for i in q]) == 0, "complex Descartes must be exact"
        for x in range(4):
            for y in range(x + 1, 4):
                i, j = q[x], q[y]
                got = abs(Z[i] - Z[j])
                want = abs(1.0 / K[i] + 1.0 / K[j])
                worst = max(worst, abs(got - want))
    assert worst < 1e-9, f"tangency drift {worst}"
    a, b, c = K[1], K[2], K[3]
    s, disc = a + b + c, a * b + b * c + c * a
    root = int(round(np.sqrt(disc)))
    assert root * root == disc and s + 2 * root == 15 and s - 2 * root == -1
    assert K[FLIP_IDX] == 2 * (K[0] + K[1] + K[2]) - K[3]
    back = 2 * (K[0] + K[1] + K[2]) - K[FLIP_IDX]
    assert back == K[3], "the flip must be an involution"
    assert all(COVERAGE[i] < COVERAGE[i + 1] < 1.0 for i in range(len(COVERAGE) - 1))
    print(f"  seed bends {K[:4]} | Descartes residual {descartes(K[:4])} (exact)")
    print(
        f"  packing: {len(K)} circles, {len(QUADS)} Descartes quadruples, depth {DEPTH}"
    )
    print(f"  every bend integer, every bend-centre Gaussian integer  [exact]")
    print(f"  worst tangency error over all pairs: {worst:.2e}")
    print(
        f"  triple (2,2,3): s={s}, disc={disc} -> bends {s + 2 * root} and {s - 2 * root}"
    )
    print(f"  drawn above one pixel: {len(DRAWABLE)} of {len(K)}")
    print("  coverage by level: " + ", ".join(f"{c * 100:.2f}%" for c in COVERAGE))


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


# ===================================================================== scene
class TheCirclesThatKiss(Base):
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

    # ---------------------------------------------------------------- circles
    def cmob(self, i, col, sw=2.4, fo=0.07):
        return Circle(
            radius=SCALE / abs(K[i]),
            stroke_color=col,
            stroke_width=sw,
            stroke_opacity=0.95,
            fill_color=col,
            fill_opacity=fo,
        ).move_to(S(Z[i]))

    def gap_region(self, idxs, g, col=MAGENTA):
        """The curvilinear triangle, sampled from the three exact arcs."""
        pts = []
        for n, i in enumerate(idxs):
            j, k = idxs[(n + 1) % 3], idxs[(n + 2) % 3]
            t1, t2 = touch_point(i, j), touch_point(i, k)
            a1 = np.angle(t1 - Z[i])
            a2 = np.angle(t2 - Z[i])
            sweep = (a2 - a1) % TAU
            mid_a = a1 + sweep / 2
            mid_b = a1 + (sweep - TAU) / 2
            r = 1.0 / K[i]
            pa = Z[i] + r * complex(np.cos(mid_a), np.sin(mid_a))
            pb = Z[i] + r * complex(np.cos(mid_b), np.sin(mid_b))
            if abs(pb - g) < abs(pa - g):
                sweep -= TAU
            for t in np.linspace(0, 1, 48):
                a = a1 + sweep * t
                pts.append(S(Z[i] + r * complex(np.cos(a), np.sin(a))))
        m = VMobject(
            stroke_color=col,
            stroke_width=2,
            stroke_opacity=0.8,
            fill_color=col,
            fill_opacity=0.20,
        )
        m.set_points_as_corners(pts + [pts[0]])
        return m

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
        lab = txt(name, 18, DIM, 5.6).move_to([-6.55, HUD_Y, 0], aligned_edge=LEFT)
        anims = [self.prog.animate.set_value(max(0.004, frac)), FadeIn(lab)]
        if self._chap is not None:
            anims.append(FadeOut(self._chap))
        self.play(*anims, run_time=run_time)
        self._chap = lab

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.cm = {}
        self.drawn = set()
        self.build_hud()
        self.act_gap()
        self.act_bend()
        self.act_equation()
        self.act_flip()
        self.act_gasket()
        self.act_payoff()

    # ================================================================== ACT 1
    def act_gap(self):
        self.chapter(0, run_time=0.8)
        seeds = VGroup(*[self.cmob(i, BLUE, 3.0, 0.08) for i in (1, 2, 3)])
        for n, i in enumerate((1, 2, 3)):
            self.cm[i] = seeds[n]
            self.drawn.add(i)
        gap = self.gap_region((1, 2, 3), Z[ANS_IDX])
        q = txt("?", 64, GOLD, 1.0).move_to(S(Z[ANS_IDX]))

        head = txt("THE GAP", 28, GOLD, weight=BOLD)
        n1 = body("Three circles. Each one touches the other two.")
        n2 = body("Between them: a gap bounded by three arcs.")
        n3 = body("Exactly one circle fits it, kissing all three.", color=GOLD)
        n4 = body("How big is it?", size=23, color=DIM)
        col = self.stack([head, n1, n2, n3, n4], buff=0.32)

        with self.voiceover(
            "Three circles. Each one touches the other two. Between them "
            "sits a gap, bounded by three arcs."
        ) as tr:
            d = tr.duration
            self.play(
                LaggedStart(*[Create(c) for c in seeds], lag_ratio=0.15),
                FadeIn(head),
                FadeIn(n1),
                run_time=d * 0.60,
            )
            self.play(FadeIn(gap), FadeIn(n2), run_time=d * 0.32)
            self.rest(tr)

        with self.voiceover(
            "Exactly one circle fits that gap, kissing all three. How big "
            "is it? You could fit it by eye. But the answer is a number, "
            "and numbers come from equations."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(q, scale=0.7), FadeIn(n3), run_time=d * 0.40)
            self.play(FadeIn(n4), run_time=d * 0.20)
            self.rest(tr)
        self.col1 = col
        self.gap_grp = VGroup(gap, q)

    # ================================================================== ACT 2
    def act_bend(self):
        self.chapter(1)
        outer = self.cmob(0, DIM, 2.6, 0.0)
        self.cm[0] = outer
        self.drawn.add(0)
        labs = VGroup(
            *[
                Integer(K[i], font_size=40, color=INK).move_to(S(Z[i]))
                for i in (1, 2, 3)
            ]
        )
        o_lab = Integer(-1, font_size=36, color=DIM).move_to(
            STAGE_C + 2.50 * np.array([np.cos(2.36), np.sin(2.36), 0.0])
        )

        head = txt("BEND, NOT RADIUS", 28, GOLD, weight=BOLD)
        rule = tex(r"k = \frac{1}{r}", 46, CYAN)
        n1 = body("Small circles bend hard. Big circles bend gently.")
        n2 = body(
            "A circle that wraps around the others gets a negative bend.", color=DIM
        )
        quad = tex(r"(k_1,k_2,k_3,k_4) = (-1,\,2,\,2,\,3)", 34, INK)
        self.stack([head, rule, n1, n2, quad], buff=0.30)

        with self.voiceover(
            "Don't measure the radius. Measure the bend: one over the "
            "radius. Small circles bend hard, big circles bend gently. "
            "These three have bends two, two and three."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.col1), FadeOut(self.gap_grp), run_time=d * 0.16)
            self.play(FadeIn(head), Write(rule), FadeIn(labs), run_time=d * 0.36)
            self.play(FadeIn(n1), run_time=d * 0.20)
            self.rest(tr)

        with self.voiceover(
            "And here is the trick. The circle that wraps around them all "
            "counts too, with a negative bend. Minus one. It kisses the "
            "others from the outside in. Four circles, each kissing the "
            "other three."
        ) as tr:
            d = tr.duration
            self.play(Create(outer), FadeIn(o_lab), run_time=d * 0.34)
            self.play(FadeIn(n2), run_time=d * 0.22)
            self.play(Write(quad), run_time=d * 0.26)
            self.rest(tr)
        self.col2 = VGroup(head, rule, n1, n2, quad)
        self.seed_labs = VGroup(labs, o_lab)

    # ================================================================== ACT 3
    def act_equation(self):
        self.chapter(2)
        head = txt("THE EQUATION", 28, GOLD, weight=BOLD)
        eq = tex(
            r"(k_1+k_2+k_3+k_4)^2 = 2\left(k_1^2+k_2^2+k_3^2+k_4^2\right)",
            34,
            INK,
        )
        chk = tex(r"6^2 = 36 \qquad 2(1+4+4+9) = 36", 30, ACID)
        solve = tex(r"k_4 = s \pm 2\sqrt{k_1k_2+k_2k_3+k_3k_1}", 32, CYAN)
        nums = tex(r"k_4 = 7 \pm 2\sqrt{16} = 7 \pm 8", 34, CYAN)
        two = tex(r"k_4 = 15 \quad\text{or}\quad -1", 40, GOLD)
        n1 = body(
            "Both roots are real circles: the tiny one in the gap, "
            "and the big one already wrapped around them.",
            size=23,
            color=DIM,
        )
        self.stack([head, eq, chk, solve, nums, two, n1], buff=0.26)

        ans = self.cmob(ANS_IDX, GOLD, 3.0, 0.30)
        self.cm[ANS_IDX] = ans
        self.drawn.add(ANS_IDX)
        ans_lab = Integer(15, font_size=24, color=BG).move_to(S(Z[ANS_IDX]))

        with self.voiceover(
            "Sixteen forty three. Descartes writes down the relation. The "
            "square of the sum of the four bends equals twice the sum of "
            "their squares. Check it. Sum six, squared thirty six. Squares "
            "one, four, four, nine, doubled: thirty six. Exact."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.col2), FadeIn(head), run_time=d * 0.16)
            self.play(Write(eq), run_time=d * 0.34)
            self.play(Write(chk), run_time=d * 0.30)
            self.rest(tr)

        with self.voiceover(
            "Solve it for the fourth bend and a plus or minus appears. "
            "Seven, plus or minus eight. Fifteen, or minus one. Both "
            "answers are real circles. The minus one is the wrapper we "
            "already drew. The fifteen is the answer in the gap."
        ) as tr:
            d = tr.duration
            self.play(Write(solve), run_time=d * 0.20)
            self.play(Write(nums), run_time=d * 0.18)
            self.play(Write(two), run_time=d * 0.16)
            self.play(
                Indicate(self.cm[0], color=DIM, scale_factor=1.03), run_time=d * 0.12
            )
            self.play(
                FadeIn(ans, scale=0.6),
                FadeIn(ans_lab),
                FadeIn(n1),
                run_time=d * 0.24,
            )
            self.rest(tr)
        self.col3 = VGroup(head, eq, chk, solve, nums, two, n1)
        self.ans_lab = ans_lab

    # ================================================================== ACT 4
    def act_flip(self):
        self.chapter(3)
        head = txt("THE FLIP", 28, GOLD, weight=BOLD)
        n1 = body("The two roots add to twice the sum of the other three.")
        flip = tex(r"k_{\text{new}} = 2(k_1+k_2+k_3) - k_{\text{old}}", 34, ACID)
        n2 = body(
            "So if you know one circle, the other is free. No square "
            "root. Just subtract.",
            color=ACID,
        )
        cen = tex(r"w = k\,z:\quad w_{\text{new}} = 2\sum w - w_{\text{old}}", 30, CYAN)
        nums = tex(r"2(-1+2+2) - 3 = 3", 32, INK)
        n3 = body(
            "Flip again and it comes back. Every gap has exactly two "
            "circles, and the flip walks between them.",
            size=23,
            color=DIM,
        )
        self.stack([head, n1, flip, n2, cen, nums, n3], buff=0.26)

        new = self.cmob(FLIP_IDX, CYAN, 3.0, 0.22)
        self.cm[FLIP_IDX] = new
        self.drawn.add(FLIP_IDX)
        arrow = Arrow(
            S(Z[3]),
            S(Z[FLIP_IDX]),
            buff=0.35,
            stroke_width=3,
            color=CYAN,
            max_tip_length_to_length_ratio=0.06,
        )
        tag = Integer(K[FLIP_IDX], font_size=32, color=CYAN).move_to(S(Z[FLIP_IDX]))

        with self.voiceover(
            "Now the beautiful part. The two roots of a quadratic add up "
            "to twice the sum of the other three. So if you already know "
            "one circle, the other one is free. No square root. Just "
            "subtract. That is the whole engine."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.col3), FadeIn(head), FadeIn(n1), run_time=d * 0.18)
            self.play(Write(flip), run_time=d * 0.26)
            self.play(FadeIn(n2), run_time=d * 0.24)
            self.rest(tr)

        with self.voiceover(
            "The same flip works for the centres, weighted by bend. Flip "
            "the top circle across the other three, and it lands "
            "underneath. Flip again, and it comes back. One subtraction "
            "builds a circle guaranteed to kiss all three."
        ) as tr:
            d = tr.duration
            self.play(Write(cen), run_time=d * 0.18)
            self.play(
                self.cm[3].animate.set_fill(opacity=0.03).set_stroke(opacity=0.35),
                Create(arrow),
                run_time=d * 0.20,
            )
            self.play(
                FadeIn(new, scale=0.7), FadeIn(tag), Write(nums), run_time=d * 0.30
            )
            self.play(FadeIn(n3), run_time=d * 0.18)
            self.rest(tr)
        self.play(FadeOut(arrow), run_time=0.5)
        self.col4 = VGroup(head, n1, flip, n2, cen, nums, n3)
        self.flip_tag = tag

    # ================================================================== ACT 5
    def act_gasket(self):
        self.chapter(4)
        head = txt("THE GASKET", 28, GOLD, weight=BOLD)
        n1 = body("Every new circle makes three new gaps. Fill them. Fill those.")
        count = txt(f"{len(K)} circles", 34, INK)
        cov = txt(f"{COVERAGE[1] * 100:.1f}% of the disc", 30, CYAN)
        n2 = body(
            "Every tangency checked. Every Descartes identity exact.",
            size=23,
            color=DIM,
        )
        self.stack([head, n1, count, cov, n2], buff=0.30)

        with self.voiceover(
            "So recurse. Every new circle makes three new gaps. Fill them. "
            "Fill those. Four hundred eighty eight circles, and every "
            "tangency is checked to machine precision."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.col4),
                FadeOut(self.flip_tag),
                FadeOut(self.ans_lab),
                FadeIn(head),
                FadeIn(n1),
                run_time=d * 0.14,
            )
            self.play(FadeIn(count), FadeIn(cov), run_time=d * 0.10)
            for lvl in range(1, len(LEVELS)):
                mobs = VGroup()
                for i in LEVELS[lvl]:
                    if i in self.drawn or i not in DRAWABLE:
                        continue
                    col = GEN[min(lvl, len(GEN) - 1)]
                    m = self.cmob(i, col, max(0.7, 2.4 - 0.32 * lvl), 0.10)
                    self.cm[i] = m
                    self.drawn.add(i)
                    mobs.add(m)
                nxt = txt(f"{COVERAGE[lvl] * 100:.1f}% of the disc", 30, CYAN).move_to(
                    cov
                )
                anims = [ReplacementTransform(cov, nxt)]
                if len(mobs):
                    anims.append(
                        LaggedStart(
                            *[FadeIn(m, scale=0.7) for m in mobs], lag_ratio=0.01
                        )
                    )
                self.play(*anims, run_time=max(0.9, d * 0.13))
                cov = nxt
            self.play(FadeIn(n2), run_time=d * 0.10)
            self.rest(tr)
        self.cov = cov

        bends = sorted({K[i] for i in range(len(K)) if K[i] > 0})[:8]
        head2 = txt("LOOK AT THE BENDS", 28, GOLD, weight=BOLD)
        seq = tex(",\\ ".join(str(b) for b in bends) + r",\ \ldots", 34, ACID)
        n3 = body(
            "Every one a whole number. The flip only adds and "
            "subtracts integers, so it can never escape them.",
            color=ACID,
        )
        n4 = body("An infinite packing, and not one fraction.", size=23, color=DIM)
        self.stack([head2, seq, n3, n4], top=-0.65, buff=0.28)

        with self.voiceover(
            "And look at the bends. Two, three, six, fifteen. Every single "
            "one is a whole number. The flip only ever adds and subtracts "
            "integers, so it can never escape them. An infinite packing, "
            "and not one fraction."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(head2), Write(seq), run_time=d * 0.34)
            self.play(FadeIn(n3), run_time=d * 0.34)
            self.play(FadeIn(n4), run_time=d * 0.20)
            self.rest(tr)
        self.col5 = VGroup(head, n1, count, self.cov, n2, head2, seq, n3, n4)

    # ================================================================== ACT 6
    def act_payoff(self):
        self.chapter(5)
        head = txt("WHOLE NUMBERS, FOREVER", 28, GOLD, weight=BOLD)
        n1 = body(
            "Four integer bends satisfying the equation force the "
            "next one to be an integer. Induction does the rest."
        )
        n2 = body(
            f"The circles fill {COVERAGE[-1] * 100:.1f}% of the disc here. "
            "Carried to infinity, the leftover dust has no area at all.",
            color=CYAN,
        )
        quote = body(
            '"The sum of the squares of all four bends is half the square '
            'of their sum."',
            size=23,
            color=INK,
        )
        who = txt("Frederick Soddy, Nature, 1936 — written as a poem", 21, DIM)
        self.stack([head, n1, n2, quote, who], buff=0.30)

        with self.voiceover(
            "Start with four whole numbers that satisfy the equation, and "
            "the flip can only ever produce another whole number. "
            "Induction does the rest. The circles fill the disc: carried "
            "to infinity, the leftover dust has no area at all. In nineteen "
            "thirty six the chemist Frederick Soddy published this theorem "
            "as a poem. The sum of the squares of all four bends is half "
            "the square of their sum."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.col5), FadeIn(head), run_time=d * 0.12)
            self.play(FadeIn(n1), run_time=d * 0.20)
            self.play(FadeIn(n2), run_time=d * 0.20)
            self.play(FadeIn(quote), run_time=d * 0.24)
            self.play(FadeIn(who), run_time=d * 0.12)
            self.rest(tr)

        card = tex(r"(k_1+k_2+k_3+k_4)^2 = 2\sum k_i^2", 56, GOLD, 9.0).move_to(
            [0, 1.10, 0]
        )
        sub = txt("Descartes · 1643     Soddy · 1936", 26, DIM, 8.0).move_to(
            [0, 0.10, 0]
        )
        tag = txt("THE CIRCLES THAT KISS", 34, INK, 9.0, weight=BOLD).move_to(
            [0, -1.15, 0]
        )
        tag.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        stage = VGroup(*self.cm.values(), self.seed_labs)

        with self.voiceover(
            "Four circles, one equation, and an infinite family of whole "
            "numbers. The picture is the proof."
        ) as tr:
            self.play(
                FadeOut(VGroup(head, n1, n2, quote, who)), FadeOut(stage), run_time=1.0
            )
            self.play(Write(card), run_time=1.2)
            self.play(FadeIn(sub), FadeIn(tag, shift=UP * 0.15), run_time=1.1)
            self.rest(tr)
        self.wait(1.6)
        self.play(self.prog.animate.set_value(1.0), run_time=1.0)
        self.rail_fill.clear_updaters()
        self.play(FadeOut(VGroup(card, sub, tag, self._chap)), run_time=1.4)
        self.wait(0.5)
