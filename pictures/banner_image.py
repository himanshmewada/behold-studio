"""
behold_banner.py — exact channel banner, 2560x1440, computed not drawn.

    manim -s behold_banner.py BeholdBanner        # full-bleed desktop composition
    manim -s behold_banner.py BeholdBannerSafe    # everything inside the mobile strip
    manim -s behold_banner.py BeholdBannerGuides  # desktop + safe-area overlay

PNGs land under media/images/. No voiceover, no animation: -s saves the frame.

WHAT IS ACTUALLY COMPUTED
-------------------------
left mark   cardioid as the envelope of the chords k -> 2k (mod 200) on a circle.
            Every chord is a straight Line. The cusp at angle 0 is real.
right mark  Vogel's model: r = c*sqrt(n), theta = n * 137.5077640 deg.
            The two traced families are seeds k, k+F, k+2F, ... for F = 34 and 55,
            so they contain EXACTLY 34 and 55 spirals (asserted at build time).
centre      nested squares shrinking by sqrt(2)-1 per level: the infinite-descent
            motif from the sqrt(2) video, held at low opacity behind the type.

SAFE AREA
---------
YouTube guarantees only the central 1546 x 423 px of a 2560 x 1440 banner.
At 160 px per scene unit that is x in [-4.83, 4.83], y in [-1.32, 1.32].
The text lockup is built to fit inside that band in BOTH modes; only the two
figures bleed in BeholdBanner. Use BeholdBannerSafe if you want nothing cropped.
"""

import numpy as np
from manim import *

# ------------------------------------------------------------------- canvas
config.pixel_width = 2560
config.pixel_height = 1440
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30

CHANNEL_NAME = "BEHOLD"  # <- change once you've settled on it
TAGLINE = "THE PICTURE IS THE PROOF"
SUBLINE = "RIGOROUS MATH ANIMATION"

# ------------------------------------------------------------------ palette
BG = "#07070f"
INK = "#f1eff9"
DIM = "#8f8bad"
BLUE = "#4d7cff"
CYAN = "#2ee6d6"
MAGENTA = "#ff2d95"
GOLD = "#ffc233"
ACID = "#b6ff3d"
CHORD = ["#2ee6d6", "#3aa0ff", "#4d7cff", "#7c6bff", "#b45cff", "#ff2d95", "#ff5cc8"]
SEED = [
    "#fff3b0",
    "#ffd166",
    "#ffa62b",
    "#ff6b35",
    "#ef476f",
    "#b5179e",
    "#7209b7",
    "#3a86ff",
]

PHI = (1 + np.sqrt(5)) / 2
SHRINK = np.sqrt(2) - 1
PX_UNIT = 2560 / 16  # 160 px per scene unit
SAFE_W = 1546 / PX_UNIT  # 9.6625
SAFE_H = 423 / PX_UNIT  # 2.64375

CHORD_W = 2.4  # nudge if strokes read too thin/thick

MODES = {
    "desktop": dict(
        fig_r=2.60,
        fig_x=5.50,
        name=104,
        tag=44,
        sub=26,
        track=(0.14, 0.06, 0.10),
        text_max=5.40,
        buff=0.26,
    ),
    "safe": dict(
        fig_r=1.15,
        fig_x=3.60,
        name=88,
        tag=34,
        sub=21,
        track=(0.11, 0.04, 0.07),
        text_max=4.40,
        buff=0.20,
    ),
}


# ------------------------------------------------------------------ helpers
def lerp_hex(h1, h2, t):
    a = np.array([int(h1[i : i + 2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i : i + 2], 16) for i in (1, 3, 5)], float)
    return "#%02x%02x%02x" % tuple(np.round(a + (b - a) * t).astype(int))


def ramp_at(u, ramp):
    x = float(np.clip(u, 0, 1)) * (len(ramp) - 1)
    i = min(int(np.floor(x)), len(ramp) - 2)
    return lerp_hex(ramp[i], ramp[i + 1], x - i)


def fit(mob, maxw):
    """Width clamp without deprecated setters."""
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def tracked(s, size, color, tracking, weight=NORMAL, space=0.30):
    """Letterspaced caps, laid out on a shared centre line (no descenders)."""
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


def lockup(mobs, center, buff):
    """Vertical block from real heights, centred as a whole. Rows cannot collide."""
    total = sum(m.height for m in mobs) + buff * (len(mobs) - 1)
    y = center[1] + total / 2.0
    for m in mobs:
        m.move_to([center[0], y - m.height / 2.0, 0.0])
        y -= m.height + buff
    return VGroup(*mobs)


# ------------------------------------------------------------------- marks
def cardioid_mark(center, R, n=200):
    C = np.array(center, float)
    pt = lambda k: C + R * np.array([np.cos(TAU * k / n), np.sin(TAU * k / n), 0.0])

    ring = Circle(
        radius=R, stroke_color=DIM, stroke_width=1.5, stroke_opacity=0.40
    ).move_to(C)
    glow, chords = VGroup(), VGroup()
    for k in range(1, n):
        col = ramp_at(k / (n - 1), CHORD)
        ln = Line(
            pt(k),
            pt(2 * k),
            stroke_color=col,
            stroke_width=CHORD_W,
            stroke_opacity=0.92,
        )
        glow.add(ln.copy().set_stroke(width=CHORD_W * 3.6, opacity=0.09))
        chords.add(ln)
    dots = VGroup(
        *[
            Dot(pt(k), radius=0.030, color=ramp_at(k / (n - 1), CHORD))
            for k in range(0, n, 4)
        ]
    )
    cusp = Dot(pt(0), radius=0.062, color="#ffffff")
    return VGroup(ring, glow, chords, dots, cusp)


