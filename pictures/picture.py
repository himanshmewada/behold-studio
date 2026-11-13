"""
brand_avatar.py — exact channel marks, 1024x1024, circular-crop safe.

    manim -s brand_avatar.py BeholdCardioid
    manim -s brand_avatar.py BeholdSeedHead

Writes PNGs to media/images/. Both marks are computed, not drawn:
  cardioid  = envelope of the chords k -> 2k (mod N) on a circle
  seed head = Vogel's model, r = c*sqrt(n), theta = n * 137.5077640 deg
"""

import numpy as np
from manim import *

config.pixel_width = 1024
config.pixel_height = 1024
config.frame_width = 8
config.frame_height = 8

BG = "#07070f"
DIM = "#8f8bad"
RAMP = ["#2ee6d6", "#3aa0ff", "#4d7cff", "#7c6bff", "#b45cff", "#ff2d95", "#ff5cc8"]
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

R = 2.85  # mark radius; 71% of the half-frame, safe inside a circle


def lerp_hex(h1, h2, t):
    a = np.array([int(h1[i : i + 2], 16) for i in (1, 3, 5)], float)
    b = np.array([int(h2[i : i + 2], 16) for i in (1, 3, 5)], float)
    return "#%02x%02x%02x" % tuple(np.round(a + (b - a) * t).astype(int))


def ramp_at(u, ramp):
    x = np.clip(u, 0, 1) * (len(ramp) - 1)
    i = min(int(np.floor(x)), len(ramp) - 2)
    return lerp_hex(ramp[i], ramp[i + 1], x - i)


def backdrop(scene):
    bg = Rectangle(width=8.2, height=8.2, stroke_width=0)
    bg.set_fill(color=["#12122a", "#05050c"], opacity=1)
    halo = VGroup(
        *[
            Circle(radius=r, stroke_width=0, fill_color="#4d7cff", fill_opacity=o)
            for r, o in ((3.6, 0.05), (2.9, 0.05), (2.1, 0.04))
        ]
    )
    scene.add(bg, halo)


class BeholdCardioid(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        N = 200
        pt = lambda k: R * np.array([np.cos(TAU * k / N), np.sin(TAU * k / N), 0.0])

        ring = Circle(radius=R, stroke_color=DIM, stroke_width=1.6, stroke_opacity=0.45)
        glow, chords = VGroup(), VGroup()
        for k in range(1, N):
            col = ramp_at(k / (N - 1), RAMP)
            line = Line(pt(k), pt(2 * k), stroke_color=col, stroke_width=2.4)
            glow.add(line.copy().set_stroke(width=9, opacity=0.10))
            chords.add(line)

        dots = VGroup(
            *[
                Dot(pt(k), radius=0.035, color=ramp_at(k / (N - 1), RAMP))
                for k in range(0, N, 4)
            ]
        )
        cusp = Dot(pt(0), radius=0.075, color="#ffffff")
        self.add(ring, glow, chords, dots, cusp)


class BeholdSeedHead(Scene):
    def construct(self):
        self.camera.background_color = BG
        backdrop(self)

        N = 430
        turns = 1 / (((1 + np.sqrt(5)) / 2) ** 2)  # 0.3819660113 of a turn
        c = R / np.sqrt(N - 1)
        dr = 0.40 * c * np.sqrt(PI)

        dots = VGroup()
        for n in range(N):
            r, a = c * np.sqrt(n), TAU * turns * n
            dots.add(
                Dot(
                    r * np.array([np.cos(a), np.sin(a), 0.0]),
                    radius=dr,
                    color=ramp_at(n / (N - 1), SEED),
                    stroke_width=0,
                )
            )

        # the two parastichy families: exactly 34 and 55 spirals
        pts = np.array([d.get_center() for d in dots])
        for step, col in ((34, "#2ee6d6"), (55, "#ff2d95")):
            for j in range(step):
                idx = np.arange(j, N, step)
                if len(idx) < 3:
                    continue
                curve = VMobject(
                    stroke_color=col, stroke_width=1.4, stroke_opacity=0.30
                )
                curve.set_points_smoothly(pts[idx])
                self.add(curve)

        self.add(dots)
