"""
thumbnail_circles_kiss.py — YouTube thumbnails, 1280x720, computed not drawn.
manim -s pictures/video9_thumbnail.py ThumbnailKiss       # recommended
manim -s pictures/video9_thumbnail.py ThumbnailIntegers   # the surprise
manim -s pictures/video9_thumbnail.py ThumbnailFits       # the question
manim -s pictures/video9_thumbnail.py "*"                 # all three

PNGs land under media/images/. PREVIEW = True renders 320x180 so you can check
feed-size legibility. Use -s, not -p/-q: these scenes have no animations.

THE PICTURE IS THE ACTUAL PACKING
---------------------------------
Same seed and same engine as videos/video9.py. Bends k = 1/r are SIGNED: the
wrapping circle carries k = -1. Seed bends (-1, 2, 2, 3) and bend-centres
w = k*z = (0, -1, 1, 2i) are Gaussian integers, and the flip

    k_new = 2(k1+k2+k3) - k_old
    w_new = 2(w1+w2+w3) - w_old

is pure integer addition. So Descartes' identity is checked EXACTLY (residual
0, not 1e-9) on every quadruple, and every bend in the packing is a whole
number. Only the tangency distances |zi - zj| = |1/ki + 1/kj| are floats.

ThumbnailIntegers labels each circle with its own bend — the numbers you can
read on the picture are the theorem. ThumbnailFits shows both roots of
k4 = 7 +/- 8: the circle of bend 15 in the gap, and the bend -1 wrapper.

Thumbnails carry three or four words; the title carries the search terms.
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

LEFT_X = -7.30
FIG_C = (3.90, 0.10)
FIG_R = 2.95
MIN_R = 0.013  # screen radius below which a circle is sub-pixel

# --------------------------------------------------------------- the packing
DEPTH = 5
K = [-1, 2, 2, 3]
W = [0j, complex(-1, 0), complex(1, 0), complex(0, 2)]
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
SHALLOW = [i for lvl in LEVELS[:3] for i in lvl]
BENDS = sorted({K[i] for i in SHALLOW if K[i] > 0})[:6]
DRAWABLE = [i for i in range(len(K)) if FIG_R / abs(K[i]) >= MIN_R]


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
    assert descartes(K[:4]) == 0 and cdescartes(W[:4]) == 0
    for i in range(len(K)):
        assert isinstance(K[i], int), "every bend must be an integer"
        assert W[i].real == int(W[i].real) and W[i].imag == int(W[i].imag), (
            "every bend-centre must be a Gaussian integer"
        )
    worst = 0.0
    for q in QUADS:
        assert descartes([K[i] for i in q]) == 0, "Descartes must be exact"
        assert cdescartes([W[i] for i in q]) == 0, "complex Descartes must be exact"
        for x in range(4):
            for y in range(x + 1, 4):
                i, j = q[x], q[y]
                worst = max(worst, abs(abs(Z[i] - Z[j]) - abs(1.0 / K[i] + 1.0 / K[j])))
    assert worst < 1e-9, f"tangency drift {worst}"
    a, b, c = K[1], K[2], K[3]
    s, disc = a + b + c, a * b + b * c + c * a
    root = int(round(np.sqrt(disc)))
    assert root * root == disc and s + 2 * root == 15 and s - 2 * root == -1
    assert K[ANS_IDX] == 15 and abs(Z[ANS_IDX] - complex(0, 4 / 15)) < 1e-12
    assert all(k > 0 for k in BENDS)
    print(f"  seed bends {K[:4]} | Descartes residual {descartes(K[:4])} (exact)")
    print(f"  packing: {len(K)} circles, {len(QUADS)} quadruples, depth {DEPTH}")
    print("  every bend integer, every bend-centre Gaussian integer  [exact]")
    print(f"  worst tangency error over all pairs: {worst:.2e}")
    print(
        f"  triple (2,2,3): s={s}, disc={disc} -> bends {s + 2 * root} and {s - 2 * root}"
    )
    print(f"  drawn above one pixel: {len(DRAWABLE)} of {len(K)}")
    print("  bends shown: " + ", ".join(str(b) for b in BENDS))


verify()


# ------------------------------------------------------------------ helpers
def P3(p):
    return np.array([p[0], p[1], 0.0], dtype=float)


def fit(mob, maxw):
    if mob.width > maxw:
        mob.scale(maxw / mob.width)
    return mob


def tracked(s, size, color, tracking=0.10, weight=NORMAL, space=0.30):
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


def chip(mob, color=GOLD, pad=0.20):
    box = RoundedRectangle(
        corner_radius=0.13,
        width=mob.width + 2 * pad,
        height=mob.height + 2 * pad,
        stroke_color=color,
        stroke_width=1.8,
        stroke_opacity=0.9,
        fill_color=BG,
        fill_opacity=0.88,
    )
    box.move_to(mob.get_center())
    return VGroup(box, mob)


def stack(mobs, top, x=LEFT_X, buff=0.30):
    y = top
    for m in mobs:
        m.move_to([x, y, 0.0], aligned_edge=UL)
        y -= m.height + buff
    return VGroup(*mobs)


def center_block(mobs, y, x=LEFT_X, buff=0.30):
    total = sum(m.height for m in mobs) + buff * (len(mobs) - 1)
    return stack(mobs, y + total / 2.0, x=x, buff=buff)


def backdrop(scene, glow_at=FIG_C):
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


# ------------------------------------------------------------------- figures
def mapper(target, R):
    C = P3(target)
    return lambda z: C + R * np.array([z.real, z.imag, 0.0])


def wrapper(target, R, color=INK, dashed=False, width=3.0, opacity=0.85):
    ring = Circle(
        radius=R,
        stroke_color=color,
        stroke_width=width,
        stroke_opacity=opacity,
        fill_color=BLUE,
        fill_opacity=0.06,
    ).move_to(P3(target))
    return DashedVMobject(ring, num_dashes=60, dashed_ratio=0.55) if dashed else ring


def packed(target, R, depth=DEPTH, labels=False):
    """Inner circles only, one hue per generation, plus the labelled wrapper."""
    S = mapper(target, R)
    lvl_of = {i: n for n, lvl in enumerate(LEVELS) for i in lvl}
    body = VGroup()
    for i in range(1, len(K)):
        r = R / abs(K[i])
        if r < MIN_R or lvl_of[i] > depth:
            continue
        n = lvl_of[i]
        col = GOLD if i == ANS_IDX else GEN[min(n, len(GEN) - 1)]
        body.add(
            Circle(
                radius=r,
                stroke_color=col,
                stroke_width=max(0.6, 2.6 - 0.35 * n),
                stroke_opacity=0.92,
                fill_color=col,
                fill_opacity=0.12,
            ).move_to(S(Z[i]))
        )
    out = VGroup(wrapper(target, R), body)
    if not labels:
        return out

    tags = VGroup()
    for i in SHALLOW:
        if K[i] <= 0:
            continue
        r = R / abs(K[i])
        if r < 0.18:
            continue
        fs = int(np.clip(46 * r, 16, 62))
        tags.add(MathTex(str(K[i]), font_size=fs, color=INK).move_to(S(Z[i])))
    return VGroup(out, tags)


def minus_one_tag(target, R, color=DIM):
    """The wrapper's bend, parked outside the disc with a short leader."""
    C = P3(target)
    u = np.array([np.cos(2.356), np.sin(2.356), 0.0])
    ring_pt = C + R * u
    tag = chip(MathTex("-1", font_size=34, color=color), color)
    tag.move_to(C + 1.20 * R * u)
    leader = Line(
        ring_pt + 0.04 * u,
        tag.get_corner(DR) * 0 + tag.get_bottom() + DOWN * 0.02,
        stroke_color=color,
        stroke_width=1.6,
        stroke_opacity=0.7,
    )
    return VGroup(leader, tag)


