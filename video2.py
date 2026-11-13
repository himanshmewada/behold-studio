"""
Times Tables on a Circle — narrated cut
=======================================
Label N points on a circle 0..N-1 and join every k to m*k (mod N).
The chords are straight; their envelope is an epicycloid with (m-1) cusps:
    m = 2 -> cardioid,  m = 3 -> nephroid, ...

Proof shown on screen:
    P = e^{i t}, Q = e^{i m t}  ->  chord PQ touches the envelope at
    E(t) = (m*P + Q)/(m+1), a fraction 1/(m+1) along the chord.
    E is a sum of two rotating vectors = a circle rolling on a circle.

Setup
-----
    pip install manim "manim-voiceover[gtts,transcription]"
    # gTTS needs internet. Whisper ("transcription") is only needed for bookmarks;
    # set TRANSCRIPTION_MODEL = None to skip that download.
    # No manim-voiceover at all? The file still renders, as a paced silent cut.

Render
------
    manim -pql times_tables_circle.py TimesTablesOnACircle   # fast preview
    manim -pqh times_tables_circle.py TimesTablesOnACircle   # 1080p60 + narration
"""

from contextlib import contextmanager
import re

from manim import *
import numpy as np

# --------------------------------------------------------------- narration
USE_VOICEOVER = True          # False -> silent cut, identical choreography
TRANSCRIPTION_MODEL = "base"  # None -> no whisper, bookmarks degrade to timing

try:
    from manim_voiceover import VoiceoverScene as _VOScene
    from manim_voiceover.services.gtts import GTTSService
except Exception:  # library missing -> fall back to the silent base below
    _VOScene, GTTSService = None, None


class _SilentTracker:
    def __init__(self, scene, duration):
        self._scene, self.duration, self._t0 = scene, duration, scene._clock

    def time_until_end(self):
        return max(0.0, self.duration - (self._scene._clock - self._t0))


class _SilentScene(Scene):
    """Stand-in that estimates speech timing from word count, so the animation
    keeps its rhythm even when no speech service is available."""

    _clock = 0.0

    def set_speech_service(self, *a, **k):
        pass

    def wait_until_bookmark(self, *a, **k):
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
        yield _SilentTracker(self, max(1.6, words / 2.55))


Base = _VOScene if (USE_VOICEOVER and _VOScene is not None) else _SilentScene

# ----------------------------------------------------------------- palette
BG, INK, DIM, GOLD = "#080b16", "#e9edf7", "#7f8aa8", "#ffd479"
PALETTE = ["#4cc9f0", "#4895ef", "#7209b7", "#f72585", "#ff7b54", "#ffd479"]
R0 = 2.55


# ----------------------------------------------------------------- helpers
def cpoint(angle, center=ORIGIN, radius=R0):
    """Point on a circle at a given angle (radians)."""
    return np.asarray(center) + radius * np.array([np.cos(angle), np.sin(angle), 0.0])


def dial_point(k, n, center=ORIGIN, radius=R0):
    """Position of label k on a dial of n points (k may be fractional)."""
    return cpoint(TAU * k / n, center, radius)


def chord_family(n, m, center=ORIGIN, radius=R0, width=1.3, opacity=0.85):
    """All chords k -> m*k (mod n). k = 0 is skipped (degenerate chord)."""
    fam = VGroup(*[
        Line(dial_point(k, n, center, radius),
             dial_point(m * k, n, center, radius),
             stroke_width=width, stroke_opacity=opacity)
        for k in range(1, n)
    ])
    fam.set_color_by_gradient(*PALETTE)
    return fam


def retarget(fam, n, m, center=ORIGIN, radius=R0):
    """Re-aim an existing family at a new (possibly non-integer) multiplier."""
    for k, line in zip(range(1, n), fam):
        line.set_points_as_corners([dial_point(k, n, center, radius),
                                    dial_point(m * k, n, center, radius)])


