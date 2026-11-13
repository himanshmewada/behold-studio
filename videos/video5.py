"""
PASCAL'S SECRET  ·  YouTube Short  ·  1080x1920  ·  ~58 s
=========================================================
Colour the odd entries of Pascal's triangle and Sierpinski's gasket appears.

LAYOUT RULES (these caused the earlier visual defects)
-----------------------------------------------------
* ONE stack() call per phase. Never mix a centre-anchored move_to with a
  top-anchored stack in the same region — that is what collided.
* body() wraps at 44 characters, which is what actually fits at font 34 in
  an 8.2-unit column. The old 34-char wrap forced orphan lines.
* The three-colour finale recolours ODD cells only. Repainting even cells
  fills the gasket's holes and destroys the fractal being explained.

THE MATHEMATICS (verified at import)
-----------------------------------
Lucas mod 2      C(n,k) odd  <=>  (k AND n) == k
Row count        #odd in row n = 2**popcount(n)
Block count      #odd in rows 0 .. 2**m - 1 = 3**m
Thirds           rows 0..31 = top copy; rows 32..63 split at k = 32 give the
                 left and right copies. Each holds exactly 3**5 = 243 odd
                 cells, so the three are congruent half-scale gaskets and
                 dim = log 3 / log 2 = 1.5849625...

RENDER
------
    manim -p pascal_secret.py PascalsSecret
    PREVIEW = True -> 540x960 draft      FPS = 60 -> smoother, slower
"""

from contextlib import contextmanager
from math import comb
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
GOLD = "#ffc233"
CYAN = "#00e5d0"
MAGENTA = "#ff2d95"
ACID = "#b6ff3d"
RED = "#ff5252"
THIRDS = ["#ffc233", "#00e5d0", "#ff2d95"]

# --------------------------------------------------------------- geometry
N_ROWS = 64
PITCH = 0.125
ROW_H = PITCH * np.sqrt(3) / 2
TOP_Y = 4.05
CELL = PITCH * 0.90

BIG_PITCH = 1.05
BIG_ROW_H = BIG_PITCH * np.sqrt(3) / 2
BIG_TOP_Y = 4.30
BIG_ROWS = 6

COL_W = 8.20
HEAD_TOP = 7.15  # top text zone
FOOT_TOP = -3.20  # below the full gasket (bottom at -2.83)
DEMO_TOP = 3.10  # below the shrunken ghost gasket
GHOST_Y = 5.10
GHOST_S = 0.42
GASKET_CY = 0.64  # bbox centre of the full-size gasket


def P3(p):
    return np.array([p[0], p[1], 0.0], dtype=float)


def cell_pos(n, k):
    return np.array([(k - n / 2.0) * PITCH, TOP_Y - n * ROW_H, 0.0])


def big_pos(n, k):
    return np.array([(k - n / 2.0) * BIG_PITCH, BIG_TOP_Y - n * BIG_ROW_H, 0.0])


# --------------------------------------------------------- verified parity
def parity_bits(n, k):
    return 1 if (k & n) == k else 0


def popcount(n):
    return bin(n).count("1")


def verify():
    for n in range(N_ROWS):
        row = [comb(n, k) % 2 for k in range(n + 1)]
        assert row == [parity_bits(n, k) for k in range(n + 1)], f"Lucas fails at {n}"
        assert sum(row) == 2 ** popcount(n), f"row count fails at {n}"
    for m in range(1, 7):
        total = sum(comb(n, k) % 2 for n in range(2**m) for k in range(n + 1))
        assert total == 3**m, f"block count fails at m={m}"
    print(f"  Lucas mod 2 verified against math.comb for all {N_ROWS} rows")
    print("  row counts = 2^popcount(n); block counts = 3^m verified")
    print(f"  dimension log3/log2 = {np.log(3) / np.log(2):.7f}")


verify()


# -------------------------------------------------------------- text helpers
def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def wrap(s, width=44):
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


def body(s, size=34, color=INK, maxw=COL_W, width=44):
    return fit(
        Text(wrap(s, width), font_size=size, color=color, line_spacing=0.85), maxw
    )


def tex(s, size=48, color=INK, maxw=COL_W):
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


