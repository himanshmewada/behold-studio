"""
thumbnail_heart.py — YouTube thumbnails, 1280x720, computed not drawn.

    manim -s thumbnail_heart.py ThumbnailHeart        # recommended
    manim -s thumbnail_heart.py ThumbnailStraight     # the surprise angle
    manim -s thumbnail_heart.py ThumbnailQuestion     # browse/suggested angle
    manim -s thumbnail_heart.py "*"                   # all three

PNGs land under media/images/. PREVIEW = True renders 320x180 so you can check
feed-size legibility. Use -s, not -p/-q: these scenes have no animations.

THE PICTURE IS THE REAL CONSTRUCTION
------------------------------------
Every chord joins point k to point 2k (mod N) on a circle. Every chord is a
straight Line. Their envelope is the cardioid E(t) = (2e^{it} + e^{2it})/3.

Orientation: the cusp sits at k = 0. Rotating by +90deg puts the cusp at the
top, which is the orientation that reads as a heart. Same curve, turned.

Framing: the cardioid's bounding box is NOT centred on the generating circle.
Re(E) ranges over [-1/2, 1], so after the rotation the shape's vertical centre
sits 0.25R above the circle's centre. The code subtracts that offset so the
heart is optically centred rather than the ring.

N = 200 gives a smooth heart; N = 60 keeps the individual straight chords
visible, which is the point of ThumbnailStraight.
"""

import numpy as np
from manim import *

# ------------------------------------------------------------------- canvas
PREVIEW = False
config.pixel_width = 320 if PREVIEW else 1280
config.pixel_height = 180 if PREVIEW else 720
config.frame_width = 16
config.frame_height = 9
config.frame_rate = 30

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

LEFT_X = -7.30
ROT = PI / 2  # cusp to the top: the heart orientation
CHORD_W = 2.4


# ------------------------------------------------------------------ helpers
def P3(p):
    """Accept (x, y) or (x, y, z); always hand manim a 3-vector."""
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
    """Width clamp without deprecated setters."""
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def lerp_hex(h1, h2, t):
    a = np.array([int(h1[i : i + 2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i : i + 2], 16) for i in (1, 3, 5)], float)
    return "#%02x%02x%02x" % tuple(np.round(a + (b - a) * t).astype(int))


def ramp_at(u, ramp=CHORD):
    x = float(np.clip(u, 0, 1)) * (len(ramp) - 1)
    i = min(int(np.floor(x)), len(ramp) - 2)
    return lerp_hex(ramp[i], ramp[i + 1], x - i)


def tracked(s, size, color, tracking=0.10, weight=NORMAL, space=0.30):
    """Letterspaced caps on a shared centre line."""
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


def pill(s, size=26, color=ACID, tracking=0.11):
    t = tracked(s, size, color, tracking, weight=BOLD)
    box = RoundedRectangle(
        corner_radius=0.16,
        width=t.width + 0.60,
        height=t.height + 0.36,
        stroke_color=color,
        stroke_width=1.8,
        stroke_opacity=0.85,
        fill_color=color,
        fill_opacity=0.12,
    )
    t.move_to(box.get_center())
    return VGroup(box, t)


def stack(mobs, top, x=LEFT_X, buff=0.30):
    """Left-aligned column from real heights. Rows cannot collide."""
    y = top
    for m in mobs:
        m.move_to([x, y, 0.0], aligned_edge=UL)
        y -= m.height + buff
    return VGroup(*mobs)


def center_block(mobs, y, x=LEFT_X, buff=0.30):
    total = sum(m.height for m in mobs) + buff * (len(mobs) - 1)
    return stack(mobs, y + total / 2.0, x=x, buff=buff)


def backdrop(scene, glow_at=(3.90, 0.10)):
    c = P3(glow_at)
    bg = Rectangle(width=16.4, height=9.4, stroke_width=0)
    bg.set_fill(color=["#141430", "#05050c"], opacity=1)
    scene.add(bg)

    lattice = VGroup()
    for i in range(-16, 17):
        for j in range(-9, 10):
            p = np.array([i * 0.5, j * 0.5, 0.0])
            if abs(p[0]) < 8.1 and abs(p[1]) < 4.6:
                lattice.add(Dot(p, radius=0.014, color=DIM, fill_opacity=0.13))
    scene.add(lattice)

    halo = VGroup(
        *[
            Circle(radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o).move_to(c)
            for r, o in ((4.4, 0.045), (3.4, 0.05), (2.4, 0.045))
        ]
    )
    scene.add(halo)