def seed_mark(center, R, n=520):
    C = np.array(center, float)
    turns = 1.0 / PHI**2
    c = R / np.sqrt(n - 1)
    dr = 0.40 * c * np.sqrt(PI)

    k = np.arange(n, dtype=float)
    r, a = c * np.sqrt(k), TAU * turns * k
    pts = np.column_stack([C[0] + r * np.cos(a), C[1] + r * np.sin(a), np.zeros(n)])

    fams = VGroup()
    for step, col in ((34, CYAN), (55, MAGENTA)):
        fam = VGroup()
        for j in range(step):
            idx = np.arange(j, n, step)
            if len(idx) < 3:
                continue
            cur = VMobject(stroke_color=col, stroke_width=1.5, stroke_opacity=0.30)
            cur.set_points_smoothly(pts[idx])
            fam.add(cur)
        assert len(fam) == step, f"expected {step} spirals, built {len(fam)}"
        print(f"  parastichy family F={step}: {len(fam)} spirals")
        fams.add(fam)

    dots = VGroup(
        *[
            Dot(pts[i], radius=dr, color=ramp_at(i / (n - 1), SEED), stroke_width=0)
            for i in range(n)
        ]
    )
    ring = Circle(
        radius=R * 1.03, stroke_color=DIM, stroke_width=1.2, stroke_opacity=0.22
    ).move_to(C)
    return VGroup(ring, fams, dots)


def descent_squares(center, side0, levels=6):
    C, s, g = np.array(center, float), side0, VGroup()
    for i in range(levels):
        g.add(
            Square(
                side_length=s,
                stroke_color=BLUE,
                stroke_width=1.4,
                stroke_opacity=max(0.05, 0.13 - 0.012 * i),
                fill_opacity=0,
            ).move_to(C)
        )
        s *= SHRINK
    return g


# ------------------------------------------------------------------- banner
def build_banner(scene, mode):
    m = MODES[mode]
    scene.camera.background_color = BG

    bg = Rectangle(width=16.4, height=9.4, stroke_width=0)
    bg.set_fill(color=["#12122a", "#05050c"], opacity=1)
    scene.add(bg)

    lattice = VGroup()
    for i in range(-16, 17):
        for j in range(-9, 10):
            p = np.array([i * 0.5, j * 0.5, 0.0])
            if abs(p[0]) < 8.1 and abs(p[1]) < 4.6:
                lattice.add(Dot(p, radius=0.012, color=DIM, fill_opacity=0.14))
    scene.add(lattice)

    halos = VGroup()
    for cx in (-m["fig_x"], m["fig_x"]):
        for f, o in ((1.42, 0.030), (1.16, 0.034), (0.92, 0.030)):
            halos.add(
                Circle(
                    radius=m["fig_r"] * f,
                    stroke_width=0,
                    fill_color=BLUE,
                    fill_opacity=o,
                ).move_to([cx, 0, 0])
            )
    scene.add(halos)

    scene.add(descent_squares(ORIGIN, 3.40 if mode == "desktop" else 2.10))

    print(f"[{mode}] building marks")
    left = cardioid_mark([-m["fig_x"], 0.0, 0.0], m["fig_r"])
    right = seed_mark([m["fig_x"], 0.0, 0.0], m["fig_r"])
    scene.add(left, right)

    tn, tt, ts = m["track"]
    name = fit(tracked(CHANNEL_NAME, m["name"], INK, tn, weight=BOLD), m["text_max"])
    rule = Line(
        [-0.9, 0, 0],
        [0.9, 0, 0],
        stroke_color=GOLD,
        stroke_width=2.2,
        stroke_opacity=0.75,
    )
    tag = fit(tracked(TAGLINE, m["tag"], INK, tt), m["text_max"])
    sub = fit(tracked(SUBLINE, m["sub"], DIM, ts), m["text_max"])
    scene.add(lockup([name, rule, tag, sub], np.zeros(3), m["buff"]))


class BeholdBanner(Scene):
    def construct(self):
        build_banner(self, "desktop")


class BeholdBannerSafe(Scene):
    def construct(self):
        build_banner(self, "safe")


class BeholdBannerGuides(Scene):
    def construct(self):
        build_banner(self, "desktop")
        box = DashedVMobject(
            Rectangle(
                width=SAFE_W,
                height=SAFE_H,
                stroke_color=ACID,
                stroke_width=2.4,
                stroke_opacity=0.95,
            ),
            num_dashes=72,
            dashed_ratio=0.5,
        )
        lab = Text(
            "guaranteed visible on every device: 1546 x 423 px",
            font_size=24,
            color=ACID,
        )
        lab.next_to(box, UP, buff=0.16)
        self.add(box, lab)