def stack(mobs, top, buff=0.32):
    """The ONLY layout primitive: top-anchored, driven by real heights."""
    y = top
    for m in mobs:
        m.move_to([0.0, y, 0.0], aligned_edge=UP)
        y -= m.height + buff
    return VGroup(*mobs)


# ===================================================================== scene
class PascalsSecret(Base):
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

    def bits_row(self, label, value, nbits, verdict=None, vcolor=INK):
        lab = txt(label, 30, DIM, 1.9)
        cells = VGroup()
        for i in range(nbits - 1, -1, -1):
            b = (value >> i) & 1
            sq = Square(
                side_length=0.52,
                stroke_color=EDGE,
                stroke_width=1.6,
                fill_color=GOLD if b else SURFACE,
                fill_opacity=0.92 if b else 1.0,
            )
            d = MathTex(str(b), font_size=30, color=BG if b else DIM)
            cells.add(VGroup(sq, d))
        cells.arrange(RIGHT, buff=0.10)
        parts = [lab, cells]
        if verdict:
            parts.append(txt(verdict, 30, vcolor, 3.0))
        return VGroup(*parts).arrange(RIGHT, buff=0.34), cells

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.act_stage()
        self.act_build()
        self.act_parity()
        self.act_reveal()
        self.act_binary()
        self.act_count()
        self.act_dimension()

    # ----------------------------------------------------------------- stage
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
                    radius=r, stroke_width=0, fill_color=GOLD, fill_opacity=o
                ).move_to([0.0, 0.6, 0.0])
                for r, o in ((4.6, 0.028), (3.5, 0.032), (2.4, 0.030))
            ]
        )
        self.add(halo)
        self.halo = halo

    # ----------------------------------------------------------------- build
    def act_build(self):
        kick = pill("PASCAL'S TRIANGLE", 28, ACID)
        rule = body("Each number is the sum of the two above it.", color=DIM)
        self.build_text = stack([kick, rule], top=HEAD_TOP, buff=0.40)

        boxes, nums, odd_n, even_n = VGroup(), VGroup(), VGroup(), VGroup()
        for n in range(BIG_ROWS):
            for k in range(n + 1):
                v = comb(n, k)
                box = RoundedRectangle(
                    corner_radius=0.12,
                    width=BIG_PITCH * 0.88,
                    height=BIG_PITCH * 0.88,
                    stroke_color=EDGE,
                    stroke_width=1.8,
                    fill_color=SURFACE,
                    fill_opacity=1.0,
                )
                box.move_to(big_pos(n, k))
                num = MathTex(str(v), font_size=42, color=INK)
                num.move_to(box.get_center())
                boxes.add(box)
                nums.add(num)
                (odd_n if v % 2 else even_n).add(num)
                box._odd = bool(v % 2)

        self.big_boxes, self.big_nums = boxes, nums
        self.odd_boxes = VGroup(*[b for b in boxes if b._odd])
        self.even_boxes = VGroup(*[b for b in boxes if not b._odd])
        self.odd_nums, self.even_nums = odd_n, even_n

        with self.voiceover(
            "Pascal's triangle. Every number is the sum of the two above it. "
            "That's the whole rule."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(kick), FadeIn(rule), run_time=d * 0.24)
            self.play(
                LaggedStart(*[FadeIn(b, scale=0.7) for b in boxes], lag_ratio=0.05),
                run_time=d * 0.44,
            )
            self.play(
                LaggedStart(*[FadeIn(v) for v in nums], lag_ratio=0.04),
                run_time=d * 0.32,
            )
            self.rest(tr)

    # ---------------------------------------------------------------- parity
    def act_parity(self):
        legend_odd = VGroup(
            Square(side_length=0.34, fill_color=GOLD, fill_opacity=0.9, stroke_width=0),
            txt("odd", 30, GOLD, 1.4),
        ).arrange(RIGHT, buff=0.20)
        legend_even = VGroup(
            Square(
                side_length=0.34,
                fill_color=SURFACE,
                fill_opacity=1.0,
                stroke_color=EDGE,
                stroke_width=1.6,
            ),
            txt("even", 30, DIM, 1.4),
        ).arrange(RIGHT, buff=0.20)
        legend = VGroup(legend_odd, legend_even).arrange(RIGHT, buff=0.70)
        legend.move_to([0.0, -1.35, 0.0])

        with self.voiceover(
            "Now forget the actual numbers. Ask one question only: odd, or even? "
            "Odd lights up. Even goes dark."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(legend), run_time=d * 0.20)
            self.play(
                self.odd_boxes.animate.set_fill(color=GOLD, opacity=0.90).set_stroke(
                    color=GOLD, opacity=0.9
                ),
                self.odd_nums.animate.set_color(BG),
                self.even_boxes.animate.set_fill(color=SURFACE, opacity=1.0).set_stroke(
                    color=EDGE, opacity=0.5
                ),
                self.even_nums.animate.set_color(DIM),
                run_time=d * 0.46,
            )
            self.play(self.big_nums.animate.set_fill(opacity=0.0), run_time=d * 0.24)
            self.rest(tr)

        self.legend = legend

    # ---------------------------------------------------------------- reveal
    def act_reveal(self):
        rows, targets = [], []
        thirds = [VGroup(), VGroup(), VGroup()]  # ODD cells only
        evens = VGroup()
        flat = VGroup()

        for n in range(N_ROWS):
            row, tgt = [], []
            for k in range(n + 1):
                odd = parity_bits(n, k)
                c = Square(
                    side_length=CELL,
                    stroke_width=0,
                    fill_color=GOLD if odd else SURFACE,
                    fill_opacity=0.0,
                ).move_to(cell_pos(n, k))
                row.append(c)
                tgt.append(0.95 if odd else 0.55)
                flat.add(c)
                if odd:
                    if n < 32:
                        thirds[0].add(c)
                    elif k < 32:
                        thirds[1].add(c)
                    else:
                        thirds[2].add(c)
                else:
                    evens.add(c)
            rows.append(row)
            targets.append(tgt)

        assert [len(t) for t in thirds] == [243, 243, 243], [len(t) for t in thirds]
        print("  three half-scale gaskets: 243 odd cells each (3^5), total 3^6")

        grow = ValueTracker(0.0)
        done = [False] * N_ROWS

        def up(_g):
            v = grow.get_value()
            for n in range(N_ROWS):
                if done[n]:
                    continue
                o = float(np.clip(v - n, 0.0, 1.0))
                if o >= 1.0:
                    done[n] = True
                for c, t in zip(rows[n], targets[n]):
                    c.set_fill(opacity=o * t)

        flat.add_updater(up)
        self.add(flat)

        cap = body("Sixty-four rows. Nothing but parity.", color=DIM)
        name = txt("SIERPINSKI", 62, GOLD, COL_W, weight=BOLD)
        name.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        sub = txt("a fractal, hiding inside addition", 32, INK, COL_W)
        self.reveal_text = stack([cap, name, sub], top=FOOT_TOP, buff=0.30)

        with self.voiceover(
            "Keep going. Sixty-four rows of nothing but odd and even. "
            "And there it is: Sierpinski's triangle."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.big_boxes),
                FadeOut(self.big_nums),
                FadeOut(self.legend),
                FadeOut(self.build_text),
                run_time=d * 0.16,
            )
            self.play(
                grow.animate.set_value(N_ROWS),
                run_time=d * 0.56,
                rate_func=rate_functions.ease_out_cubic,
            )
            flat.clear_updaters()
            for n in range(N_ROWS):
                for c, t in zip(rows[n], targets[n]):
                    c.set_fill(opacity=t)
            self.play(FadeIn(cap), run_time=d * 0.10)
            self.play(
                FadeIn(name, scale=0.85), FadeIn(sub), run_time=max(0.8, d * 0.18)
            )
            self.rest(tr)

        self.gasket, self.thirds, self.evens = flat, thirds, evens

    # ---------------------------------------------------------------- binary
    def act_binary(self):
        head = body("Write the row and the position in binary.")
        rule = tex(
            r"\binom{n}{k}\ \text{odd}\iff (k\ \mathrm{AND}\ n)=k", 42, ACID, COL_W
        )
        r5, c5 = self.bits_row("row 5", 5, 3)
        r3, c3 = self.bits_row("k = 3", 3, 3, "10  even", RED)
        r4, c4 = self.bits_row("k = 4", 4, 3, "5  odd", ACID)
        note = body("That middle bit does not fit.", size=30, color=RED)
        good = body("Every bit fits, so the entry is odd.", size=30, color=ACID)
        self.binary = stack(
            [head, rule, r5, r3, r4, note, good], top=DEMO_TOP, buff=0.34
        )

        bad = VGroup(
            SurroundingRectangle(c5[1], color=RED, buff=0.09, stroke_width=2.6),
            SurroundingRectangle(c3[1], color=RED, buff=0.09, stroke_width=2.6),
        )
        self.binary.add(bad)

        with self.voiceover(
            "Why? Binary. The entry is odd exactly when every one-bit of the "
            "position also sits in the row. Row five is one oh one. Position "
            "three has a bit that row five doesn't, so ten is even. Position "
            "four fits, so five is odd."
        ) as tr:
            d = tr.duration
            self.play(
                self.gasket.animate.scale(GHOST_S)
                .move_to([0.0, GHOST_Y, 0.0])
                .set_fill(opacity=0.20),
                FadeOut(self.reveal_text),
                run_time=d * 0.16,
            )
            self.play(FadeIn(head), Write(rule), run_time=d * 0.20)
            self.play(FadeIn(r5), run_time=d * 0.10)
            self.play(FadeIn(r3), Create(bad), FadeIn(note), run_time=d * 0.22)
            self.play(FadeIn(r4), FadeIn(good), run_time=d * 0.22)
            self.rest(tr)

    # ----------------------------------------------------------------- count
    def act_count(self):
        head = body("So count the one-bits in a row.")
        formula = tex(
            r"\#\text{odd in row } n = 2^{\,\text{popcount}(n)}", 42, GOLD, COL_W
        )
        r7, _ = self.bits_row("row 7", 7, 3, "8 odd", ACID)
        r8, _ = self.bits_row("row 8", 8, 4, "2 odd", DIM)
        full = txt("the entire row, odd", 30, ACID, COL_W)
        sparse = txt("just the two ends", 30, DIM, COL_W)
        self.counts = stack(
            [head, formula, r7, r8, full, sparse], top=DEMO_TOP, buff=0.36
        )

        with self.voiceover(
            "So count the one-bits in a row, and two to that power tells you how "
            "many odd entries it has. Row seven: three ones, eight odds. The "
            "entire row."
        ) as tr:
            d = tr.duration
            self.play(FadeOut(self.binary), run_time=d * 0.14)
            self.play(FadeIn(head), Write(formula), run_time=d * 0.26)
            self.play(FadeIn(r7), FadeIn(full), run_time=d * 0.28)
            self.play(FadeIn(r8), FadeIn(sparse), run_time=d * 0.22)
            self.rest(tr)

    # ------------------------------------------------------------- dimension
    def act_dimension(self):
        three = txt("three copies, half the size", 34, INK, COL_W)
        dim = tex(r"\dim = \frac{\log 3}{\log 2} = 1.5849\ldots", 50, GOLD, COL_W)
        punch = body("Not a line. Not a plane. In between.", color=CYAN)
        tail = stack([three, dim, punch], top=FOOT_TOP, buff=0.30)

        with self.voiceover(
            "And the shape itself? Three copies of itself, at half the size. "
            "Dimension: log three over log two. One point five eight five. "
            "Not a line, not a plane. Something in between."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.counts),
                self.gasket.animate.scale(1 / GHOST_S).move_to([0.0, GASKET_CY, 0.0]),
                run_time=d * 0.20,
            )
            # odd cells take the three hues; even cells stay dark so the
            # gasket's holes survive the recolour
            self.play(
                *[
                    t.animate.set_fill(color=col, opacity=0.95)
                    for t, col in zip(self.thirds, THIRDS)
                ],
                self.evens.animate.set_fill(color=SURFACE, opacity=0.55),
                FadeIn(three),
                run_time=d * 0.26,
            )
            self.play(Write(dim), run_time=d * 0.24)
            self.play(
                FadeIn(punch),
                Flash(
                    dim, color=GOLD, line_length=0.30, num_lines=18, flash_radius=2.2
                ),
                run_time=max(0.9, d * 0.20),
            )
            self.rest(tr)

        self.wait(1.0)
        self.play(FadeOut(VGroup(self.gasket, self.halo, tail)), run_time=1.3)
        self.wait(0.4)