def gap_region(target, R, idxs=(1, 2, 3), col=MAGENTA):
    """The curvilinear triangle, sampled from the three exact arcs."""
    S = mapper(target, R)
    g = Z[ANS_IDX]
    pts = []
    for n, i in enumerate(idxs):
        j, k = idxs[(n + 1) % 3], idxs[(n + 2) % 3]
        t1, t2 = touch_point(i, j), touch_point(i, k)
        a1, a2 = np.angle(t1 - Z[i]), np.angle(t2 - Z[i])
        sweep = (a2 - a1) % TAU
        r = 1.0 / K[i]
        pa = Z[i] + r * complex(np.cos(a1 + sweep / 2), np.sin(a1 + sweep / 2))
        pb = Z[i] + r * complex(
            np.cos(a1 + (sweep - TAU) / 2), np.sin(a1 + (sweep - TAU) / 2)
        )
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
        fill_opacity=0.22,
    )
    m.set_points_as_corners(pts + [pts[0]])
    return m


def caption(scene, s, dy=-3.30, color=DIM, size=24):
    t = fit(Text(s, font_size=size, color=color), 6.4)
    t.move_to([FIG_C[0], dy, 0.0])
    scene.add(t)
    return t


# ============================================================ 1 · THE KISS
class ThumbnailKiss(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("DESCARTES' THEOREM", 26, ACID)
        l1 = fit(Text("CIRCLES", font_size=140, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("THAT KISS", font_size=140, color=GOLD, weight=BOLD), 6.9)
        foot = fit(
            MathTex(r"(k_1+k_2+k_3+k_4)^2 = 2\sum k_i^2", font_size=36, color=CYAN),
            6.9,
        )
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))
        self.add(packed(FIG_C, FIG_R, depth=DEPTH))
        caption(self, f"{len(K)} circles · every bend a whole number")


