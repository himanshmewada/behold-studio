"""
THE FASTEST FALL  ·  16:9 YouTube video  ·  1920x1080  ·  ~4 min 50 s
=====================================================================
The brachistochrone: why the fastest slide is not a straight line,
why light already knows the answer, and why the wheel is a clock.

THE MATHEMATICS (every on-screen number is computed, then asserted)
------------------------------------------------------------------
Cycloid from A, rolling radius R:   P(t) = A + (R(t - sin t), -R(1 - cos t))
Hit B = A + (bx, -by):              (t - sin t)/(1 - cos t) = bx/by   (bisection)
Energy:                             v = sqrt(2 g * drop)
Snell invariant along the cycloid:  sin(alpha)/v = 1/(2 sqrt(gR))   EXACT
  because  alpha = t/2  and  drop = 2R sin^2(t/2)  -> the sines cancel.
Tangent property (Thales):          tangent at P passes through the wheel's
                                    lowest point; contact-P-bottom is 90 deg.
Time:                               dt = ds/v = sqrt(R/g) dt  -> T = t_B sqrt(R/g)
Tautochrone:                        u = cos(t/2) obeys u(t) = u0 cos(w t),
                                    w = sqrt(g/R)/2  ->  T = pi sqrt(R/g)
                                    from EVERY start. Beads use this exact flow.
Race competitors:                   straight line (analytic T), Galileo's
                                    circular arc (quadrature), cycloid.

LAYOUT RULES (house style)
--------------------------
* HUD chip on its own row (HUD_Y); progress rail at RAIL_Y.
* Right column placed only by stack(), driven by real mobject heights.
* Every act fades its own panel; stage objects persist explicitly.
* Updaters cleared before any FadeOut; DecimalNumber pre-synced with .update(0).
* One .animate chain per mobject per play().

SETUP / RENDER
--------------
pip install manim "manim-voiceover[gtts]"
manim -pqh videos/video6.py TheFastestFall     # 1080p + narration
PREVIEW = True -> 854x480 draft.  No voiceover lib? Renders as a paced silent cut.
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
GOLD = "#ffc233"
CYAN = "#2ee6d6"
MAGENTA = "#ff2d95"
ACID = "#b6ff3d"
RED = "#ff5252"

# ------------------------------------------------------------- layout grid
HUD_Y = 3.80
COL_TOP = 2.90
COL_L = 1.75
COL_W = 5.20
RAIL_Y, RAIL_X0, RAIL_X1 = -3.74, -6.55, 6.55
CHAPTERS = [
    (0.00, "01 / THE RACE"),
    (0.17, "02 / ONE RULE"),
    (0.33, "03 / LIGHT KNOWS THE WAY"),
    (0.52, "04 / THE WHEEL"),
    (0.72, "05 / THE CLOCK"),
    (0.86, "06 / SAME ARRIVAL"),
]

# ------------------------------------------------------------------- physics
G = 9.81
A = np.array([-6.55, 2.55, 0.0])
BX, BY = 7.0, 2.45
B = A + np.array([BX, -BY, 0.0])
STAGE_CX = 0.5 * (A[0] + B[0])


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
DIP_D = 2.0 * R  # turning depth = cycloid bottom
BOT = A + np.array([PI * R, -DIP_D, 0.0])
BOT_DX = PI * R
K_TRUE = 1.0 / (2.0 * np.sqrt(G * R))
T_CYC = TH_B * np.sqrt(R / G)  # exact
T_LINE = 2.0 * np.hypot(BX, BY) / np.sqrt(2 * G * BY)  # exact
OMEGA = 0.5 * np.sqrt(G / R)
T_TAU = PI * np.sqrt(R / G)
TAU_SLOW = 2.8  # tautochrone playback stretch
TH0S = [0.55, 1.25, 1.95, 2.65]
TAU_COLS = [CYAN, ACID, MAGENTA, BLUE]


def cyc_point(th):
    return A + np.array([R * (th - np.sin(th)), -R * (1 - np.cos(th)), 0.0])


def cyc_tangent(th):
    """Unit tangent, exact and singularity-free: (sin(t/2), -cos(t/2))."""
    return np.array([np.sin(th / 2), -np.cos(th / 2), 0.0])


def make_track(pts):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    drop = pts[0, 1] - 0.5 * (pts[:-1, 1] + pts[1:, 1])
    dt = seg / np.sqrt(2 * G * drop)
    cum = np.concatenate([[0.0], np.cumsum(dt)])
    return {"pts": pts, "cum": cum, "T": float(cum[-1])}


def track_point(track, t):
    cum, pts = track["cum"], track["pts"]
    t = float(np.clip(t, 0.0, track["T"]))
    i = int(np.clip(np.searchsorted(cum, t), 1, len(cum) - 1))
    f = (t - cum[i - 1]) / (cum[i] - cum[i - 1])
    return pts[i - 1] + f * (pts[i] - pts[i - 1])


M = 20001
_th = np.linspace(0, TH_B, M)
CYC_PTS = np.column_stack(
    [A[0] + R * (_th - np.sin(_th)), A[1] - R * (1 - np.cos(_th)), np.zeros(M)]
)
LINE_PTS = np.linspace(A, B, M)
H_ARC = (BX**2 + BY**2) / (2 * BX)
O_ARC = A + np.array([H_ARC, 0.0, 0.0])
_PHI_B = float(np.arctan2(-BY, BX - H_ARC) % TAU)
_phi = np.linspace(PI, _PHI_B, M)
ARC_PTS = np.column_stack(
    [O_ARC[0] + H_ARC * np.cos(_phi), O_ARC[1] + H_ARC * np.sin(_phi), np.zeros(M)]
)
TR_CYC, TR_LINE, TR_ARC = make_track(CYC_PTS), make_track(LINE_PTS), make_track(ARC_PTS)
T_ARC = TR_ARC["T"]


def snell_ray(n):
    """Refracted ray through n faster-and-faster layers, aimed at the cycloid's
    lowest point (where the true ray turns horizontal). Returns pts, k, max gap."""
    ys = np.linspace(0, DIP_D, n + 1)
    vm = np.sqrt(2 * G * 0.5 * (ys[:-1] + ys[1:]))

    def X(k):
        s = k * vm
        return float(np.sum(np.diff(ys) * s / np.sqrt(1 - s * s)))

    lo, hi = 1e-12, 0.999999 / vm.max()
    for _ in range(160):
        mid = 0.5 * (lo + hi)
        if X(mid) < BOT_DX:
            lo = mid
        else:
            hi = mid
    k = 0.5 * (lo + hi)
    s = k * vm
    xs = np.concatenate([[0.0], np.cumsum(np.diff(ys) * s / np.sqrt(1 - s * s))])
    pts = np.column_stack([A[0] + xs, A[1] - ys, np.zeros(n + 1)])
    th_i = 2 * np.arcsin(np.sqrt(np.clip(ys / (2 * R), 0, 1)))  # descending branch
    err = float(np.abs(xs - R * (th_i - np.sin(th_i))).max())
    return pts, k, err


def resample(pts, m=240):
    d = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    u = np.linspace(0, d[-1], m)
    return np.column_stack([np.interp(u, d, pts[:, i]) for i in range(3)])


# ------------------------------------------------------------------- verify
def verify():
    assert np.linalg.norm(cyc_point(TH_B) - B) < 1e-9
    assert abs(TR_CYC["T"] - T_CYC) / T_CYC < 3e-3
    assert T_CYC < T_ARC < T_LINE, "the race must finish cycloid, arc, line"
    th = np.linspace(0.05, TH_B, 4000)
    inv = np.sin(th / 2) / (2 * np.sqrt(G * R) * np.sin(th / 2))
    assert np.abs(inv - K_TRUE).max() < 1e-12, "Snell invariant must be exact"
    P = np.array([cyc_point(t) for t in th if t < PI])
    tt = th[th < PI]
    Tc = np.column_stack([A[0] + R * tt, np.full(len(tt), A[1]), np.zeros(len(tt))])
    Bo = np.column_stack(
        [A[0] + R * tt, np.full(len(tt), A[1] - 2 * R), np.zeros(len(tt))]
    )
    u1 = Tc - P
    u1 /= np.linalg.norm(u1, axis=1)[:, None]
    u2 = Bo - P
    u2 /= np.linalg.norm(u2, axis=1)[:, None]
    assert np.abs((u1 * u2).sum(1)).max() < 1e-9, "Thales: tangent -> wheel bottom"
    _, k2, e2 = snell_ray(2)
    _, k64, e64 = snell_ray(64)
    assert abs(k64 - K_TRUE) < 5e-3 and e64 < e2, "light must converge to the cycloid"
    for th0 in TH0S:  # tautochrone by u-substitution quadrature
        u0 = np.cos(th0 / 2)
        n = 200000
        u = (np.arange(n) + 0.5) / n * u0
        T = np.sum(2 * np.sqrt(R / G) * (u0 / n) / np.sqrt(u0**2 - u**2))
        assert abs(T - T_TAU) < 2e-3, f"tautochrone fails from theta0={th0}"
    print(f"  brachistochrone: theta_B={TH_B:.4f} rad, R={R:.4f}")
    print(
        f"  times: line {T_LINE:.2f}s | arc {T_ARC:.2f}s | cycloid {T_CYC:.2f}s"
        f"  (win by {T_ARC - T_CYC:.2f}s)"
    )
    print(f"  dip below finish: {DIP_D - BY:.3f} | Snell k_true={K_TRUE:.5f}")
    print(f"  light layers 2->64: gap {e2:.3f} -> {e64:.3f}, k {k2:.5f} -> {k64:.5f}")
    print(f"  tautochrone: every start {T_TAU:.4f}s = pi*sqrt(R/g)  [verified]")


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


def body(s, size=25, color=INK, maxw=COL_W, width=36):
    return fit(
        Text(wrap(s, width), font_size=size, color=color, line_spacing=0.9), maxw
    )


def tex(s, size=36, color=INK, maxw=COL_W):
    return fit(MathTex(s, font_size=size, color=color), maxw)


def curve_from(pts, color, width, opacity=1.0, step=60):
    m = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    m.set_points_smoothly(pts[::step])
    return m


# ===================================================================== scene
class TheFastestFall(Base):
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

    # ---------------------------------------------------------------- script
    def construct(self):
        self.camera.background_color = BG
        if not SILENT:
            self.set_speech_service(self.make_service())
        self.build_hud()
        self.act_race()
        self.act_energy()
        self.act_light()
        self.act_wheel()
        self.act_clock()
        self.act_tauto()

    # ================================================================== ACT 1
    def act_race(self):
        self.chapter(0, run_time=0.8)
        ceiling = DashedLine(
            A + LEFT * 0.4,
            A + RIGHT * (BX + 0.9),
            stroke_color=DIM,
            stroke_width=1.5,
            stroke_opacity=0.5,
            dash_length=0.09,
        )
        a_dot = Dot(A, radius=0.06, color=INK)
        a_lab = txt("A", 24, INK, 0.5).next_to(a_dot, UL, buff=0.12)
        b_ring = Circle(radius=0.14, stroke_color=GOLD, stroke_width=3).move_to(B)
        b_lab = txt("B", 24, GOLD, 0.5).next_to(b_ring, UR, buff=0.12)
        line_mob = Line(A, B, stroke_color=BLUE, stroke_width=2.5, stroke_opacity=0.85)
        arc_mob = curve_from(ARC_PTS, MAGENTA, 2.5, 0.85)
        cyc_mob = curve_from(CYC_PTS, GOLD, 4.0)
        self.ceiling, self.a_dot, self.b_ring = ceiling, a_dot, b_ring
        self.line_mob, self.arc_mob, self.cyc_mob = line_mob, arc_mob, cyc_mob

        specs = [
            ("straight line", BLUE, line_mob),
            ("Galileo's arc", MAGENTA, arc_mob),
            ("curve X", GOLD, cyc_mob),
        ]
        rows, self.vals = [], []
        for name, col, _ in specs:
            sw = Square(
                side_length=0.22, fill_color=col, fill_opacity=1, stroke_width=0
            )
            nm = txt(name, 26, INK, 3.2)
            val = txt("—", 28, DIM, 1.6)
            row = VGroup(sw, nm, val).arrange(RIGHT, buff=0.24)
            rows.append(row)
            self.vals.append(val)
        self.rows = rows
        self.stack(rows, top=1.55, buff=0.34)

        clock = ValueTracker(0.0)
        self.race_clock = clock
        c_lab = tex(r"t =", 34, DIM, 0.8)
        c_num = DecimalNumber(0.0, num_decimal_places=2, font_size=40, color=INK)
        c_unit = txt("s", 26, DIM, 0.5)
        c_grp = VGroup(c_lab, c_num, c_unit).arrange(RIGHT, buff=0.18)
        self.stack([c_grp], top=COL_TOP)
        anchor = c_num.get_center().copy()

        def c_up(m):
            m.set_value(clock.get_value())
            m.move_to(anchor)

        c_num.add_updater(c_up)
        c_num.update(0)
        self.clock_grp, self.clock_num = c_grp, c_num

        beads = []
        for (name, col, _), tr in zip(specs, (TR_LINE, TR_ARC, TR_CYC)):
            bead = Dot(A, radius=0.085, color=col)
            bead.add_updater(
                lambda d, tr=tr: d.move_to(track_point(tr, clock.get_value()))
            )
            beads.append(bead)
        self.beads = beads

        note = txt(
            "same gravity · computed, not drawn · shown in slow motion", 18, DIM, 9.0
        ).move_to([STAGE_CX, -3.30, 0])
        self.a_lab, self.b_lab, self.race_note = a_lab, b_lab, note

        with self.voiceover(
            "Three tracks. Same start, same finish, same gravity. A straight "
            "line, the shortest path. A circular arc, Galileo's guess for the "
            "fastest. And one mystery curve."
        ) as tr:
            d = tr.duration
            self.play(
                Create(ceiling),
                FadeIn(a_dot),
                FadeIn(a_lab),
                FadeIn(b_ring),
                FadeIn(b_lab),
                run_time=d * 0.18,
            )
            self.play(Create(line_mob), FadeIn(rows[0]), run_time=d * 0.24)
            self.play(Create(arc_mob), FadeIn(rows[1]), run_time=d * 0.24)
            self.play(Create(cyc_mob), FadeIn(rows[2]), run_time=d * 0.24)
            self.rest(tr)

        with self.voiceover(
            "Release them all, now. The line is nowhere. Galileo's arc pushes "
            "hard, and still loses by six hundredths of a second. The shortest "
            "path is not the fastest. So what is curve X?"
        ) as tr:
            d = tr.duration
            self.play(
                FadeIn(c_grp), FadeIn(note), *[FadeIn(b) for b in beads], run_time=0.6
            )
            count = txt("3", 84, GOLD, 1.2, weight=BOLD).move_to([STAGE_CX, 1.35, 0])
            self.play(FadeIn(count, scale=0.7), run_time=0.4)
            for s in ("2", "1"):
                nxt = txt(s, 84, GOLD, 1.2, weight=BOLD).move_to(count.get_center())
                self.play(ReplacementTransform(count, nxt), run_time=0.4)
                count = nxt
            self.play(FadeOut(count), run_time=0.25)
            race_rt = max(4.6, d * 0.62)
            self.play(
                clock.animate.set_value(T_LINE), run_time=race_rt, rate_func=linear
            )
            for b in beads:
                b.clear_updaters()
            c_num.clear_updaters()
            for i, T in ((2, T_CYC), (1, T_ARC), (0, T_LINE)):
                col = specs[i][1]
                v = txt(f"{T:.2f} s", 28, col, 1.6).move_to(self.vals[i])
                self.play(
                    ReplacementTransform(self.vals[i], v),
                    Indicate(rows[i], color=col, scale_factor=1.06),
                    run_time=0.45,
                )
                self.vals[i] = v
            self.play(
                Flash(
                    b_ring, color=GOLD, line_length=0.28, num_lines=16, flash_radius=0.6
                ),
                run_time=0.6,
            )
            self.rest(tr)
        self.winner_box = SurroundingRectangle(
            rows[2], color=GOLD, buff=0.14, stroke_width=2.2, stroke_opacity=0.9
        )
        self.play(Create(self.winner_box), run_time=0.5)
        self.wait(0.4)

    # ================================================================== ACT 2
    def act_energy(self):
        self.chapter(1)
        self.play(
            FadeOut(
                VGroup(self.clock_grp, *self.rows, self.winner_box, self.race_note)
            ),
            *[FadeOut(b) for b in self.beads],
            self.line_mob.animate.set_stroke(opacity=0.18),
            self.arc_mob.animate.set_stroke(opacity=0.18),
            run_time=0.8,
        )

        head = txt("ONE RULE", 28, GOLD, COL_W, weight=BOLD)
        rule = tex(r"v = \sqrt{2\,g\,y}", 46, INK, COL_W)
        n1 = body(
            "Speed is bought with height lost. The path never enters the equation."
        )
        n2 = body(
            "Dive early: bank speed for later. Dive too deep: waste it climbing back."
        )
        n3 = body(
            "1696: Bernoulli challenges Europe. Newton answers in one night.", color=DIM
        )
        self.stack([head, rule, n1, n2, n3], buff=0.32)

        th = ValueTracker(0.02)
        bead = Dot(cyc_point(0.02), radius=0.085, color=GOLD)
        bead.add_updater(lambda d: d.move_to(cyc_point(th.get_value())))
        ruler = Line(A, A, stroke_color=DIM, stroke_width=1.5, stroke_opacity=0.7)
        ruler.add_updater(
            lambda m: m.put_start_and_end_on(
                [cyc_point(th.get_value())[0], A[1], 0], cyc_point(th.get_value())
            )
        )
        y_lab = tex("y", 30, DIM, 0.5)
        y_lab.add_updater(
            lambda m: m.move_to(
                0.5
                * (
                    np.array([cyc_point(th.get_value())[0], A[1], 0])
                    + cyc_point(th.get_value())
                )
                + RIGHT * 0.24
            )
        )
        VS = 0.11
        varrow = Arrow(
            cyc_point(0.02),
            cyc_point(0.02) + DOWN * 0.1,
            buff=0,
            stroke_width=5,
            color=CYAN,
            max_tip_length_to_length_ratio=0.2,
        )

        def v_up(a):
            t = th.get_value()
            v = 2 * np.sqrt(G * R) * np.sin(t / 2)
            a.put_start_and_end_on(cyc_point(t), cyc_point(t) + VS * v * cyc_tangent(t))

        varrow.add_updater(v_up)
        v_lab = tex(r"v =", 30, CYAN, 0.8)
        v_num = DecimalNumber(0.0, num_decimal_places=2, font_size=34, color=CYAN)
        v_grp = VGroup(v_lab, v_num).arrange(RIGHT, buff=0.16)
        v_grp.move_to([STAGE_CX, -3.25, 0])
        v_anchor = v_num.get_center().copy()

        def vn_up(m):
            m.set_value(2 * np.sqrt(G * R) * np.sin(th.get_value() / 2))
            m.move_to(v_anchor)

        v_num.add_updater(vn_up)
        v_num.update(0)

        with self.voiceover(
            "Here is the only rule the beads obey. Speed comes from height "
            "lost: v equals root two g y. The path never enters the equation. "
            "So the game is a trade. Dive early, and you bank speed for later. "
            "Dive too deep, and you waste it climbing back. In sixteen ninety "
            "six, Johann Bernoulli dared Europe to find the perfect trade. "
            "Newton solved it in a single night."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(head), Write(rule), run_time=d * 0.14)
            self.play(
                FadeIn(bead),
                FadeIn(ruler),
                FadeIn(y_lab),
                FadeIn(varrow),
                FadeIn(v_grp),
                FadeIn(n1),
                run_time=d * 0.12,
            )
            self.play(th.animate.set_value(TH_B), run_time=d * 0.42, rate_func=linear)
            self.play(FadeIn(n2), run_time=d * 0.10)
            self.play(FadeIn(n3), run_time=d * 0.10)
            self.rest(tr)
        for m in (bead, ruler, y_lab, varrow, v_num):
            m.clear_updaters()
        self.play(
            FadeOut(VGroup(head, rule, n1, n2, n3, bead, ruler, y_lab, varrow, v_grp)),
            run_time=0.8,
        )

    # ================================================================== ACT 3
    def act_light(self):
        self.chapter(2)
        head = txt("LIGHT KNOWS THE WAY", 28, GOLD, COL_W, weight=BOLD)
        snell = tex(r"\frac{\sin\theta}{v} = \text{const}", 42, CYAN, COL_W)
        n1 = body("Each layer is faster, because speed grows with the drop.")
        limit = tex(r"\frac{\sin\alpha}{\sqrt{y}} = \text{const}", 40, ACID, COL_W)
        n2 = body(
            "At the bottom the ray turns horizontal, then mirrors back up to B.",
            color=DIM,
        )
        self.stack([head, snell, n1, limit, n2], buff=0.32)

        self.play(
            FadeOut(self.line_mob),
            FadeOut(self.arc_mob),
            self.cyc_mob.animate.set_stroke(opacity=0.30),
            FadeIn(head),
            Write(snell),
            run_time=1.0,
        )

        def bands(n):
            ys = np.linspace(0, DIP_D, n + 1)
            g = VGroup()
            for i in range(n):
                h = ys[i + 1] - ys[i]
                g.add(
                    Rectangle(
                        width=7.8,
                        height=h,
                        stroke_width=0,
                        fill_color=BLUE,
                        fill_opacity=0.045 + 0.10 * (i + 1) / n,
                    ).move_to([STAGE_CX, A[1] - 0.5 * (ys[i] + ys[i + 1]), 0])
                )
            return g

        def chip(n, err):
            return txt(f"{n} layers · max gap {err:.3f}", 20, DIM, 5.0).move_to(
                [STAGE_CX, -3.25, 0]
            )

        ns = [2, 4, 8, 16, 64]
        p0, _, e0 = snell_ray(ns[0])
        cur_bands = bands(ns[0])
        ray = VMobject(stroke_color=CYAN, stroke_width=3.5)
        ray.set_points_as_corners(resample(p0))
        cur_chip = chip(ns[0], e0)

        with self.voiceover(
            "Bernoulli's trick is the beautiful part. Light already solves "
            "this problem. Crossing into a faster medium, light bends so that "
            "sine theta over speed stays constant. Snell's law. So build the "
            "fall out of layers, each faster than the last, and let light "
            "pick the route. Two layers: crude. Four: better. Sixteen: nearly "
            "smooth. In the limit, the fastest route keeps sine alpha over "
            "root drop constant. We need a curve that does this exactly."
        ) as tr:
            d = tr.duration
            self.play(
                FadeIn(cur_bands),
                FadeIn(ray),
                FadeIn(cur_chip),
                FadeIn(n1),
                run_time=d * 0.22,
            )
            per = d * 0.13
            for n in ns[1:]:
                pts, _, err = snell_ray(n)
                nb = bands(n)
                nr = VMobject(stroke_color=CYAN, stroke_width=3.5)
                nr.set_points_as_corners(resample(pts))
                nc = chip(n, err)
                self.play(
                    FadeOut(cur_bands),
                    FadeIn(nb),
                    ReplacementTransform(ray, nr),
                    ReplacementTransform(cur_chip, nc),
                    run_time=per,
                )
                cur_bands, ray, cur_chip = nb, nr, nc
            dash = curve_from(CYC_PTS[: M // 2 + 1], GOLD, 3.0, 0.9)
            self.play(Create(dash), Write(limit), run_time=d * 0.14)
            up_half = curve_from(CYC_PTS[M // 2 :], GOLD, 3.0, 0.55)
            self.play(Create(up_half), FadeIn(n2), run_time=d * 0.12)
            self.rest(tr)
        self.play(
            FadeOut(
                VGroup(
                    cur_bands, ray, cur_chip, dash, up_half, head, snell, n1, limit, n2
                )
            ),
            run_time=0.8,
        )

    # ================================================================== ACT 4
    def act_wheel(self):
        self.chapter(3)
        th = ValueTracker(0.0)
        self.wth = th
        O = lambda: A + np.array([R * th.get_value(), -R, 0.0])
        P = lambda: cyc_point(th.get_value())

        wheel = Circle(
            radius=R, stroke_color=DIM, stroke_width=2, stroke_opacity=0.8
        ).move_to(O())
        wheel.add_updater(lambda m: m.move_to(O()))
        spokes = VGroup()
        for j in range(3):
            sp = Line(O(), O(), stroke_color=DIM, stroke_width=1.2, stroke_opacity=0.4)
            sp.add_updater(
                lambda m, j=j: m.put_start_and_end_on(
                    O()
                    + R
                    * np.array(
                        [
                            np.cos(PI / 2 + th.get_value() + j * TAU / 3),
                            np.sin(PI / 2 + th.get_value() + j * TAU / 3),
                            0,
                        ]
                    ),
                    O()
                    - R
                    * np.array(
                        [
                            np.cos(PI / 2 + th.get_value() + j * TAU / 3),
                            np.sin(PI / 2 + th.get_value() + j * TAU / 3),
                            0,
                        ]
                    ),
                )
            )
            spokes.add(sp)
        radius = Line(O(), P(), stroke_color=GOLD, stroke_width=2.5)
        radius.add_updater(lambda m: m.put_start_and_end_on(O(), P()))
        contact = Dot(O() + UP * R, radius=0.045, color=INK)
        contact.add_updater(lambda d: d.move_to(O() + UP * R))
        pdot = Dot(P(), radius=0.07, color=GOLD)
        pdot.add_updater(lambda d: d.move_to(P()))
        trace = TracedPath(P, stroke_color=GOLD, stroke_width=4.2)
        wheel_grp = VGroup(wheel, spokes, radius, contact, pdot)

        head = txt("THE WHEEL", 28, GOLD, COL_W, weight=BOLD)
        e1 = tex(
            r"\alpha = \tfrac{\theta}{2},\quad \sin\alpha = \sin\tfrac{\theta}{2}",
            34,
            CYAN,
            COL_W,
        )
        e2 = tex(r"y = 2R\sin^{2}\tfrac{\theta}{2}", 34, DIM, COL_W)
        e3 = tex(r"v = 2\sqrt{gR}\,\sin\tfrac{\theta}{2}", 34, GOLD, COL_W)
        e4 = tex(r"\frac{\sin\alpha}{v} = \frac{1}{2\sqrt{gR}}", 40, ACID, COL_W)
        n1 = body("The sines cancel. Snell's law holds exactly, at every point.")
        self.stack([head, e1, e2, e3, e4, n1], buff=0.30)

        with self.voiceover(
            "Roll a circle under the ceiling and watch one point on its rim. "
            "It draws a cycloid. Curve X. Here is the picture that proves "
            "everything. The tangent always points at the bottom of the "
            "wheel, and its angle from vertical is exactly half the rolling "
            "angle."
        ) as tr:
            d = tr.duration
            self.play(
                FadeOut(self.cyc_mob), FadeIn(wheel_grp), FadeIn(head), run_time=0.8
            )
            self.add(trace)
            self.play(
                th.animate.set_value(2.0), run_time=max(3.0, d * 0.75), rate_func=linear
            )
            self.rest(tr)

        # static proof markers at theta* = 2.0 (no updaters needed)
        ts = 2.0
        Ps, Os = cyc_point(ts), A + np.array([R * ts, -R, 0.0])
        Tc = Os + np.array([0, R, 0])
        Bo = Os + np.array([0, -R, 0])
        t_hat = cyc_tangent(ts)
        chord = Line(Ps, Tc, stroke_color=INK, stroke_width=1.6, stroke_opacity=0.75)
        tangent = Line(
            Ps - 1.25 * t_hat, Ps + 1.25 * t_hat, stroke_color=ACID, stroke_width=3
        )
        vert = DashedLine(
            Ps, Ps + DOWN * 1.1, stroke_color=DIM, stroke_width=1.5, dash_length=0.07
        )
        alpha_arc = Arc(
            radius=0.5,
            start_angle=-PI / 2,
            angle=ts / 2,
            arc_center=Ps,
            stroke_color=ACID,
            stroke_width=3,
        )
        a_lab = tex(r"\alpha=\tfrac{\theta}{2}", 28, ACID, 1.6).move_to(
            Ps + np.array([0.30, -1.10, 0.0])
        )  # outside the rim
        u1 = (Tc - Ps) / np.linalg.norm(Tc - Ps)
        u2 = (Bo - Ps) / np.linalg.norm(Bo - Ps)
        eps = 0.18
        ra = VMobject(stroke_color=INK, stroke_width=2)
        ra.set_points_as_corners([Ps + eps * u1, Ps + eps * (u1 + u2), Ps + eps * u2])
        bo_dot = Dot(Bo, radius=0.05, color=ACID)
        markers = VGroup(chord, tangent, vert, alpha_arc, a_lab, ra, bo_dot)

        with self.voiceover(
            "So sine alpha is sine theta over two. The drop is two R sine "
            "squared theta over two, so the speed is two root g R, sine theta "
            "over two. Divide them: the sines cancel. The cycloid is the "
            "light ray. The picture is the proof."
        ) as tr:
            d = tr.duration
            self.play(
                wheel.animate.set_stroke(opacity=0.30),
                Create(chord),
                Create(tangent),
                Create(vert),
                FadeIn(bo_dot),
                Create(ra),
                run_time=d * 0.20,
            )
            self.play(Create(alpha_arc), FadeIn(a_lab), Write(e1), run_time=d * 0.18)
            self.play(Write(e2), run_time=d * 0.14)
            self.play(Write(e3), run_time=d * 0.14)
            self.play(Write(e4), FadeIn(n1), run_time=d * 0.20)
            self.rest(tr)

        with self.voiceover("Keep rolling, and the wheel signs its name.") as tr:
            self.play(
                FadeOut(markers), wheel.animate.set_stroke(opacity=0.8), run_time=0.5
            )
            self.play(
                th.animate.set_value(TH_B),
                run_time=max(2.0, tr.duration * 0.8),
                rate_func=linear,
            )
            self.rest(tr)
        name = txt("THE CYCLOID", 40, INK, 8.0, weight=BOLD).move_to([0, 3.24, 0])
        name.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        self.play(FadeIn(name, shift=UP * 0.12), run_time=0.8)
        self.wait(0.6)
        for m in (wheel, contact, pdot, radius, *spokes):
            m.clear_updaters()
        trace.clear_updaters()
        self.curve = trace
        self.play(
            FadeOut(wheel_grp),
            FadeOut(VGroup(head, e1, e2, e3, e4, n1)),
            FadeOut(name),
            run_time=0.9,
        )

    # ================================================================== ACT 5
    def act_clock(self):
        self.chapter(4)
        head = txt("THE CLOCK", 28, GOLD, COL_W, weight=BOLD)
        hero = tex(r"dt = \frac{ds}{v} = \sqrt{\tfrac{R}{g}}\;d\theta", 44, ACID, COL_W)
        n1 = body("Time is the rolling angle. The wheel ticks uniformly.")
        self.stack([head, hero, n1], buff=0.32)
        recap_top = n1.get_bottom()[1] - 0.42

        recap = []
        for name, col, T in (
            ("cycloid", GOLD, T_CYC),
            ("arc", MAGENTA, T_ARC),
            ("line", BLUE, T_LINE),
        ):
            sw = Square(
                side_length=0.22, fill_color=col, fill_opacity=1, stroke_width=0
            )
            nm = txt(name, 25, INK, 2.0)
            tm = txt(f"{T:.2f} s", 27, col, 1.5)
            dl = txt(
                "winner" if T == T_CYC else f"+{T - T_CYC:.2f} s",
                22,
                ACID if T == T_CYC else DIM,
                1.7,
            )
            recap.append(VGroup(sw, nm, tm, dl).arrange(RIGHT, buff=0.20))

        hline = DashedLine(
            [BOT[0] - 1.2, B[1], 0],
            [B[0] + 0.7, B[1], 0],
            stroke_color=DIM,
            stroke_width=1.5,
            dash_length=0.08,
        )
        band = Rectangle(
            width=3.6,
            height=DIP_D - BY,
            stroke_width=0,
            fill_color=MAGENTA,
            fill_opacity=0.10,
        ).move_to([0.5 * (BOT[0] + B[0]), B[1] - (DIP_D - BY) / 2, 0])
        dip_arrow = DoubleArrow(
            [BOT[0], B[1], 0],
            [BOT[0], BOT[1], 0],
            buff=0,
            stroke_width=3,
            color=GOLD,
            max_tip_length_to_length_ratio=0.12,
        )
        dip_lab = txt(f"{DIP_D - BY:.2f} below", 22, GOLD, 2.2).move_to(
            [BOT[0], BOT[1] - 0.42, 0]
        )  # below the lowest point
        n2 = body(
            "The fastest path dives below the finish. Depth buys speed.", color=GOLD
        )
        self.stack(recap + [n2], top=recap_top, buff=0.30)

        with self.voiceover(
            "And the cancellation pays a bonus. Distance over speed: the "
            "sines cancel again, leaving d t equals root R over g, d theta. "
            "Time is the rolling angle. The wheel is a clock. Final times, "
            "computed. And notice: the winner dives below the finish line, "
            "and climbs back. Depth buys speed."
        ) as tr:
            d = tr.duration
            self.play(FadeIn(head), Write(hero), run_time=d * 0.22)
            self.play(FadeIn(n1), run_time=d * 0.12)
            self.play(
                *[FadeIn(r, shift=RIGHT * 0.15) for r in recap], run_time=d * 0.20
            )
            self.play(Create(hline), FadeIn(band), run_time=d * 0.12)
            self.play(Create(dip_arrow), FadeIn(dip_lab), FadeIn(n2), run_time=d * 0.18)
            self.rest(tr)
        self.play(
            FadeOut(
                VGroup(head, hero, n1, *recap, hline, band, dip_arrow, dip_lab, n2)
            ),
            run_time=0.8,
        )

    # ================================================================== ACT 6
    def act_tauto(self):
        self.chapter(5)
        head = txt("SAME ARRIVAL", 28, GOLD, COL_W, weight=BOLD)
        eq = tex(r"T = \pi\sqrt{\tfrac{R}{g}}", 46, ACID, COL_W)
        val = txt(f"= {T_TAU:.2f} s — from every start", 26, INK, COL_W)
        n1 = body("Huygens' tautochrone: the equal-time curve.")
        n2 = body(
            "The fastest curve and the equal-time curve are the same curve.", color=GOLD
        )
        self.stack([head, eq, val, n1, n2], buff=0.32)

        clk = ValueTracker(0.0)
        bottom_dot = Dot(BOT, radius=0.06, color=INK)
        beads, rings = VGroup(), VGroup()
        for th0, col in zip(TH0S, TAU_COLS):
            p0 = cyc_point(th0)
            rings.add(
                Circle(
                    radius=0.12, stroke_color=col, stroke_width=2, stroke_opacity=0.6
                ).move_to(p0)
            )
            bead = Dot(p0, radius=0.065, color=col)
            u0 = np.cos(th0 / 2)

            def up(d, u0=u0):
                t = clk.get_value()
                theta = (
                    PI
                    if t >= T_TAU
                    else 2 * np.arccos(np.clip(u0 * np.cos(OMEGA * t), -1.0, 1.0))
                )
                d.move_to(cyc_point(theta))

            bead.add_updater(up)
            beads.add(bead)

        with self.voiceover(
            "One last secret. Start beads anywhere on this curve. Different "
            "heights, same moment. They arrive together. Every start takes "
            "pi root R over g. The fastest curve is also the equal time "
            "curve: Huygens' tautochrone, hiding in the same cycloid. "
            "Bernoulli found two miracles in one curve."
        ) as tr:
            d = tr.duration
            self.play(
                FadeIn(head),
                FadeIn(bottom_dot),
                FadeIn(rings),
                FadeIn(beads),
                run_time=d * 0.16,
            )
            self.play(Write(eq), FadeIn(val), run_time=d * 0.14)
            self.play(
                clk.animate.set_value(T_TAU),
                run_time=T_TAU * TAU_SLOW,
                rate_func=linear,
            )
            for b in beads:
                b.clear_updaters()
            self.play(
                Flash(
                    bottom_dot,
                    color=ACID,
                    line_length=0.32,
                    num_lines=20,
                    flash_radius=0.8,
                ),
                FadeIn(n1),
                run_time=0.8,
            )
            self.play(FadeIn(n2), run_time=d * 0.12)
            self.rest(tr)

        card1 = tex(
            r"\text{brachistochrone} \;=\; \text{tautochrone}", 40, GOLD, 9.0
        ).move_to([0, 1.10, 0])
        card2 = txt("one curve: the cycloid", 30, INK, 8.0).move_to([0, 0.15, 0])
        tag = txt("THE WHEEL IS THE CLOCK", 32, INK, 9.0, weight=BOLD).move_to(
            [0, -1.10, 0]
        )
        tag.set_color_by_gradient(GOLD, MAGENTA, CYAN)
        with self.voiceover("The wheel was the clock all along.") as tr:
            self.play(
                FadeOut(
                    VGroup(
                        head,
                        eq,
                        val,
                        n1,
                        n2,
                        beads,
                        rings,
                        bottom_dot,
                        self.ceiling,
                        self.a_dot,
                        self.a_lab,
                        self.b_ring,
                        self.b_lab,
                        self.curve,
                    )
                ),
                run_time=0.9,
            )
            self.play(Write(card1), run_time=1.1)
            self.play(FadeIn(card2), FadeIn(tag, shift=UP * 0.15), run_time=1.1)
            self.rest(tr)
        self.wait(1.6)
        self.play(self.prog.animate.set_value(1.0), run_time=1.0)
        self.rail_fill.clear_updaters()
        self.play(FadeOut(VGroup(card1, card2, tag, self._chap)), run_time=1.4)
        self.wait(0.5)
