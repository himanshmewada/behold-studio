"""
THE SQUARE THAT BREAKS A FRACTION  ·  YouTube Short  ·  1080x1920  ·  ~58 s
==========================================================================
Tennenbaum's geometric proof that sqrt(2) is irrational, by infinite descent.

THE MATHEMATICS (exact, and every animation is the proof itself)
---------------------------------------------------------------
Assume sqrt(2) = a/b with a the smallest possible positive integer.
    a^2 = 2 b^2                     -> b = a/sqrt(2), and b < a < 2b
Place two b-squares in opposite corners of an a-square:
    overlap  = square of side 2b - a, centred
    uncovered = two squares of side a - b, at the other two corners
The two b-squares have total area a^2, so double-counting must cancel gaps:
    (2b - a)^2 = 2 (a - b)^2
Same equation, smaller positive integers. Descent forever -> contradiction.

The descent is drawn as a PURE TRANSLATION, never a fudge:
    new a-square  := the overlap      (side 2b-a, already centred)
    new b-squares := the two gaps     (side a-b, exactly the right size)
    they slide into the opposite corners of the new a-square.
Shrink factor per level = sqrt(2) - 1 = 0.41421356...

act_assume / RENDER
--------------
    pip install manim "manim-voiceover[gtts]"
    manim -p vid5.py TheSquareThatBreaksAFraction
    PREVIEW = True -> 540x960 draft      FPS = 60 -> smoother, slower render

MANIM 0.22 RULES OBEYED
-----------------------
    * no set_width/set_height kwargs -> .scale()
    * no set_height(stretch=...)
    * one .animate chain per mobject per play()
    * counters are static Integers swapped by ReplacementTransform, so no
      DecimalNumber family can change size mid-fade
    * updaters cleared before any FadeOut
    * text rows placed by stack() from real heights; long copy is wrapped
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
# ink-violet night; blue = the a-square, amber = the b-squares,
# magenta = counted twice, cyan = missed, acid = the verdict
BG      = "#07070f"
SURFACE = "#141426"
EDGE    = "#2a2a45"
INK     = "#f1eff9"
DIM     = "#8f8bad"
BLUE    = "#4d7cff"
GOLD    = "#ffb020"
MAGENTA = "#ff2d95"
CYAN    = "#00e5d0"
ACID    = "#b6ff3d"
RED     = "#ff4d4d"
LEVELS  = ["#4d7cff", "#00e5d0", "#b6ff3d", "#ffb020", "#ff2d95", "#a06bff"]

# --------------------------------------------------------------- layout grid
TOP_TOP = 7.05          # top text column cursor
BOT_TOP = -2.55         # bottom text column cursor
COL_W   = 8.20
SQ_A    = 5.00          # screen side of the a-square
SQ_C    = np.array([0.0, 0.60, 0.0])
SHRINK  = np.sqrt(2.0) - 1.0


# -------------------------------------------------------------- text helpers
def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def wrap(s, width=32):
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


def txt(s, size=44, color=INK, maxw=COL_W, weight=NORMAL):
    return fit(Text(s, font_size=size, color=color, weight=weight), maxw)


def body(s, size=38, color=INK, maxw=COL_W, width=32):
    return fit(Text(wrap(s, width), font_size=size, color=color,
                    line_spacing=0.85), maxw)


def tex(s, size=52, color=INK, maxw=COL_W):
    return fit(MathTex(s, font_size=size, color=color), maxw)


# ===================================================================== scene
class TheSquareThatBreaksAFraction(Base):
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

    def stack(self, mobs, top, buff=0.30):
        """Centre-aligned column driven by real heights: rows cannot collide."""
        y = top
        for m in mobs:
            m.move_to([0.0, y, 0.0], aligned_edge=UP)
            y -= m.height + buff
        return VGroup(*mobs)

    def swatch_row(self, color, label, value):
        sw = Square(side_length=0.30, fill_color=color, fill_opacity=1,
                    stroke_width=0)
        lab = txt(label, 32, DIM, 4.6)
        val = tex(value, 40, color, 3.2)
        return VGroup(sw, lab, val).arrange(RIGHT, buff=0.26)

    # -------------------------------------------------------------- geometry
    def geo(self, A, C):
        """Exact corner placement for side A, centre C."""
        B = A / np.sqrt(2.0)
        d = (A - B) / 2.0
        return {
            "A": A, "B": B, "C": np.array(C, dtype=float),
            "s1": C + np.array([-d, d, 0.0]),      # top-left b-square
            "s2": C + np.array([d, -d, 0.0]),      # bottom-right b-square
            "ov": 2.0 * B - A,                     # overlap side
            "gap": A - B,                          # uncovered side
            "gTR": C + np.array([B / 2, B / 2, 0.0]),
            "gBL": C - np.array([B / 2, B / 2, 0.0]),
        }

    def big_square(self, g, color):
        return Square(side_length=g["A"], stroke_color=color, stroke_width=4,
                      fill_color=color, fill_opacity=0.07).move_to(g["C"])

    def small_square(self, g, which, color=GOLD):
        return Square(side_length=g["B"], stroke_color=color, stroke_width=3,
                      fill_color=color, fill_opacity=0.20).move_to(g[which])

    def highlights(self, g):
        ov = Square(side_length=g["ov"], stroke_color=MAGENTA, stroke_width=3,
                    fill_color=MAGENTA, fill_opacity=0.42).move_to(g["C"])
        gTR = Square(side_length=g["gap"], stroke_color=CYAN, stroke_width=3,
                     fill_color=CYAN, fill_opacity=0.34).move_to(g["gTR"])
        gBL = Square(side_length=g["gap"], stroke_color=CYAN, stroke_width=3,
                     fill_color=CYAN, fill_opacity=0.34).move_to(g["gBL"])
        return ov, gTR, gBL

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.act_stage()
        self.act_hook()
        self.act_assume()
        self.act_balance()
        self.act_equation()
        self.act_descent()
        self.act_verdict()

    # ----------------------------------------------------------------- act_stage
    def act_stage(self):
        bg = Rectangle(width=9.4, height=16.4, stroke_width=0)
        bg.set_fill(color=["#101024", "#05050c"], opacity=1)
        self.add(bg)

        # integer-lattice texture: the whole proof is about whole numbers
        lattice = VGroup()
        for i in range(-9, 10):
            for j in range(-16, 17):
                p = np.array([i * 0.5, j * 0.5, 0.0])
                if abs(p[0]) < 4.6 and abs(p[1]) < 8.1:
                    lattice.add(Dot(p, radius=0.017, color=DIM,
                                    fill_opacity=0.16))
        self.add(lattice)

        halo = VGroup(*[
            Square(side_length=s, stroke_width=0, fill_color=BLUE,
                   fill_opacity=o).move_to(SQ_C)
            for s, o in ((8.4, 0.030), (6.8, 0.036), (5.6, 0.040))
        ])
        self.add(halo)
        self.halo = halo

    # ------------------------------------------------------------------ act_hook
    def act_hook(self):
        g = self.geo(SQ_A, SQ_C)
        self.g = g

        digits = tex(r"\sqrt{2} = 1.41421356237\ldots", 54, INK, COL_W)
        question = txt("Can this be a fraction?", 50, GOLD, COL_W, weight=BOLD)
        self.stack([digits, question], top=TOP_TOP, buff=0.42)

        ghost = Square(side_length=SQ_A, stroke_color=BLUE, stroke_width=3,
                       stroke_opacity=0.55, fill_opacity=0).move_to(SQ_C)

        with self.voiceover(
            "Can root two be written as a fraction? "
            "This one picture proves it can't."
        ) as tr:
            d = tr.duration
            self.play(Write(digits), run_time=d * 0.40)
            self.play(FadeIn(question, shift=UP * 0.15), run_time=d * 0.28)
            self.play(Create(ghost), run_time=d * 0.32)
            self.rest(tr)

        self.hook_group = VGroup(digits, question)
        self.ghost_intro = ghost

    # ----------------------------------------------------------------- act_assume
    def act_assume(self):
        g = self.g
        title = tex(r"\sqrt{2} = \frac{a}{b}", 60, INK, 4.0)
        sub = body("with a the smallest whole number possible.",
                   size=34, color=DIM)
        eq = tex(r"a^{2} = 2\,b^{2}", 56, GOLD, COL_W)
        self.stack([title, sub, eq], top=TOP_TOP, buff=0.34)
        self.top_setup = VGroup(title, sub, eq)

        big = self.big_square(g, BLUE)
        a_lab = tex(r"a", 46, BLUE, 0.7).next_to(big, LEFT, buff=0.22)
        area = tex(r"a^{2}", 52, BLUE, 1.6).move_to(g["C"])

        s1 = self.small_square(g, "s1")
        s2 = self.small_square(g, "s2")
        s1.shift(LEFT * 7.0)
        s2.shift(RIGHT * 7.0)
        l1 = tex(r"b^{2}", 44, GOLD, 1.2).move_to(
            g["C"] + np.array([-SQ_A / 2 + 0.62, SQ_A / 2 - 0.62, 0]))
        l2 = tex(r"b^{2}", 44, GOLD, 1.2).move_to(
            g["C"] + np.array([SQ_A / 2 - 0.62, -SQ_A / 2 + 0.62, 0]))

        with self.voiceover(
            "Suppose it could. Root two equals a over b, with a as small as "
            "possible. Rearranged: a squared equals two b squared. One square "
            "of side a, same area as two squares of side b."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.hook_group),
                      ReplacementTransform(self.ghost_intro, big),
                      run_time=d * 0.16)
            self.play(FadeIn(a_lab), FadeIn(area), Write(title), run_time=d * 0.18)
            self.play(FadeIn(sub), run_time=d * 0.12)
            self.play(Write(eq), run_time=d * 0.16)
            self.play(FadeOut(area),
                      s1.animate.move_to(g["s1"]),
                      s2.animate.move_to(g["s2"]),
                      run_time=d * 0.26, rate_func=smooth)
            self.play(FadeIn(l1), FadeIn(l2), run_time=max(0.6, d * 0.12))
            self.rest(tr)

        self.big, self.s1, self.s2 = big, s1, s2
        self.setup_labels = VGroup(a_lab, l1, l2)

    # --------------------------------------------------------------- act_balance
    def act_balance(self):
        g = self.g
        ov, gTR, gBL = self.highlights(g)
        self.ov, self.gTR, self.gBL = ov, gTR, gBL

        twice = tex(r"\times 2", 44, INK, 1.4).move_to(g["C"])
        m1 = txt("missed", 30, INK, 1.5).move_to(g["gTR"])
        m2 = txt("missed", 30, INK, 1.5).move_to(g["gBL"])

        note = body("Counted twice here. Missed at these corners.", size=36)
        bal = body("The areas started equal, so they must cancel.",
                   size=36, color=ACID)
        self.stack([note, bal], top=BOT_TOP, buff=0.34)

        with self.voiceover(
            "Drop them into opposite corners. Since a is less than two b, they "
            "have to overlap. That overlap gets counted twice. These two corners "
            "get missed entirely."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.setup_labels), run_time=d * 0.10)
            self.play(FadeIn(ov, scale=0.85), FadeIn(twice), run_time=d * 0.26)
            self.play(FadeIn(gTR, scale=0.85), FadeIn(gBL, scale=0.85),
                      FadeIn(m1), FadeIn(m2), run_time=d * 0.26)
            self.play(FadeIn(note), run_time=d * 0.20)
            self.rest(tr)

        with self.voiceover(
            "But the two squares started with exactly the same area as the big "
            "one. So the double counted bit must exactly cancel the missing bits."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(bal), run_time=d * 0.30)
            self.play(Indicate(ov, color=MAGENTA, scale_factor=1.10),
                      Indicate(gTR, color=CYAN, scale_factor=1.10),
                      Indicate(gBL, color=CYAN, scale_factor=1.10),
                      run_time=d * 0.45)
            self.rest(tr)

        self.balance_labels = VGroup(twice, m1, m2)
        self.balance_text = VGroup(note, bal)

    # -------------------------------------------------------------- act_equation
    def act_equation(self):
        g = self.g
        row1 = self.swatch_row(MAGENTA, "overlap side", r"2b - a")
        row2 = self.swatch_row(CYAN, "each gap side", r"a - b")
        self.stack([row1, row2], top=TOP_TOP, buff=0.36)

        main = tex(r"(2b - a)^{2} \;=\; 2\,(a - b)^{2}", 54, ACID, COL_W)
        same = body("Same equation. Smaller whole numbers.", size=36, color=GOLD)
        self.stack([main, same], top=BOT_TOP, buff=0.36)
        box = SurroundingRectangle(main, color=ACID, buff=0.24,
                                   stroke_width=2.4, stroke_opacity=0.9)

        with self.voiceover(
            "The overlap has side two b minus a. Each gap has side a minus b. "
            "So two b minus a, squared, equals two times a minus b, squared."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.top_setup), FadeOut(self.balance_labels),
                      FadeOut(self.balance_text), run_time=d * 0.14)
            self.play(FadeIn(row1, shift=RIGHT * 0.2), run_time=d * 0.20)
            self.play(FadeIn(row2, shift=RIGHT * 0.2), run_time=d * 0.20)
            self.play(Write(main), run_time=d * 0.30)
            self.play(Create(box), run_time=max(0.6, d * 0.16))
            self.rest(tr)

        with self.voiceover(
            "That is the same equation again, with smaller numbers."
        ) as tr:
            self.play(FadeIn(same), run_time=min(1.3, tr.duration * 0.7))
            self.rest(tr)

        self.eq_top = VGroup(row1, row2)
        self.eq_bot = VGroup(main, same, box)

    # --------------------------------------------------------------- act_descent
    def act_descent(self):
        g = self.g
        big, s1, s2 = self.big, self.s1, self.s2
        ov, gTR, gBL = self.ov, self.gTR, self.gBL
        ghosts = VGroup()

        counter = Integer(1, font_size=64, color=LEVELS[0]).move_to([3.55, 3.55, 0])
        clab = txt("level", 26, DIM, 1.6).next_to(counter, UP, buff=0.16)
        shrink = tex(r"\times\,0.41421\ldots", 34, DIM, 3.0).move_to([0, -4.95, 0])

        with self.voiceover(
            "So do it again. The overlap becomes the new big square. "
            "The two gaps become the new small ones."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.eq_top), FadeOut(self.eq_bot),
                      FadeIn(counter), FadeIn(clab), run_time=d * 0.22)
            self.play(FadeIn(shrink), run_time=d * 0.14)
            self.rest(tr)

        with self.voiceover(
            "And again. And again. Every single time, smaller whole numbers."
        ) as tr:
            step = max(1.15, tr.duration / 3.4)
            for lvl in range(1, 4):
                col = LEVELS[lvl % len(LEVELS)]
                ng = self.geo(g["ov"], g["C"])

                ghost = Square(side_length=g["A"], stroke_color=LEVELS[(lvl - 1) % 6],
                               stroke_width=1.6, stroke_opacity=0.30,
                               fill_opacity=0).move_to(g["C"])
                ghosts.add(ghost)
                self.add(ghost)

                nxt = Integer(lvl + 1, font_size=64,
                              color=col).move_to(counter.get_center())
                self.play(
                    big.animate.set_stroke(color=col, width=1.6, opacity=0.30)
                               .set_fill(opacity=0.0),
                    FadeOut(s1), FadeOut(s2),
                    ov.animate.set_stroke(color=col, width=4, opacity=1.0)
                              .set_fill(color=col, opacity=0.07),
                    gTR.animate.move_to(ng["s2"])
                               .set_stroke(color=GOLD, width=3)
                               .set_fill(color=GOLD, opacity=0.20),
                    gBL.animate.move_to(ng["s1"])
                               .set_stroke(color=GOLD, width=3)
                               .set_fill(color=GOLD, opacity=0.20),
                    ReplacementTransform(counter, nxt),
                    run_time=step * 0.62, rate_func=smooth,
                )
                counter = nxt
                big, s1, s2 = ov, gBL, gTR
                g = ng

                ov, gTR, gBL = self.highlights(g)
                self.play(FadeIn(ov, scale=0.8), FadeIn(gTR, scale=0.8),
                          FadeIn(gBL, scale=0.8), run_time=step * 0.38)
            self.rest(tr)

        # zoom back out one whole level-set: the picture is identical
        with self.voiceover(
            "Zoom in and it is the exact same picture. It never, ever stops."
        ) as tr:
            d = tr.duration
            cur = VGroup(big, s1, s2, ov, gTR, gBL)
            self.play(FadeOut(ghosts), run_time=d * 0.18)
            self.play(cur.animate.scale(SHRINK ** -3, about_point=g["C"]),
                      run_time=d * 0.52, rate_func=smooth)
            g = self.geo(SQ_A, SQ_C)
            nxt = Integer(7, font_size=64, color=LEVELS[0]).move_to(
                counter.get_center())
            self.play(ReplacementTransform(counter, nxt), run_time=d * 0.14)
            counter = nxt
            self.rest(tr)

        self.descent_group = VGroup(big, s1, s2, ov, gTR, gBL, ghosts)
        self.descent_text = VGroup(counter, clab, shrink)

    # --------------------------------------------------------------- act_verdict
    def act_verdict(self):
        line1 = body("Whole numbers cannot shrink forever.", size=40, color=INK)
        line2 = body("So there was never a smallest fraction.", size=36, color=DIM)
        self.stack([line1, line2], top=TOP_TOP, buff=0.34)

        verdict = txt("IRRATIONAL", 86, ACID, COL_W, weight=BOLD)
        verdict.set_color_by_gradient(ACID, CYAN, BLUE)
        final = tex(r"\sqrt{2} \neq \frac{a}{b}", 66, INK, 5.0)
        self.stack([final, verdict], top=-2.35, buff=0.44)
        box = SurroundingRectangle(verdict, color=ACID, buff=0.26,
                                   stroke_width=2.6, stroke_opacity=0.9)

        with self.voiceover(
            "But whole numbers can't shrink forever. So there was never a "
            "smallest fraction to begin with."
        ) as tr:
            d = tr.duration
            self.play(self.descent_group.animate.set_stroke(opacity=0.22)
                                                 .set_fill(opacity=0.05),
                      FadeOut(self.descent_text), run_time=d * 0.24)
            self.play(FadeIn(line1), run_time=d * 0.34)
            self.play(FadeIn(line2), run_time=d * 0.30)
            self.rest(tr)

        with self.voiceover("Root two is irrational.") as tr:
            d = tr.duration
            self.play(Write(final), run_time=d * 0.42)
            self.play(FadeIn(verdict, scale=0.85), Create(box),
                      run_time=d * 0.42)
            self.play(Flash(verdict, color=ACID, line_length=0.34,
                            num_lines=20, flash_radius=2.6), run_time=0.7)
            self.rest(tr)

        self.wait(1.1)
        self.play(FadeOut(VGroup(self.descent_group, self.halo, line1, line2,
                                 final, verdict, box)), run_time=1.3)
        self.wait(0.4)