# ------------------------------------------------------------------- the mark
def cardioid(target, R, n=200, highlight=(), chord_w=CHORD_W, dots_every=4):
    """Chords k -> 2k (mod n), cusp rotated to the top, heart optically centred."""
    C = P3(target) - np.array([0.0, 0.25 * R, 0.0])  # bbox centre, not ring centre
    ang = lambda k: TAU * k / n + ROT
    pt = lambda k: C + R * np.array([np.cos(ang(k)), np.sin(ang(k)), 0.0])

    ring = Circle(
        radius=R, stroke_color=DIM, stroke_width=1.5, stroke_opacity=0.32
    ).move_to(C)
    glow, chords = VGroup(), VGroup()
    for k in range(1, n):
        hot = k in highlight
        col = GOLD if hot else ramp_at(k / (n - 1))
        w = chord_w * 2.3 if hot else chord_w
        ln = Line(
            pt(k),
            pt(2 * k),
            stroke_color=col,
            stroke_width=w,
            stroke_opacity=1.0 if hot else 0.92,
        )
        glow.add(ln.copy().set_stroke(width=w * 3.6, opacity=0.10))
        chords.add(ln)

    assert len(chords) == n - 1
    assert all(np.linalg.norm(l.get_end() - l.get_start()) > 1e-9 for l in chords), (
        "degenerate chord: k = 0 must stay excluded"
    )
    print(f"  cardioid: {len(chords)} straight chords, n={n}, cusp at top")

    dots = VGroup(
        *[
            Dot(pt(k), radius=0.032, color=ramp_at(k / (n - 1)))
            for k in range(0, n, dots_every)
        ]
    )
    cusp = Dot(pt(0), radius=0.070, color="#ffffff")
    return VGroup(ring, glow, chords, dots, cusp)


def caption(scene, s, target, R, dy=0.55):
    """Sits below the heart's lowest point, clear of the duration stamp."""
    low = P3(target)[1] - 0.25 * R - 0.5 * R  # heart bottom
    t = Text(s, font_size=26, color=DIM)
    t.move_to([P3(target)[0], low - dy, 0.0])
    scene.add(t)
    return t


# ============================================================ 1 · THE HEART
class ThumbnailHeart(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("THE 2 TIMES TABLE", 26, ACID)
        soft = fit(Text("MAKES A", font_size=70, color=DIM), 6.9)
        hero = fit(Text("HEART", font_size=210, color=GOLD, weight=BOLD), 6.9)
        foot = fit(Text("from straight lines only", font_size=36, color=INK), 6.9)
        self.add(center_block([kick, soft, hero, foot], y=0.20, buff=0.30))

        self.add(cardioid((3.90, 0.10), 3.00, n=200))
        caption(self, "200 straight chords", (3.90, 0.10), 3.00)


# ========================================================= 2 · THE SURPRISE
class ThumbnailStraight(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("THE 2 TIMES TABLE", 26, ACID)
        l1 = fit(Text("EVERY LINE", font_size=94, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("IS STRAIGHT", font_size=94, color=CYAN, weight=BOLD), 6.9)
        foot = fit(Text("and yet, a heart.", font_size=42, color=GOLD), 6.9)
        self.add(center_block([kick, l1, l2, foot], y=0.20, buff=0.32))

        # few enough chords that the straightness is unmistakable
        self.add(
            cardioid(
                (3.90, 0.10),
                3.00,
                n=60,
                highlight=(13, 22, 41),
                chord_w=2.8,
                dots_every=2,
            )
        )
        caption(self, "60 straight chords, three picked out", (3.90, 0.10), 3.00)


# ========================================================= 3 · THE QUESTION
class ThumbnailQuestion(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        kick = pill("THE 2 TIMES TABLE", 26, ACID)
        soft = fit(Text("WHY A", font_size=92, color=DIM), 6.9)
        hero = fit(Text("HEART?", font_size=196, color=MAGENTA, weight=BOLD), 6.9)
        foot = fit(Text("wrapped around a circle", font_size=36, color=INK), 6.9)
        self.add(center_block([kick, soft, hero, foot], y=0.20, buff=0.30))

        self.add(cardioid((3.90, 0.10), 3.00, n=200))
        caption(self, "k to 2k, modulo 200", (3.90, 0.10), 3.00)
