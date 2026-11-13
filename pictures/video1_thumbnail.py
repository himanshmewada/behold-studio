"""
thumbnail_odd_square.py — YouTube thumbnails, 1280x720, computed not drawn.

    manim -s thumbnail_odd_square.py ThumbnailProof      # recommended
    manim -s thumbnail_odd_square.py ThumbnailAlgebra    # tutorial flavour
    manim -s thumbnail_odd_square.py ThumbnailPairs      # insight flavour

PNGs land under media/images/. Set PREVIEW = True to render at 320x180 and
check legibility at feed size before committing.

WHY NOT THE FULL TITLE
----------------------
"How to Prove If n is an Odd Integer, Then n² is Odd (Direct Proof)" is 62
characters. At feed size (~168 px wide) that is unreadable mush. The thumbnail
carries 3-4 words; the title carries the search terms. They do different jobs.

THE PICTURES ARE THE ACTUAL PROOF
---------------------------------
ThumbnailProof    (2k+1)^2 dissected into 4k^2 + 2k + 2k + 1. Three even
                  regions and one lone unit cell. Shown at k=3, n=7:
                  36 + 6 + 6 + 1 = 49. The corner cell is the whole argument.
ThumbnailAlgebra  the exact chain from the video, ending at 2m+1.
ThumbnailPairs    7x7 = 49 dots tiled by 24 dominoes with one cell left over.
                  The tiling is constructive, not decorative: rows 0-5 take
                  21 vertical dominoes, the top row minus its corner takes 3
                  horizontal ones. 49 = 2*24 + 1.
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

LEFT_X = -7.30  # strong left edge for all type
K = 3  # the instance drawn: n = 2k+1 = 7


# ------------------------------------------------------------------ helpers
def fit(mob, maxw):
    """Width clamp without deprecated setters."""
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


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


def stack(mobs, top, x=LEFT_X, buff=0.32):
    """Left-aligned column from real heights. Rows cannot collide."""
    y = top
    for m in mobs:
        m.move_to([x, y, 0.0], aligned_edge=UL)
        y -= m.height + buff
    return VGroup(*mobs)


def backdrop(scene, glow_at=(4.30, 0.30)):
    center = np.array([glow_at[0], glow_at[1], 0.0], dtype=float)

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
            Circle(radius=r, stroke_width=0, fill_color=BLUE, fill_opacity=o).move_to(
                center
            )
            for r, o in ((4.2, 0.045), (3.2, 0.05), (2.2, 0.045))
        ]
    )
    scene.add(halo)


def statement(n_part, size, math_color, word_color):
    """`n is ODD` / `n^2 is ODD` with independently coloured parts."""
    m = MathTex(n_part, r"\;\text{is}\;", r"\text{ODD}", font_size=size)
    m[0].set_color(math_color)
    m[1].set_color(DIM)
    m[2].set_color(word_color)
    return m


# ============================================================ 1 · THE PROOF
class ThumbnailProof(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        # ---------------- type column
        kick = pill("DIRECT PROOF", 26, ACID)
        line1 = fit(statement(r"n", 66, CYAN, CYAN), 6.9)
        arrow = Arrow(
            [0, 0, 0],
            [0, -0.72, 0],
            buff=0,
            stroke_width=7,
            color=GOLD,
            max_tip_length_to_length_ratio=0.42,
        )
        hero = fit(statement(r"n^2", 168, INK, GOLD), 6.9)
        foot = MathTex(
            r"n = 2k+1 \;\Longrightarrow\; n^2 = 2m+1", font_size=38, color=DIM
        )
        fit(foot, 6.9)
        self.add(stack([kick, line1, arrow, hero, foot], top=3.62, buff=0.30))

        # ---------------- the dissection: (2k+1)^2 = 4k^2 + 2k + 2k + 1
        C = np.array([4.30, 0.30, 0.0])
        S = 4.40
        n = 2 * K + 1
        u = S / n
        BL = C + np.array([-S / 2, -S / 2, 0.0])
        big = 2 * K * u

        inner = Rectangle(
            width=big,
            height=big,
            stroke_color=BLUE,
            stroke_width=2,
            stroke_opacity=0.75,
            fill_color=BLUE,
            fill_opacity=0.24,
        )
        inner.move_to(BL + np.array([big / 2, big / 2, 0.0]))

        strip_r = Rectangle(
            width=u,
            height=big,
            stroke_color=CYAN,
            stroke_width=2,
            stroke_opacity=0.75,
            fill_color=CYAN,
            fill_opacity=0.20,
        )
        strip_r.move_to(BL + np.array([big + u / 2, big / 2, 0.0]))

        strip_t = Rectangle(
            width=big,
            height=u,
            stroke_color=CYAN,
            stroke_width=2,
            stroke_opacity=0.75,
            fill_color=CYAN,
            fill_opacity=0.20,
        )
        strip_t.move_to(BL + np.array([big / 2, big + u / 2, 0.0]))

        corner_c = BL + np.array([big + u / 2, big + u / 2, 0.0])
        glow = Square(
            side_length=u * 1.9, stroke_width=0, fill_color=GOLD, fill_opacity=0.16
        ).move_to(corner_c)
        corner = Square(
            side_length=u,
            stroke_color=GOLD,
            stroke_width=2.5,
            fill_color=GOLD,
            fill_opacity=1.0,
        ).move_to(corner_c)

        frame = Square(
            side_length=S,
            stroke_color=INK,
            stroke_width=3,
            stroke_opacity=0.55,
            fill_opacity=0,
        ).move_to(C)

        lab_in = MathTex(r"4k^2", font_size=46, color=INK).move_to(inner)
        lab_r = MathTex(r"2k", font_size=32, color=INK).move_to(strip_r)
        lab_t = MathTex(r"2k", font_size=32, color=INK).move_to(strip_t)
        lab_c = MathTex(r"1", font_size=34, color=BG).move_to(corner)

        plus = MathTex(r"+1", font_size=58, color=GOLD)
        plus.move_to(corner_c + np.array([0.0, u / 2 + 0.62, 0.0]))
        tick = Line(
            plus.get_bottom() + DOWN * 0.06,
            corner_c + np.array([0, u / 2 + 0.06, 0]),
            stroke_color=GOLD,
            stroke_width=3,
            stroke_opacity=0.9,
        )

        cap = MathTex(r"(2k+1)^2 = 4k^2 + 4k + 1", font_size=36, color=INK)
        cap.move_to([C[0], C[1] - S / 2 - 0.62, 0.0])
        inst = Text(
            f"shown at k = {K}, n = {n}:  36 + 6 + 6 + 1 = 49", font_size=22, color=DIM
        )
        inst.move_to([C[0], C[1] - S / 2 - 1.16, 0.0])

        self.add(
            glow,
            inner,
            strip_r,
            strip_t,
            corner,
            frame,
            lab_in,
            lab_r,
            lab_t,
            lab_c,
            plus,
            tick,
            cap,
            inst,
        )


# ========================================================== 2 · THE ALGEBRA
class ThumbnailAlgebra(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(0.0, -1.60))

        kick = pill("DIRECT PROOF", 26, ACID).move_to([5.90, 3.55, 0])
        self.add(kick)

        chain = [
            MathTex(r"n = 2k+1", font_size=58, color=CYAN),
            MathTex(r"n^2 = (2k+1)^2", font_size=58, color=INK),
            MathTex(r"= 4k^2 + 4k + 1", font_size=58, color=INK),
            MathTex(r"= 2(2k^2 + 2k) + 1", font_size=58, color=INK),
        ]
        for m in chain:
            fit(m, 9.0)

        hero = MathTex(r"n^2 = 2m", r"+\,1", font_size=132)
        hero[0].set_color(INK)
        hero[1].set_color(ACID)
        fit(hero, 10.5)

        self.add(stack(chain + [hero], top=3.30, buff=0.34))

        box = SurroundingRectangle(
            hero, color=ACID, buff=0.26, stroke_width=3, stroke_opacity=0.9
        )
        note = MathTex(r"m = 2k^2 + 2k \;\text{is an integer}", font_size=34, color=DIM)
        note.move_to([0.0, -3.30, 0.0])
        self.add(box, note)


# ============================================================ 3 · THE PAIRS
class ThumbnailPairs(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self, glow_at=(4.10, 0.20))

        kick = pill("DIRECT PROOF", 26, ACID)
        h1 = fit(statement(r"n^2", 150, INK, GOLD), 6.6)
        h2 = MathTex(r"=", r"2m", r"+\,1", font_size=132)
        h2[0].set_color(DIM)
        h2[1].set_color(CYAN)
        h2[2].set_color(GOLD)
        fit(h2, 6.6)
        foot = Text("pairs, and one left over", font_size=34, color=DIM)
        fit(foot, 6.6)
        self.add(stack([kick, h1, h2, foot], top=3.55, buff=0.32))

        # ---------------- 7x7 dots, 24 dominoes, one cell uncovered
        C = np.array([4.10, 0.20, 0.0])
        n = 2 * K + 1
        p = 0.62
        origin = C - np.array([(n - 1) * p / 2, (n - 1) * p / 2, 0.0])
        pos = lambda i, j: origin + np.array([i * p, j * p, 0.0])

        dominoes = VGroup()
        for i in range(n):  # rows 0..5: vertical pairs
            for j in (0, 2, 4):
                c = (pos(i, j) + pos(i, j + 1)) / 2
                dominoes.add(
                    RoundedRectangle(
                        corner_radius=0.16,
                        width=p * 0.80,
                        height=p * 1.80,
                        stroke_color=CYAN,
                        stroke_width=2,
                        stroke_opacity=0.45,
                        fill_color=CYAN,
                        fill_opacity=0.06,
                    ).move_to(c)
                )
        for i in (0, 2, 4):  # top row minus its corner
            c = (pos(i, n - 1) + pos(i + 1, n - 1)) / 2
            dominoes.add(
                RoundedRectangle(
                    corner_radius=0.16,
                    width=p * 1.80,
                    height=p * 0.80,
                    stroke_color=CYAN,
                    stroke_width=2,
                    stroke_opacity=0.45,
                    fill_color=CYAN,
                    fill_opacity=0.06,
                ).move_to(c)
            )
        assert len(dominoes) == 24, len(dominoes)

        dots = VGroup(
            *[
                Dot(pos(i, j), radius=p * 0.19, color=INK, fill_opacity=0.85)
                for i in range(n)
                for j in range(n)
                if (i, j) != (n - 1, n - 1)
            ]
        )
        lone_c = pos(n - 1, n - 1)
        halo = Circle(
            radius=p * 0.52, stroke_width=0, fill_color=GOLD, fill_opacity=0.20
        ).move_to(lone_c)
        ring = Circle(
            radius=p * 0.38,
            stroke_color=GOLD,
            stroke_width=2.5,
            stroke_opacity=0.9,
            fill_opacity=0,
        ).move_to(lone_c)
        lone = Dot(lone_c, radius=p * 0.26, color=GOLD)

        cap = MathTex(r"49 = 2(24) + 1", font_size=38, color=INK)
        cap.move_to([C[0], C[1] - (n - 1) * p / 2 - 0.80, 0.0])

        self.add(dominoes, dots, halo, ring, lone, cap)