# ========================================================= 2 · THE SURPRISE
class ThumbnailIntegers(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("DESCARTES' THEOREM", 26, ACID)
        l1 = fit(Text("ALL WHOLE", font_size=126, color=INK, weight=BOLD), 6.9)
        l2 = fit(Text("NUMBERS", font_size=146, color=GOLD, weight=BOLD), 6.9)
        foot = fit(
            MathTex(
                ",\\ ".join(str(b) for b in BENDS) + r",\ \ldots",
                font_size=40,
                color=CYAN,
            ),
            6.9,
        )
        self.add(center_block([kick, l1, l2, foot], y=0.15, buff=0.28))
        self.add(packed(FIG_C, FIG_R, depth=2, labels=True))
        self.add(minus_one_tag(FIG_C, FIG_R, DIM))
        caption(self, "each circle labelled with its bend, 1/radius")


# ========================================================= 3 · THE QUESTION
class ThumbnailFits(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)
        kick = pill("DESCARTES' THEOREM", 26, ACID)
        soft = fit(Text("WHICH ONE", font_size=88, color=DIM), 6.9)
        hero = fit(Text("FITS?", font_size=190, color=MAGENTA, weight=BOLD), 6.9)
        foot = fit(MathTex(r"k_4 = 7 \pm 8", font_size=48, color=CYAN), 6.9)
        self.add(center_block([kick, soft, hero, foot], y=0.15, buff=0.30))

        S = mapper(FIG_C, FIG_R)
        seeds = VGroup(
            *[
                Circle(
                    radius=FIG_R / abs(K[i]),
                    stroke_color=BLUE,
                    stroke_width=3.0,
                    fill_color=BLUE,
                    fill_opacity=0.14,
                ).move_to(S(Z[i]))
                for i in (1, 2, 3)
            ]
        )
        ans = Circle(
            radius=FIG_R / abs(K[ANS_IDX]),
            stroke_color=GOLD,
            stroke_width=3.0,
            fill_color=GOLD,
            fill_opacity=0.55,
        ).move_to(S(Z[ANS_IDX]))
        self.add(wrapper(FIG_C, FIG_R, CYAN, dashed=True, width=2.6, opacity=0.9))
        self.add(seeds, gap_region(FIG_C, FIG_R), ans)
        self.add(minus_one_tag(FIG_C, FIG_R, CYAN))

        tag = chip(MathTex("15", font_size=30, color=GOLD), GOLD)
        tag.move_to(S(Z[ANS_IDX]) + np.array([1.30, -0.95, 0.0]))
        lead = Line(
            S(Z[ANS_IDX]) + np.array([0.16, -0.12, 0.0]),
            tag.get_corner(UL) + np.array([-0.03, 0.03, 0.0]),
            stroke_color=GOLD,
            stroke_width=1.8,
            stroke_opacity=0.85,
        )
        self.add(lead, tag)
        caption(self, "both roots are real circles", color=INK, size=26)