# ------------------------------------------------------------------- scene
class TimesTablesOnACircle(Base):
    C = LEFT * 1.7 + DOWN * 0.1      # dial centre (text column lives on the right)
    R = 2.55
    N_SMALL = 20
    N_BIG = 220
    PX = 4.4

    # ---------------- narration / layout utilities ----------------
    def make_service(self):
        try:
            return GTTSService(transcription_model=TRANSCRIPTION_MODEL)
        except Exception:
            return GTTSService()      # no whisper -> bookmarks simply won't fire

    def cue(self, mark):
        """Sync to a <bookmark/> when the service produced one; otherwise skip."""
        try:
            self.wait_until_bookmark(mark)
        except Exception:
            pass

    def remaining(self, tracker):
        try:
            return max(0.0, float(tracker.time_until_end()))
        except Exception:
            return 0.0

    def rest(self, tracker):
        left = self.remaining(tracker)
        if left > 0.05:
            self.wait(left)

    def panel(self, mob, y, max_w=5.0):
        if mob.width > max_w:
            mob.scale_to_fit_width(max_w)
        mob.move_to(np.array([self.PX, y, 0.0]))
        return mob

    # ---------------- script ----------------
    def construct(self):
        self.camera.background_color = BG
        if Base is not _SilentScene:
            self.set_speech_service(self.make_service())
        self.intro()
        self.dial()
        self.zoom_in()
        self.sweep()
        self.why()
        self.finale()

    # ------------------------------------------------------------------ 1
    def intro(self):
        ghost = chord_family(110, 2, ORIGIN, 3.35, width=0.8, opacity=0.30)
        title = Text("Times Tables on a Circle", font_size=46, weight=BOLD)
        title.set_color_by_gradient("#4cc9f0", "#f72585", "#ffd479")
        sub = Text("where modular arithmetic turns into geometry",
                   font_size=25, color=DIM).next_to(title, DOWN, buff=0.35)
        head = VGroup(title, sub).move_to(ORIGIN)
        back = BackgroundRectangle(head, color=BG, buff=0.3, fill_opacity=0.8)

        with self.voiceover(
            "Here is a strange little fact. <bookmark mark='title'/> "
            "A times table, drawn on a circle, becomes a curve."
        ) as tracker:
            self.play(FadeIn(ghost, lag_ratio=0.02),
                      run_time=max(2.0, tracker.duration * 0.5))
            self.cue("title")
            self.play(FadeIn(back), Write(title),
                      run_time=max(1.6, tracker.duration * 0.45))

        with self.voiceover(
            "It is called a cardioid, and it falls straight out of modular arithmetic. "
            "Let's build it, one line at a time."
        ) as tracker:
            self.play(FadeIn(sub, shift=UP * 0.2), run_time=1.0)
            self.rest(tracker)

        self.play(FadeOut(head), FadeOut(back), FadeOut(ghost), run_time=1.2)

    # ------------------------------------------------------------------ 2
    def dial(self):
        n = self.N_SMALL
        circle = Circle(radius=self.R, stroke_color=DIM,
                        stroke_width=2, stroke_opacity=0.8).move_to(self.C)
        dots = VGroup(*[Dot(dial_point(k, n, self.C, self.R), radius=0.05, color=INK)
                        for k in range(n)])
        labels = VGroup(*[Text(str(k), font_size=22, color=DIM)
                          .move_to(dial_point(k, n, self.C, self.R + 0.34))
                          for k in range(n)])
        chords = chord_family(n, 2, self.C, self.R, width=2.2, opacity=0.95)
        self.circle, self.small_chords, self.dots, self.labels = circle, chords, dots, labels

        head = self.panel(Text("the rule", font_size=28, color=GOLD), 2.6)
        nlab = self.panel(MathTex(rf"N = {n}", font_size=36), 1.9)
        rule = self.panel(MathTex(r"k \;\longmapsto\; 2k \;\;(\mathrm{mod}\ N)",
                                  font_size=36), 1.0)
        note = self.panel(Text("wrap around after N", font_size=22, color=DIM), -2.2)
        ex1 = self.panel(MathTex(r"3 \;\mapsto\; 6", font_size=34), 0.1)
        ex2 = self.panel(MathTex(r"12 \;\mapsto\; 24 \equiv 4", font_size=34), -0.8)

        with self.voiceover(
            "Start with twenty points, evenly spaced around a circle, "
            "labelled zero to nineteen."
        ) as tracker:
            d = tracker.duration
            self.play(Create(circle), run_time=d * 0.34)
            self.play(LaggedStart(*[FadeIn(dot, scale=0.5) for dot in dots],
                                  lag_ratio=0.06), run_time=d * 0.34)
            self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.05),
                      run_time=d * 0.32)

        with self.voiceover(
            "The rule is simple. Take a number k, double it, and keep the remainder "
            "after dividing by twenty. Then draw a straight line from k to that answer."
        ) as tracker:
            d = tracker.duration
            self.play(FadeIn(head), FadeIn(nlab), run_time=d * 0.28)
            self.play(Write(rule), run_time=d * 0.5)
            self.rest(tracker)

        with self.voiceover("Three, for example, goes to six.") as tracker:
            d = tracker.duration
            self.play(Indicate(dots[3], color=GOLD), Indicate(labels[3], color=GOLD),
                      FadeIn(ex1), run_time=d * 0.55)
            self.play(Create(chords[2]), Indicate(dots[6], color=GOLD),
                      run_time=d * 0.45)          # family index = k - 1

        with self.voiceover(
            "Twelve goes to twenty four. But twenty four wraps all the way around "
            "the dial, and lands on four."
        ) as tracker:
            d = tracker.duration
            self.play(Indicate(dots[12], color=GOLD), Indicate(labels[12], color=GOLD),
                      FadeIn(ex2), run_time=d * 0.4)
            self.play(Create(chords[11]), Indicate(dots[4], color=GOLD),
                      FadeIn(note), run_time=d * 0.45)
            self.rest(tracker)

        others = VGroup(*[l for i, l in enumerate(chords) if i not in (2, 11)])
        with self.voiceover(
            "Now do exactly the same thing, for every number on the dial."
        ) as tracker:
            self.play(LaggedStart(*[Create(l) for l in others], lag_ratio=0.05),
                      run_time=max(2.5, tracker.duration))
            self.rest(tracker)

        self.small_panel = VGroup(head, nlab, rule, ex1, ex2, note)

    # ------------------------------------------------------------------ 3
    def zoom_in(self):
        n = self.N_BIG
        big = chord_family(n, 2, self.C, self.R, width=1.25, opacity=0.85)
        fine = VGroup(*[Dot(dial_point(k, n, self.C, self.R), radius=0.018,
                            color=INK, fill_opacity=0.55) for k in range(n)])
        cap = self.panel(Text("same rule, more points", font_size=28, color=GOLD), 2.2)
        nlab = self.panel(MathTex(rf"N = {n}", font_size=36), 1.5)
        hint = self.panel(Text("a smooth curve appears\nout of straight lines",
                               font_size=24, color=INK, line_spacing=0.8), -1.6)

        with self.voiceover(
            "Twenty lines are a little crude. So keep the rule exactly as it is, "
            "and raise the number of points to two hundred and twenty."
        ) as tracker:
            d = tracker.duration
            self.play(FadeOut(self.small_panel), FadeOut(self.dots),
                      FadeOut(self.labels), FadeOut(self.small_chords),
                      run_time=min(1.4, d * 0.3))
            self.play(FadeIn(cap), FadeIn(nlab), FadeIn(fine), run_time=min(1.5, d * 0.3))
            self.rest(tracker)

        with self.voiceover(
            "Every line is still perfectly straight. <bookmark mark='curve'/> "
            "But their outline is smooth. A cardioid, hiding inside the two times table."
        ) as tracker:
            self.play(LaggedStart(*[Create(l) for l in big], lag_ratio=0.008),
                      run_time=max(4.0, tracker.duration * 0.68))
            self.cue("curve")
            self.play(FadeIn(hint), run_time=1.0)
            self.rest(tracker)

        self.big = big
        self.dense_panel = VGroup(cap, nlab, hint)

    # ------------------------------------------------------------------ 4
    def sweep(self):
        m = ValueTracker(2)
        self.m = m
        self.big.add_updater(lambda g: retarget(g, self.N_BIG, m.get_value(), self.C, self.R))

        times = MathTex(r"\times", font_size=54, color=GOLD)
        num = DecimalNumber(2, num_decimal_places=2, font_size=58, color=GOLD)
        readout = self.panel(VGroup(times, num).arrange(RIGHT, buff=0.25), 2.0)
        anchor = num.get_center().copy()

        def read(mob):
            mob.set_value(m.get_value())
            mob.move_to(anchor)
        num.add_updater(read)

        formula = self.panel(MathTex(r"k \;\longmapsto\; m\,k \;\;(\mathrm{mod}\ N)",
                                     font_size=34), 0.9)
        cusp = self.panel(MathTex(r"\text{cusps} = m - 1", font_size=34), -2.3)

        def name(v):
            txt = {2: "cardioid (1 cusp)", 3: "nephroid (2 cusps)"}.get(
                v, f"epicycloid ({v - 1} cusps)")
            return self.panel(Text(txt, font_size=26, color=INK), -1.5)

        current = name(2)
        with self.voiceover(
            "Now let's change the multiplier, and watch the shape answer."
        ) as tracker:
            self.play(FadeOut(self.dense_panel), FadeIn(readout), FadeIn(formula),
                      run_time=min(1.5, tracker.duration * 0.5))
            self.play(FadeIn(current), FadeIn(cusp), run_time=0.8)
            self.rest(tracker)

        with self.voiceover("Times three gives a nephroid, with two cusps.") as tracker:
            self.play(m.animate.set_value(3),
                      run_time=max(2.2, tracker.duration * 0.8), rate_func=smooth)
            nxt = name(3)
            self.play(FadeOut(current), FadeIn(nxt), run_time=0.5)
            current = nxt

        with self.voiceover("Times four gives three cusps. Times five gives four.") as tracker:
            d = tracker.duration
            self.play(m.animate.set_value(4), run_time=d * 0.42, rate_func=smooth)
            nxt = name(4)
            self.play(FadeOut(current), FadeIn(nxt), run_time=0.35)
            current = nxt
            self.play(m.animate.set_value(5), run_time=d * 0.42, rate_func=smooth)
            nxt = name(5)
            self.play(FadeOut(current), FadeIn(nxt), run_time=0.35)
            current = nxt

        with self.voiceover(
            "In general, times m draws an epicycloid with m minus one cusps. "
            "And between the whole numbers the pattern never closes, which is where "
            "these shimmering interference patterns come from."
        ) as tracker:
            d = tracker.duration
            self.play(m.animate.set_value(6), run_time=d * 0.4, rate_func=smooth)
            nxt = name(6)
            self.play(FadeOut(current), FadeIn(nxt), run_time=0.4)
            current = nxt
            self.play(m.animate.set_value(7), run_time=d * 0.4, rate_func=smooth)
            nxt = name(7)
            self.play(FadeOut(current), FadeIn(nxt), run_time=0.4)
            current = nxt
            self.rest(tracker)

        with self.voiceover(
            "Back to two. And now the real question. Why is there a curve at all?"
        ) as tracker:
            self.play(m.animate.set_value(2),
                      run_time=max(2.5, tracker.duration * 0.8), rate_func=smooth)
            last = name(2)
            self.play(FadeOut(current), FadeIn(last), run_time=0.5)
            self.rest(tracker)

        self.sweep_panel = VGroup(readout, formula, cusp, last)

    # ------------------------------------------------------------------ 5
    def why(self):
        C, R, th = self.C, self.R, ValueTracker(0)
        P = lambda: cpoint(th.get_value(), C, R)          # e^{i theta}
        Q = lambda: cpoint(2 * th.get_value(), C, R)      # e^{2i theta}
        M = lambda: (2 * P() + C) / 3                     # rolling-circle centre
        E = lambda: (2 * P() + Q()) / 3                   # envelope point

        chord = Line(P(), Q(), stroke_color=WHITE, stroke_width=2.5, stroke_opacity=0.9)
        chord.add_updater(lambda l: l.set_points_as_corners([P(), Q()]))
        pdot = Dot(P(), radius=0.06, color=BLUE_B).add_updater(lambda d: d.move_to(P()))
        qdot = Dot(Q(), radius=0.06, color=TEAL_B).add_updater(lambda d: d.move_to(Q()))
        edot = Dot(E(), radius=0.08, color=GOLD).add_updater(lambda d: d.move_to(E()))

        fixed = Circle(radius=R / 3, stroke_color=DIM, stroke_width=1.5,
                       stroke_opacity=0.6).move_to(C)
        roll = Circle(radius=R / 3, stroke_color=GOLD, stroke_width=1.5,
                      stroke_opacity=0.55).move_to(M())
        roll.add_updater(lambda c: c.move_to(M()))
        v1 = Arrow(C, M(), buff=0, stroke_width=5, color=BLUE_B,
                   max_tip_length_to_length_ratio=0.12)
        v1.add_updater(lambda a: a.put_start_and_end_on(C, M()))
        v2 = Arrow(M(), E(), buff=0, stroke_width=5, color=TEAL_B,
                   max_tip_length_to_length_ratio=0.25)
        v2.add_updater(lambda a: a.put_start_and_end_on(M(), E()))

        trace = TracedPath(E, stroke_color=GOLD, stroke_width=4.5)
        exact = ParametricFunction(
            lambda t: C + (2 * R / 3) * np.array([np.cos(t), np.sin(t), 0])
                        + (R / 3) * np.array([np.cos(2 * t), np.sin(2 * t), 0]),
            t_range=[0, TAU], color=GOLD, stroke_width=5)
        glow = exact.copy().set_stroke(width=16, opacity=0.18)

        t1 = self.panel(Text("why a curve?", font_size=28, color=GOLD), 2.6)
        f1 = self.panel(MathTex(r"P = e^{i\theta}, \quad Q = e^{2i\theta}", font_size=34), 1.8)
        f2 = self.panel(MathTex(r"E = \frac{2P + Q}{3}", font_size=38, color=GOLD), 0.9)
        t2 = self.panel(Text("each chord touches the curve\none third of the way along",
                             font_size=22, color=INK, line_spacing=0.8), -0.2)
        f3 = self.panel(MathTex(r"E(\theta)=\tfrac{2}{3}e^{i\theta}+\tfrac{1}{3}e^{2i\theta}",
                                font_size=32), -1.3)
        t3 = self.panel(Text("a circle rolling on a circle", font_size=23, color=DIM), -2.3)

        with self.voiceover(
            "Think of the points as complex numbers. P is e to the i theta, "
            "and Q is e to the two i theta."
        ) as tracker:
            self.play(FadeOut(self.sweep_panel),
                      self.big.animate.set_stroke(opacity=0.22),
                      run_time=min(1.2, tracker.duration * 0.3))
            self.play(FadeIn(t1), FadeIn(f1), run_time=1.0)
            self.rest(tracker)

        with self.voiceover(
            "As theta slides around the circle, the chord slides with it. "
            "A moving family of straight lines sweeps out an envelope."
        ) as tracker:
            self.play(FadeIn(chord), FadeIn(pdot), FadeIn(qdot), run_time=1.0)
            self.add(trace)
            self.play(th.animate.set_value(1.0),
                      run_time=max(2.5, self.remaining(tracker)), rate_func=linear)

        with self.voiceover(
            "Here is the key. <bookmark mark='third'/> Every chord touches that envelope "
            "exactly one third of the way along, at the point E equals two P plus Q, "
            "all over three."
        ) as tracker:
            self.play(FadeIn(t2), run_time=0.6)
            self.cue("third")
            self.play(FadeIn(f2), FadeIn(edot), run_time=1.0)
            self.play(th.animate.set_value(3.0),
                      run_time=max(3.0, self.remaining(tracker)), rate_func=linear)

        with self.voiceover(
            "Keep tracing that point, and it draws the cardioid exactly."
        ) as tracker:
            self.play(th.animate.set_value(TAU),
                      run_time=max(4.0, self.remaining(tracker)), rate_func=linear)
            trace.clear_updaters()
            self.rest(tracker)

        with self.voiceover(
            "Now look at what E really is. Two thirds of a vector spinning once, "
            "plus one third of a vector spinning twice."
        ) as tracker:
            d = tracker.duration
            self.play(FadeIn(glow), FadeIn(fixed), FadeIn(roll), FadeIn(v1), FadeIn(v2),
                      run_time=min(1.4, d * 0.3))
            self.play(FadeOut(chord), FadeOut(pdot), FadeOut(qdot), FadeOut(t2),
                      FadeIn(f3), FadeIn(t3), run_time=min(1.4, d * 0.3))
            self.rest(tracker)

        with self.voiceover(
            "That is a small circle, rolling around another circle. "
            "The two times table is literally a rolling wheel."
        ) as tracker:
            self.play(th.animate.set_value(2 * TAU),
                      run_time=max(8.0, tracker.duration), rate_func=linear)
            self.rest(tracker)

        self.machinery = VGroup(chord, pdot, qdot, fixed, roll, v1, v2, edot)
        self.why_panel = VGroup(t1, f1, f2, t2, f3, t3)
        self.trace, self.glow = trace, glow

    # ------------------------------------------------------------------ 6
    def finale(self):
        self.big.clear_updaters()
        art = VGroup(self.circle, self.big, self.glow, self.trace)
        cap = MathTex(r"k \;\longmapsto\; 2k \pmod N", font_size=44, color=INK)
        sub = Text("arithmetic becomes geometry", font_size=26, color=DIM)
        sub.next_to(cap, DOWN, buff=0.3)
        text = VGroup(cap, sub).move_to(DOWN * 3.35)

        with self.voiceover(
            "So the chords were never really the point. "
            "They are the shadow of something smoother."
        ) as tracker:
            d = tracker.duration
            self.play(FadeOut(self.machinery), FadeOut(self.why_panel),
                      self.big.animate.set_stroke(opacity=0.8),
                      run_time=min(1.4, d * 0.35))
            self.play(art.animate.move_to(ORIGIN).scale(1.05),
                      run_time=max(2.0, d * 0.4))
            self.rest(tracker)

        with self.voiceover(
            "Arithmetic, wrapped around a circle, becomes geometry. "
            "Try other multipliers, and see what curves are hiding in your tables."
        ) as tracker:
            self.play(FadeIn(cap), FadeIn(sub), run_time=1.2)
            self.play(art.animate.rotate(TAU, about_point=ORIGIN),
                      run_time=max(6.0, self.remaining(tracker)), rate_func=smooth)
            self.rest(tracker)

        self.play(FadeOut(art), FadeOut(text), run_time=2)
        self.wait(0.5)
