"""
THE MOST IRRATIONAL NUMBER  ·  16:9 YouTube video  ·  1920x1080  ·  ~4 min 50 s
==============================================================================
Why sunflowers count in Fibonacci — and why the answer is a number that
fractions can never catch.

LAYOUT RULES (these caused the earlier visual defects)
-----------------------------------------------------
* HUD chip lives on its own row (HUD_Y); act titles live on TITLE_Y. They can
  never share a band.
* Right-column content is placed by stack(), which advances a cursor by each
  mobject's REAL height + buff. Stacked fractions cannot overlap the next row.
* Inline fractions in stacked rows use \tfrac; \frac/\cfrac are reserved for
  stand-alone display equations.
* Every phase clears the previous phase's panel before writing a new one.
* Long sentences are wrapped, never scaled down to fit.

MATHEMATICS (all on-screen numbers are computed)
-----------------------------------------------
Vogel model        seed k -> (r, theta) = (c*sqrt(k), 360deg * k * t)
t                  fraction of ONE FULL TURN. Used consistently everywhere.
Golden angle       t = 1/phi^2 = 0.3819660113  ->  137.5077640 degrees
Rational t = p/q   exactly q rays, forever
Parastichies       seeds k, k+F, k+2F... form one spiral; residues mod F give
                   EXACTLY F spirals.
                   34t = 12.986844 turns -> offset -4.736 deg
                   55t = 21.008131 turns -> offset +2.927 deg  (opposite curl)
Continued fractions  phi = [1;1,1,...] -> convergents F(n+1)/F(n)
                   |phi - p/q| q^2 -> 1/sqrt5 = 0.4472136   (Hurwitz limit)
                   |sqrt2 - p/q| q^2 -> 1/(2sqrt2) = 0.3535534
                   pi = [3;7,15,1,292,...] -> 355/113 dives to 0.0034
Golden rectangle   side r(i) = phi^-i, centre recurrence
                   c(i+1) = c(i) + (r(i) - r(i+1)) u(i), each arc 90deg CCW
                   -> tangent-continuous quarter circles, exact.

SETUP / RENDER
--------------
    pip install manim "manim-voiceover[gtts]"
    manim -p golden.py TheMostIrrationalNumber
    PREVIEW = True  -> 854x480 draft      FPS = 60 -> smoother, slower render

MANIM 0.22 RULES OBEYED
-----------------------
    * no set_width/set_height kwargs -> .scale()
    * DecimalNumber pre-synced with .update(0) and rebuilt only on change
    * one .animate chain per mobject per play()
    * reveal updaters cleared before any FadeOut
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
BG = "#080a0c"
SURFACE = "#141a20"
EDGE = "#242d38"
INK = "#f3ece0"
DIM = "#8b939e"
GOLD = "#ffc233"
CYAN = "#2ee6d6"
MAGENTA = "#ff3d8b"
ACID = "#a3e635"
RED = "#ff5252"
SEEDS = [
    "#fff3b0",
    "#ffd166",
    "#ffa62b",
    "#ff6b35",
    "#ef476f",
    "#b5179e",
    "#7209b7",
    "#3a86ff",
]

# ------------------------------------------------------------- layout grid
HUD_Y = 3.80  # chapter chip row (nothing else may sit here)
TITLE_Y = 3.24  # centred act titles
COL_TOP = 3.02  # right column cursor start
COL_L = 0.45  # right column left edge
COL_W = 6.30  # right column max width
RAIL_Y, RAIL_X0, RAIL_X1 = -3.74, -6.55, 6.55

CHAPTERS = [
    (0.00, "01 / THE PATTERN"),
    (0.11, "02 / THE RECIPE"),
    (0.27, "03 / WHY FRACTIONS FAIL"),
    (0.44, "04 / THE MOST IRRATIONAL NUMBER"),
    (0.70, "05 / WHY FIBONACCI"),
    (0.90, "06 / THE PAYOFF"),
]

# --------------------------------------------------------------------- math
PHI = (1.0 + np.sqrt(5.0)) / 2.0
GOLD_T = 1.0 / PHI**2
GOLD_DEG = 360.0 * GOLD_T
HURWITZ = 1.0 / np.sqrt(5.0)


def hexlerp(h1, h2, t):
    a = np.array([int(h1[i : i + 2], 16) for i in (1, 3, 5)], dtype=float)
    b = np.array([int(h2[i : i + 2], 16) for i in (1, 3, 5)], dtype=float)
    c = np.round(a + (b - a) * t).astype(int)
    return "#%02x%02x%02x" % tuple(c)


def seed_palette(n, ramp=SEEDS):
    out = []
    for i in range(n):
        u = 0.0 if n == 1 else (i / (n - 1)) * (len(ramp) - 1)
        j = min(int(np.floor(u)), len(ramp) - 2)
        out.append(hexlerp(ramp[j], ramp[j + 1], u - j))
    return out


def vogel(n, turns, c, center=ORIGIN):
    k = np.arange(n, dtype=float)
    r = c * np.sqrt(k)
    a = TAU * turns * k
    return np.column_stack(
        [center[0] + r * np.cos(a), center[1] + r * np.sin(a), np.zeros(n)]
    )


def residual_turns(step):
    x = step * GOLD_T
    return float(x - np.round(x))


def gap_metric(n, turns, c, samples=52):
    """Largest empty circle in the annulus 0.28R..0.86R, in ideal spacings."""
    pts = vogel(n, turns, c)[:, :2]
    rmax = c * np.sqrt(n - 1)
    g = np.linspace(-rmax, rmax, samples)
    X, Y = np.meshgrid(g, g)
    P = np.column_stack([X.ravel(), Y.ravel()])
    rad = np.linalg.norm(P, axis=1)
    P = P[(rad > 0.28 * rmax) & (rad < 0.86 * rmax)]
    d = np.sqrt(((P[:, None, :] - pts[None, :, :]) ** 2).sum(-1)).min(axis=1)
    return float(d.max() / (c * np.sqrt(PI)))


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
CF_PI = [3, 7, 15, 1, 292, 1, 1]


def quality(pairs, x):
    return [(q, abs(x - p / q) * q * q) for p, q in pairs]


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


def txt(s, size=30, color=INK, maxw=6.3, weight=NORMAL):
    return fit(Text(s, font_size=size, color=color, weight=weight), maxw)


def body(s, size=25, color=INK, maxw=COL_W, width=40):
    return fit(
        Text(wrap(s, width), font_size=size, color=color, line_spacing=0.9), maxw
    )


def tex(s, size=36, color=INK, maxw=COL_W):
    return fit(MathTex(s, font_size=size, color=color), maxw)


# ===================================================================== scene
class TheMostIrrationalNumber(Base):
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
        """Left-aligned column driven by real heights: rows cannot collide."""
        y = top
        for m in mobs:
            m.move_to([left, y, 0.0], aligned_edge=UL)
            y -= m.height + buff
        return VGroup(*mobs)

    def title(self, s):
        return txt(s, 32, INK, 12.6, weight=BOLD).move_to([0, TITLE_Y, 0])

    def metric_row(self, label, value, col, vmax=1.6, w=4.6):
        lab = tex(label, 30, col, w)
        bw = float(np.clip(value / vmax, 0.03, 1.0)) * w
        bg = Rectangle(
            width=w, height=0.13, stroke_width=0, fill_color=EDGE, fill_opacity=1
        )
        bar = Rectangle(
            width=bw, height=0.13, stroke_width=0, fill_color=col, fill_opacity=1
        )
        bar.align_to(bg, LEFT)
        return VGroup(lab, VGroup(bg, bar)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)

    # ------------------------------------------------------------------- hud
    def build_hud(self):
        bg = Rectangle(width=14.4, height=8.2, stroke_width=0)
        bg.set_fill(color=["#0d1218", "#06080a"], opacity=1)
        grain = VGroup(
            *[
                Circle(
                    radius=r, stroke_width=0, fill_color=SEEDS[3], fill_opacity=o
                ).move_to([0, 0.15, 0])
                for r, o in ((5.4, 0.020), (4.0, 0.024), (2.9, 0.028))
            ]
        )
        self.add(bg, grain)

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

        def up(m):
            f = self.prog.get_value()
            m.put_start_and_end_on(
                [RAIL_X0, RAIL_Y, 0], [RAIL_X0 + f * (RAIL_X1 - RAIL_X0), RAIL_Y, 0]
            )

        fill.add_updater(up)
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

    # ------------------------------------------------------------ seed heads
    def head(self, n, turns, c, center=ORIGIN, dot_scale=0.40):
        pts = vogel(n, turns, c, center)
        cols = seed_palette(n)
        dr = dot_scale * c * np.sqrt(PI)
        dots = VGroup(
            *[Dot(pts[i], radius=dr, color=cols[i], stroke_width=0) for i in range(n)]
        )
        return dots, pts

    def reveal_updater(self, dots, tracker):
        def up(g):
            v = tracker.get_value()
            for i, d in enumerate(g):
                d.set_fill(opacity=float(np.clip(v - i, 0.0, 1.0)))

        dots.add_updater(up)

    def place_updater(self, dots, n, turns_tr, c, center):
        k = np.arange(n, dtype=float)
        r = c * np.sqrt(k)

        def up(g):
            a = TAU * turns_tr.get_value() * k
            xs = center[0] + r * np.cos(a)
            ys = center[1] + r * np.sin(a)
            for i, d in enumerate(g):
                d.move_to([xs[i], ys[i], 0.0])

        dots.add_updater(up)

    def freeze(self, dots):
        dots.clear_updaters()
        dots.set_fill(opacity=1.0)

    def family(self, n, step, turns, c, center, color, width=2.0, opacity=0.9):
        pts = vogel(n, turns, c, center)
        fam = VGroup()
        for j in range(step):
            idx = np.arange(j, n, step)
            if len(idx) < 3:
                continue
            curve = VMobject(
                stroke_color=color, stroke_width=width, stroke_opacity=opacity
            )
            curve.set_points_smoothly(pts[idx])
            fam.add(curve)
        return fam

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.build_hud()
        self.act_pattern()
        self.act_recipe()
        self.act_fractions()
        self.act_irrational()
        self.act_fibonacci()
        self.act_payoff()

    # ================================================================== ACT 1
    def act_pattern(self):
        self.chapter(0, run_time=0.8)
        N, R = 610, 2.72
        C = np.array([0.0, 0.10, 0.0])
        c = R / np.sqrt(N - 1)

        dots, _ = self.head(N, GOLD_T, c, C)
        dots.set_fill(opacity=0.0)
        grow = ValueTracker(0.0)
        self.reveal_updater(dots, grow)
        self.add(dots)

        hook = self.title("Every seed here was placed by one line of maths.")

        with self.voiceover(
            "This is a sunflower. Except it isn't. Every seed here was placed by "
            "a single line of mathematics. And when you count the spirals..."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(hook, shift=DOWN * 0.12), run_time=d * 0.22)
            self.play(
                grow.animate.set_value(N),
                run_time=d * 0.70,
                rate_func=rate_functions.ease_out_cubic,
            )
            self.freeze(dots)
            self.rest(tr)

        famA = self.family(N, 34, GOLD_T, c, C, CYAN, 2.1, 0.85)
        famB = self.family(N, 55, GOLD_T, c, C, MAGENTA, 2.1, 0.85)
        nA = Integer(len(famA), font_size=76, color=CYAN).move_to([-5.55, 0.95, 0])
        nB = Integer(len(famB), font_size=76, color=MAGENTA).move_to([5.55, 0.95, 0])
        lA = txt("spirals this way", 22, DIM, 2.6).next_to(nA, DOWN, buff=0.22)
        lB = txt("spirals that way", 22, DIM, 2.6).next_to(nB, DOWN, buff=0.22)

        with self.voiceover(
            "Thirty four curling one way. Fifty five the other. Two neighbours in "
            "the Fibonacci sequence. Make the flower bigger and you get fifty five "
            "and eighty nine. Always neighbours."
        ) as tr:
            d = tr.duration
            self.play(
                dots.animate.set_fill(opacity=0.42),
                LaggedStart(*[Create(s) for s in famA], lag_ratio=0.02),
                run_time=d * 0.30,
            )
            self.play(FadeIn(nA, scale=0.7), FadeIn(lA), run_time=d * 0.12)
            self.play(
                LaggedStart(*[Create(s) for s in famB], lag_ratio=0.02),
                run_time=d * 0.32,
            )
            self.play(FadeIn(nB, scale=0.7), FadeIn(lB), run_time=d * 0.12)
            self.rest(tr)

        fib = tex(
            r"1,\;1,\;2,\;3,\;5,\;8,\;13,\;21,\;34,\;55,\;89", 36, GOLD, 8.4
        ).move_to([0, -3.20, 0])
        with self.voiceover(
            "Nature is counting in Fibonacci. And there is a reason. It comes down "
            "to the one number that is hardest to turn into a fraction."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(fib, shift=UP * 0.12), run_time=d * 0.35)
            self.play(
                Indicate(nA, color=CYAN, scale_factor=1.25),
                Indicate(nB, color=MAGENTA, scale_factor=1.25),
                run_time=d * 0.35,
            )
            self.rest(tr)

        self.play(
            FadeOut(VGroup(dots, famA, famB, nA, nB, lA, lB, fib, hook)), run_time=0.9
        )

    # ================================================================== ACT 2
    def act_recipe(self):
        self.chapter(1)
        N, R = 320, 2.40
        C = np.array([-3.45, -0.10, 0.0])
        c = R / np.sqrt(N - 1)

        turns = ValueTracker(0.25)
        dots, _ = self.head(N, turns.get_value(), c, C)
        self.place_updater(dots, N, turns, c, C)
        ring = Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(C)
        self.add(ring, dots)

        rule = tex(
            r"\theta_k = 360^{\circ}\,k\,t,\qquad r_k = c\sqrt{k}", 34, GOLD, COL_W
        )
        why = body("Square-root spacing gives every seed the same amount of room.")
        self.stack([rule, why], top=COL_TOP)

        # divergence-angle protractor: reference ray + one turn of size t
        panel = RoundedRectangle(
            corner_radius=0.14,
            width=4.0,
            height=1.30,
            stroke_color=EDGE,
            stroke_width=1.6,
            fill_color=SURFACE,
            fill_opacity=0.95,
        )
        panel.move_to([3.60, 0.30, 0])
        plab = txt("angle between consecutive seeds", 19, DIM, 3.6)
        plab.move_to([3.60, 0.78, 0])
        O = np.array([2.35, 0.12, 0.0])
        ray0 = Line(O, O + RIGHT * 0.52, stroke_color=DIM, stroke_width=3)
        ray1 = Line(O, O + RIGHT * 0.52, stroke_color=GOLD, stroke_width=3)

        def ray_up(m):
            a = TAU * turns.get_value()
            m.put_start_and_end_on(O, O + 0.52 * np.array([np.cos(a), np.sin(a), 0]))

        ray1.add_updater(ray_up)
        pivot = Dot(O, radius=0.05, color=GOLD)

        ang = DecimalNumber(90.0, num_decimal_places=2, font_size=44, color=GOLD)
        ang.move_to([4.05, 0.12, 0])
        deg = tex(r"^{\circ}", 32, GOLD, 0.5).move_to([5.05, 0.30, 0])
        shown = [None]

        def ang_up(m):
            v = round(360.0 * turns.get_value(), 2)
            if shown[0] != v:
                m.set_value(v)
                shown[0] = v
            m.move_to([4.05, 0.12, 0])

        ang.add_updater(ang_up)
        ang.update(0)

        with self.voiceover(
            "Here is the whole recipe. Start at the centre. Turn by a fixed angle, "
            "step outward a little, plant a seed. Then do it again. And again. "
            "The step size is easy: outward as the square root of the seed number, "
            "which gives every seed the same amount of room. The angle is the "
            "interesting part."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(ring), Write(rule), run_time=d * 0.24)
            self.play(FadeIn(why), run_time=d * 0.16)
            self.play(
                FadeIn(panel),
                FadeIn(plab),
                FadeIn(ray0),
                FadeIn(pivot),
                FadeIn(ray1),
                FadeIn(deg),
                run_time=d * 0.20,
            )
            ang.update(0)
            self.play(FadeIn(ang), run_time=0.4)
            self.rest(tr)

        bad1 = body("Quarter turn: four spokes, and a flower full of holes.", color=RED)
        bad2 = body("A third of a turn: three spokes.", color=RED)
        good = body("137.51 degrees: the gaps vanish.", color=ACID)
        self.stack([bad1, bad2, good], top=-0.62, buff=0.26)

        with self.voiceover(
            "Watch what happens as I sweep it. Quarter turn: four spokes, and a "
            "flower full of holes. A third of a turn: three spokes. But land on one "
            "hundred thirty seven point five degrees, and the gaps just vanish."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(bad1), run_time=d * 0.12)
            self.play(
                turns.animate.set_value(1 / 3), run_time=d * 0.20, rate_func=smooth
            )
            self.play(FadeIn(bad2), run_time=d * 0.10)
            self.play(
                turns.animate.set_value(0.30), run_time=d * 0.14, rate_func=smooth
            )
            self.play(
                turns.animate.set_value(GOLD_T), run_time=d * 0.30, rate_func=smooth
            )
            self.play(
                FadeIn(good),
                Flash(
                    dots, color=ACID, line_length=0.3, num_lines=18, flash_radius=2.6
                ),
                run_time=max(0.9, d * 0.14),
            )
            self.rest(tr)

        self.freeze(dots)
        ray1.clear_updaters()
        ang.update(0)
        self.play(
            FadeOut(
                VGroup(
                    ring,
                    dots,
                    rule,
                    why,
                    panel,
                    plab,
                    ray0,
                    ray1,
                    pivot,
                    ang,
                    deg,
                    bad1,
                    bad2,
                    good,
                )
            ),
            run_time=0.8,
        )

    # ================================================================== ACT 3
    def act_fractions(self):
        self.chapter(2)
        title = self.title("Any fraction eventually lines up.")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)

        specs = [(1, 4, RED), (5, 13, "#ff8a3d"), (13, 34, GOLD), (None, None, ACID)]
        n, R = 180, 1.10
        c = R / np.sqrt(n - 1)
        xs = [-5.20, -1.75, 1.75, 5.20]
        cards = VGroup()

        for (p, q, col), x in zip(specs, xs):
            t = GOLD_T if p is None else p / q
            g = gap_metric(n, t, c)
            C = np.array([x, 1.00, 0.0])
            dots, _ = self.head(n, t, c, C)
            ring = Circle(radius=R, stroke_color=EDGE, stroke_width=1.6).move_to(C)
            label = (
                tex(r"t = \tfrac{1}{\varphi^{2}}", 30, col, 2.6)
                if p is None
                else tex(rf"t = \tfrac{{{p}}}{{{q}}}", 30, col, 2.6)
            )
            label.move_to([x, 2.52, 0])
            rays = (
                tex(r"\infty", 28, col, 1.6)
                if p is None
                else tex(rf"{q}\ \mathrm{{rays}}", 26, col, 2.6)
            )
            rays.move_to([x, -0.48, 0])
            w = float(np.clip(g / 5.5, 0.04, 1.0)) * 2.3
            bar_bg = Rectangle(
                width=2.3, height=0.13, stroke_width=0, fill_color=EDGE, fill_opacity=1
            ).move_to([x, -0.92, 0])
            bar = Rectangle(
                width=w, height=0.13, stroke_width=0, fill_color=col, fill_opacity=1
            )
            bar.move_to([x - 1.15 + w / 2, -0.92, 0])
            val = tex(rf"{g:.2f}", 25, col, 1.6).move_to([x, -1.26, 0])
            cards.add(VGroup(ring, dots, label, rays, bar_bg, bar, val))

        cap = txt(
            "bar = biggest empty gap, in units of the ideal seed spacing", 22, DIM, 9.6
        ).move_to([0, -1.82, 0])

        with self.voiceover(
            "So why do fractions ruin it? If your angle is p over q of a full turn, "
            "then after q seeds you are pointing exactly where you started. Every "
            "seed after that lands on one of those same q rays. Forever. And it does "
            "not help to pick a clever fraction. Five thirteenths gives thirteen "
            "spokes. Thirteen over thirty four looks almost perfect."
        ) as tr:
            d = tr.duration
            for card in cards:
                self.play(FadeIn(card, shift=UP * 0.12), run_time=max(0.5, d * 0.21))
            self.play(FadeIn(cap), run_time=max(0.5, d * 0.16))
            self.rest(tr)

        # grow the near-miss rational until its spokes betray it
        Ng, Rg = 610, 2.30
        Cg = np.array([-3.45, -0.20, 0.0])
        cg = Rg / np.sqrt(Ng - 1)
        dots_g, _ = self.head(Ng, 13 / 34, cg, Cg)
        dots_g.set_fill(opacity=0.0)
        grow = ValueTracker(60.0)
        self.reveal_updater(dots_g, grow)
        ring_g = Circle(radius=Rg, stroke_color=EDGE, stroke_width=2).move_to(Cg)

        t1 = tex(r"t = \tfrac{13}{34} = 0.382353\ldots", 32, GOLD, COL_W)
        t2 = tex(r"t = \tfrac{1}{\varphi^{2}} = 0.381966\ldots", 32, ACID, COL_W)
        t3 = body("Close enough to fool a small flower.")
        self.stack([t1, t2, t3], top=COL_TOP, buff=0.34)

        t4 = body(
            "Keep growing and thirty-four spokes creep out. "
            "Every fraction betrays you eventually.",
            color=RED,
        )
        self.stack([t4], top=0.55)
        t5 = body(
            "So nature wants the number that stays farthest from every "
            "fraction there is.",
            color=GOLD,
        )
        self.stack([t5], top=-0.85)

        with self.voiceover(
            "But keep growing, and the spokes creep out. Any fraction betrays you "
            "eventually. Which means nature wants a number that stays as far away "
            "from every fraction as it possibly can."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(cards), FadeOut(cap), FadeOut(title), run_time=d * 0.14)
            self.play(FadeIn(ring_g), FadeIn(t1), FadeIn(t2), run_time=d * 0.16)
            self.add(dots_g)
            self.play(
                FadeIn(t3),
                grow.animate.set_value(200),
                run_time=d * 0.20,
                rate_func=linear,
            )
            self.play(
                FadeIn(t4),
                grow.animate.set_value(Ng),
                run_time=d * 0.32,
                rate_func=linear,
            )
            self.freeze(dots_g)
            self.play(FadeIn(t5), run_time=max(0.7, d * 0.18))
            self.rest(tr)

        self.play(FadeOut(VGroup(dots_g, ring_g, t1, t2, t3, t4, t5)), run_time=0.8)

    # ================================================================== ACT 4
    def act_irrational(self):
        self.chapter(3)

        # ---- exact golden-rectangle subdivision + tangent-continuous spiral
        s = 2.25
        ox, oy = -3.55, 0.05
        map_pt = lambda p: np.array(
            [ox + (p[0] - PHI / 2) * s, oy + (p[1] - 0.5) * s, 0.0]
        )
        outer = Rectangle(
            width=PHI * s,
            height=s,
            stroke_color=GOLD,
            stroke_width=2.4,
            stroke_opacity=0.9,
        )
        outer.move_to(map_pt([PHI / 2, 0.5]))

        centre = np.array([1.0, 1.0])
        squares, arcs = VGroup(), VGroup()
        quad = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        for i in range(10):
            r = PHI ** (-i)
            sx, sy = quad[i % 4]
            corner = centre + np.array([sx * r, sy * r])
            lo = np.minimum(centre, corner)
            col = SEEDS[(i + 1) % len(SEEDS)]
            sq = Rectangle(
                width=r * s,
                height=r * s,
                stroke_color=col,
                stroke_width=1.6,
                stroke_opacity=0.85,
                fill_color=col,
                fill_opacity=0.13,
            )
            sq.move_to(map_pt(lo + np.array([r / 2, r / 2])))
            squares.add(sq)
            a0 = PI + i * PI / 2
            arcs.add(
                Arc(
                    radius=r * s,
                    start_angle=a0,
                    angle=PI / 2,
                    arc_center=map_pt(centre),
                    stroke_color=GOLD,
                    stroke_width=3.2,
                )
            )
            end = centre + r * np.array([np.cos(a0 + PI / 2), np.sin(a0 + PI / 2)])
            centre = centre + (r - PHI ** (-(i + 1))) * (end - centre) / r

        rest_rect = Rectangle(
            width=(PHI - 1) * s,
            height=s,
            stroke_color=CYAN,
            stroke_width=3,
            stroke_opacity=0.95,
        )
        rest_rect.move_to(map_pt([1 + (PHI - 1) / 2, 0.5]))

        # ---- phase A
        headA = tex(r"\varphi = 1.6180339887\ldots", 34, GOLD, COL_W)
        eqA = tex(r"\varphi = 1 + \frac{1}{\varphi}", 42, INK, COL_W)
        noteA = body(
            "Cut a square. The leftover is the same shape, turned and smaller.",
            color=DIM,
        )
        self.stack([headA, eqA, noteA], top=COL_TOP, buff=0.36)

        with self.voiceover(
            "Meet phi. One point six one eight. The golden ratio. Take a rectangle "
            "with sides in that ratio, slice off a square, and the piece left over "
            "is the same shape again, just smaller and turned. Do it forever and "
            "you get this spiral. That self similarity is an equation: phi equals "
            "one plus one over phi."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(headA), Create(outer), run_time=d * 0.18)
            self.play(FadeIn(squares[0]), Create(arcs[0]), run_time=d * 0.16)
            self.play(Create(rest_rect), FadeIn(noteA), run_time=d * 0.14)
            self.play(
                LaggedStart(*[FadeIn(q) for q in squares[1:]], lag_ratio=0.12),
                LaggedStart(*[Create(a) for a in arcs[1:]], lag_ratio=0.12),
                run_time=d * 0.30,
            )
            self.play(FadeOut(rest_rect), Write(eqA), run_time=d * 0.22)
            self.rest(tr)

        # ---- phase B (panel A is cleared first: no stacked leftovers)
        cf = tex(
            r"\varphi = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}}",
            40,
            INK,
            3.4,
        ).move_to([-3.55, 0.10, 0])
        cf_bg = BackgroundRectangle(cf, color=BG, buff=0.24, fill_opacity=0.9)

        ones = body("All ones. The worst possible ingredient.", color=GOLD)
        gift = body("A big entry is a gift: a suspiciously good approximation.")
        pi_cf = tex(r"\pi = [3;\,7,\,15,\,1,\,\mathbf{292},\ldots]", 32, MAGENTA, COL_W)
        pi_best = tex(r"\tfrac{355}{113} = 3.14159292\ldots", 32, MAGENTA, COL_W)
        pi_note = body(
            "Six correct decimals from a three digit denominator.", size=23, color=DIM
        )
        self.stack([ones, gift, pi_cf, pi_best, pi_note], top=COL_TOP, buff=0.32)

        with self.voiceover(
            "Feed it back into itself and phi becomes a continued fraction made "
            "entirely of ones. And ones are the worst possible ingredient. Every "
            "big number in a continued fraction is a gift, a suspiciously good "
            "approximation. Pi has a two hundred ninety two, which hands you three "
            "hundred fifty five over one hundred thirteen. Six correct decimals "
            "from a three digit denominator."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(VGroup(outer, squares, arcs, headA, eqA, noteA)),
                run_time=d * 0.14,
            )
            self.play(FadeIn(cf_bg), Write(cf), FadeIn(ones), run_time=d * 0.26)
            self.play(FadeIn(gift), run_time=d * 0.12)
            self.play(Write(pi_cf), run_time=d * 0.18)
            self.play(
                FadeIn(pi_best, shift=UP * 0.1), FadeIn(pi_note), run_time=d * 0.20
            )
            self.rest(tr)

        # ---- phase C
        fibs = tex(
            r"\tfrac{1}{1},\tfrac{2}{1},\tfrac{3}{2},\tfrac{5}{3},"
            r"\tfrac{8}{5},\tfrac{13}{8},\tfrac{21}{13},\tfrac{34}{21},"
            r"\tfrac{55}{34}",
            32,
            GOLD,
            COL_W,
        )
        fib_note = body(
            "Phi's best attempts are Fibonacci over Fibonacci. And they crawl."
        )
        self.stack([fibs, fib_note], top=COL_TOP, buff=0.36)

        with self.voiceover(
            "Phi has no gifts. Its best approximations are ratios of consecutive "
            "Fibonacci numbers, and they crawl."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(VGroup(ones, gift, pi_cf, pi_best, pi_note)), run_time=d * 0.25
            )
            self.play(FadeIn(fibs, shift=UP * 0.1), FadeIn(fib_note), run_time=d * 0.55)
            self.rest(tr)

        # ---- phase D: the scoreboard, |x - p/q| q^2 against log10(q)
        LX = float(np.log10(230))
        ax = Axes(
            x_range=[0, LX, 1],
            y_range=[0, 1.0, 0.2],
            x_length=6.0,
            y_length=2.70,
            tips=False,
            axis_config={
                "stroke_color": EDGE,
                "stroke_width": 2,
                "tick_size": 0.05,
                "include_numbers": False,
            },
        ).move_to([3.45, -0.80, 0])
        P = lambda q, v: ax.c2p(float(np.log10(q)), v)

        ceil = DashedLine(
            P(1, HURWITZ),
            P(230, HURWITZ),
            color=GOLD,
            stroke_width=2,
            stroke_opacity=0.75,
            dash_length=0.09,
        )
        ceil_lab = tex(r"\tfrac{1}{\sqrt{5}}", 26, GOLD, 0.8).next_to(
            ceil, LEFT, buff=0.12
        )

        series = [
            (quality(convergents(CF_PHI, 10)[2:], PHI), GOLD, r"\varphi"),
            (quality(convergents(CF_SQ2, 6)[1:], np.sqrt(2)), CYAN, r"\sqrt{2}"),
            (quality(convergents(CF_PI, 4), PI), MAGENTA, r"\pi"),
        ]
        plots, labels, markers = VGroup(), VGroup(), VGroup()
        for data, col, name in series:
            pts = [P(q, v) for q, v in data]
            seg = VGroup(
                *[
                    Line(
                        pts[i],
                        pts[i + 1],
                        stroke_color=col,
                        stroke_width=2.6,
                        stroke_opacity=0.9,
                    )
                    for i in range(len(pts) - 1)
                ]
            )
            dd = VGroup(*[Dot(p, radius=0.045, color=col) for p in pts])
            plots.add(VGroup(seg, dd))
            markers.add(dd)
            labels.add(tex(name, 30, col, 0.8).next_to(pts[-1], UR, buff=0.10))

        xlabels = VGroup(
            *[
                txt(s, 20, DIM, 0.8).next_to(P(q, 0), DOWN, buff=0.14)
                for q, s in ((1, "1"), (10, "10"), (100, "100"))
            ]
        )
        ylab = tex(r"\left|x - \tfrac{p}{q}\right| \cdot q^{2}", 26, DIM, 2.4)
        ylab.next_to(ax, UP, buff=0.14).align_to(ax, LEFT)
        xlab = txt("denominator q", 20, DIM, 2.4).next_to(ax, DOWN, buff=0.32)
        verdict = body(
            "Phi never dips. It sits on the ceiling forever.", color=GOLD
        ).move_to([3.45, -3.20, 0])

        with self.voiceover(
            "Here is the scoreboard. Error times denominator squared. Root two "
            "settles here. Pi dives. Phi just sits on the ceiling, one over root "
            "five. Hurwitz proved every irrational gets infinitely many "
            "approximations under that line, and phi is the reason the line cannot "
            "be raised. It is, provably, the most irrational number."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(VGroup(cf, cf_bg, fibs, fib_note)), run_time=d * 0.10)
            self.play(
                Create(ax),
                FadeIn(xlabels),
                FadeIn(ylab),
                FadeIn(xlab),
                run_time=d * 0.12,
            )
            self.play(Create(ceil), FadeIn(ceil_lab), run_time=d * 0.10)
            self.play(Create(plots[1]), FadeIn(labels[1]), run_time=d * 0.13)
            self.play(Create(plots[2]), FadeIn(labels[2]), run_time=d * 0.15)
            self.play(Create(plots[0]), FadeIn(labels[0]), run_time=d * 0.15)
            self.play(
                FadeIn(verdict),
                Indicate(markers[0][-1], color=GOLD, scale_factor=1.8),
                run_time=d * 0.15,
            )
            self.rest(tr)

        self.play(
            FadeOut(
                VGroup(ax, xlabels, ylab, xlab, ceil, ceil_lab, plots, labels, verdict)
            ),
            run_time=0.9,
        )

    # ================================================================== ACT 5
    def act_fibonacci(self):
        self.chapter(4)
        N, R = 610, 2.35
        C = np.array([-3.45, -0.15, 0.0])
        c = R / np.sqrt(N - 1)
        dots, pts = self.head(N, GOLD_T, c, C)
        dots.set_fill(opacity=0.30)
        ring = Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(C)

        r34, r55 = residual_turns(34), residual_turns(55)
        e1 = tex(rf"34\,t = {34 * GOLD_T:.6f}\ \mathrm{{turns}}", 30, CYAN, COL_W)
        e1b = tex(rf"\mathrm{{offset}} = {r34 * 360:+.3f}^{{\circ}}", 30, CYAN, COL_W)
        n1 = body("Almost a whole number of turns. Almost is the whole point.")
        self.stack([e1, e1b, n1], top=COL_TOP, buff=0.30)

        with self.voiceover(
            "Now watch the two ideas collide. The golden angle is one over phi "
            "squared of a turn. Multiply it by thirty four and you get thirteen "
            "full turns, minus four point seven degrees. So seed thirty four sits "
            "almost on top of seed zero's direction."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(ring), FadeIn(dots), run_time=d * 0.18)
            self.play(Write(e1), run_time=d * 0.26)
            self.play(Write(e1b), run_time=d * 0.22)
            self.play(FadeIn(n1), run_time=d * 0.22)
            self.rest(tr)

        idx = np.arange(0, N, 34)
        chain = VGroup(*[Dot(pts[i], radius=0.085, color=CYAN) for i in idx])
        one = VMobject(stroke_color=CYAN, stroke_width=3.4)
        one.set_points_smoothly(pts[idx])
        mod = tex(r"k \equiv 0 \pmod{34}", 30, CYAN, COL_W)
        n2 = body("Join them and you trace one spiral.")
        self.stack([mod, n2], top=0.62, buff=0.28)

        with self.voiceover(
            "Join them, and the next, and the next, and you trace one spiral."
        ) as tr:
            d = tr.duration
            self.play(
                LaggedStart(*[GrowFromCenter(p) for p in chain], lag_ratio=0.10),
                run_time=d * 0.55,
            )
            self.play(Create(one), FadeIn(mod), FadeIn(n2), run_time=d * 0.45)
            self.rest(tr)

        famA = self.family(N, 34, GOLD_T, c, C, CYAN, 1.9, 0.8)
        famB = self.family(N, 55, GOLD_T, c, C, MAGENTA, 1.9, 0.8)
        why = body(
            "Seeds 34 apart share a remainder mod 34, so the family has "
            "exactly 34 members.",
            size=23,
            color=DIM,
        )
        cntA = tex(rf"{len(famA)}\ \mathrm{{spirals}}", 32, CYAN, COL_W)
        e2 = tex(rf"55\,t = {55 * GOLD_T:.6f}\ \mathrm{{turns}}", 30, MAGENTA, COL_W)
        e2b = tex(
            rf"\mathrm{{offset}} = {r55 * 360:+.3f}^{{\circ}}", 30, MAGENTA, COL_W
        )
        cntB = tex(rf"{len(famB)}\ \mathrm{{spirals}}", 32, MAGENTA, COL_W)
        self.stack([why, cntA, e2, e2b, cntB], top=0.62, buff=0.26)

        with self.voiceover(
            "Step by fifty five instead and you overshoot by two point nine "
            "degrees, so that family curls the other way. And how many spirals are "
            "in a family? Exactly the step size, because seeds thirty four apart "
            "share a remainder mod thirty four. Thirty four spirals. Fifty five "
            "spirals. The flower was never counting. It was just refusing to line up."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(VGroup(mod, n2, one, chain)), FadeIn(why), run_time=d * 0.14
            )
            self.play(
                LaggedStart(*[Create(s) for s in famA], lag_ratio=0.02),
                run_time=d * 0.24,
            )
            self.play(FadeIn(cntA), run_time=d * 0.08)
            self.play(
                LaggedStart(*[Create(s) for s in famB], lag_ratio=0.02),
                run_time=d * 0.24,
            )
            self.play(FadeIn(e2), FadeIn(e2b), FadeIn(cntB), run_time=d * 0.18)
            self.rest(tr)

        self.play(
            FadeOut(
                VGroup(dots, ring, famA, famB, e1, e1b, n1, why, cntA, e2, e2b, cntB)
            ),
            run_time=0.9,
        )

    # ================================================================== ACT 6
    def act_payoff(self):
        self.chapter(5)
        N, R = 610, 2.50
        C = np.array([-3.30, 0.00, 0.0])
        c = R / np.sqrt(N - 1)
        turns = ValueTracker(13 / 34)
        dots, _ = self.head(N, turns.get_value(), c, C)
        self.place_updater(dots, N, turns, c, C)
        ring = Circle(radius=R, stroke_color=EDGE, stroke_width=2).move_to(C)
        self.add(ring, dots)

        g0 = gap_metric(N, 13 / 34, c)
        g1 = gap_metric(N, GOLD_T, c)
        vmax = max(g0, g1) * 1.15

        head = body(
            "Impossible to approximate = never leaves a gap.", size=28, color=GOLD
        )
        row0 = self.metric_row(rf"t=\tfrac{{13}}{{34}}:\quad {g0:.2f}", g0, RED, vmax)
        row1 = self.metric_row(
            rf"t=\tfrac{{1}}{{\varphi^{{2}}}}:\quad {g1:.2f}", g1, ACID, vmax
        )
        sub = body("biggest empty gap, same seed count", size=22, color=DIM)
        self.stack([head, row0, row1, sub], top=COL_TOP, buff=0.30)

        punch = body(
            "Sunflowers, pinecones and pineapples all quietly agree on one angle."
        )
        self.stack([punch], top=-0.90)
        last = body(
            "Not beauty. Not coincidence. Just the number that fractions cannot catch.",
            color=GOLD,
        )
        self.stack([last], top=-2.00)

        with self.voiceover(
            "That is the trick. Being impossible to approximate is the same as "
            "never leaving a gap. The most irrational number is the best packer. "
            "Which is why sunflowers, pinecones and pineapples all quietly agree on "
            "one hundred thirty seven point five degrees."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(head), FadeIn(row0), FadeIn(sub), run_time=d * 0.22)
            self.play(
                turns.animate.set_value(GOLD_T), run_time=d * 0.42, rate_func=smooth
            )
            self.play(
                FadeIn(row1),
                Flash(
                    dots, color=ACID, line_length=0.3, num_lines=18, flash_radius=2.7
                ),
                run_time=d * 0.16,
            )
            self.play(FadeIn(punch), run_time=d * 0.20)
            self.rest(tr)

        self.freeze(dots)
        with self.voiceover(
            "Not beauty. Not coincidence. Just the number that fractions cannot catch."
        ) as tr:
            self.play(FadeIn(last), run_time=min(1.4, tr.duration * 0.6))
            self.rest(tr)

        card_phi = tex(
            r"\varphi = \frac{1+\sqrt{5}}{2} = 1.6180339887\ldots", 36, GOLD, 7.0
        ).move_to([0, 1.15, 0])
        card_ang = tex(
            r"360^{\circ}/\varphi^{2} = 137.5077640^{\circ}", 36, CYAN, 7.0
        ).move_to([0, 0.20, 0])
        card_lim = tex(
            r"\lim_{n\to\infty}\frac{F_{n+1}}{F_n} = \varphi", 32, DIM, 7.0
        ).move_to([0, -0.85, 0])
        tag = txt("THE MOST IRRATIONAL NUMBER", 30, INK, 8.0, weight=BOLD).move_to(
            [0, -2.15, 0]
        )
        tag.set_color_by_gradient(GOLD, MAGENTA, CYAN)

        self.play(
            FadeOut(VGroup(dots, ring, head, row0, row1, sub, punch, last)),
            run_time=0.9,
        )
        self.play(Write(card_phi), run_time=1.3)
        self.play(Write(card_ang), run_time=1.3)
        self.play(FadeIn(card_lim), FadeIn(tag, shift=UP * 0.15), run_time=1.2)
        self.wait(2.0)
        self.play(self.prog.animate.set_value(1.0), run_time=1.0)
        self.rail_fill.clear_updaters()
        self.play(
            FadeOut(VGroup(card_phi, card_ang, card_lim, tag, self._chap)), run_time=1.4
        )
        self.wait(0.5)
