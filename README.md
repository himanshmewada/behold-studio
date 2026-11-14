# behold-studio

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Manim](https://img.shields.io/badge/manim-0.19%2B-4d7cff)
![Narration](https://img.shields.io/badge/narration-manim--voiceover-ff2d95)
![License](https://img.shields.io/badge/license-MIT-b6ff3d)

**THE PICTURE IS THE PROOF.**

Every film, thumbnail, banner and avatar for the maths channel *BEHOLD*, generated
from code. Nothing here is placed by hand: the cardioid is the envelope of 199 real
chords, the sunflower is Vogel's model, the gasket is Lucas' theorem mod 2, and the
winning slide is a cycloid solved by bisection. Where an identity matters, it is
**asserted at build time** — if the maths drifts, the render fails.



---

## Contents

- [The films](#the-films)
- [The stills](#the-stills)
- [Quick start](#quick-start)
- [Render commands](#render-commands)
- [What is actually computed](#what-is-actually-computed)
- [House rules](#house-rules)
- [Palette](#palette)
- [Project layout](#project-layout)
- [Adding a film](#adding-a-film)
- [Troubleshooting](#troubleshooting)

## The films

| # | File | Scene | Format | Subject |
|---|---|---|---|---|
| 01 | `videos/video1.py` | `Video1` | 16:9 | If *n* is odd then *n²* is odd — direct proof |
| 02 | `videos/video2.py` | `TimesTablesOnACircle` | 16:9 | k ↦ 2k (mod N): straight chords, cardioid envelope |
| 03 | `videos/video3.py` | `TheMostIrrationalNumber` | 1920×1080 | φ, the golden angle, and why sunflowers count in Fibonacci |
| 04 | `videos/video4.py` | `TheSquareThatBreaksAFraction` | 1080×1920 | Tennenbaum's dissection: √2 is irrational, by descent |
| 05 | `videos/video5.py` | `PascalsSecret` | 1080×1920 | Colour the odd entries → Sierpiński, dim = log 3 / log 2 |
| 06 | `videos/video6.py` | `TheFastestFall` | 1920×1080 | Brachistochrone, Snell's law, and Huygens' tautochrone |

Films 02–06 ship with a **silent fallback**: if `manim-voiceover` is missing, a
`_SilentScene` stand-in estimates speech timing from word count (`words / 2.55`) so
the choreography survives intact. Film 01 requires the real voiceover service.

## The stills

| File | Scenes | Output |
|---|---|---|
| `pictures/banner_image.py` | `BeholdBanner`, `BeholdBannerSafe`, `BeholdBannerGuides` | 2560×1440 channel banner |
| `pictures/picture.py` | `BeholdCardioid`, `BeholdSeedHead` | 1024×1024 circular-crop-safe avatars |
| `pictures/video1_thumbnail.py` | `ThumbnailProof`, `ThumbnailAlgebra`, `ThumbnailPairs` | 1280×720 |
| `pictures/video2_thumbnail.py` | `ThumbnailHeart`, `ThumbnailStraight`, `ThumbnailQuestion` | 1280×720 |
| `pictures/video3_thumbnail.py` | `ThumbnailMostIrrational`, `ThumbnailCeiling`, `ThumbnailAllOnes` | 1280×720 |
| `pictures/video4_thumbnail.py` | `ThumbnailSquare`, `ThumbnailDescent`, `ThumbnailNoFraction` | 1080×1920 |
| `pictures/video5_thumbnail.py` | `ThumbnailHidden`, `ThumbnailParity`, `ThumbnailDimension` | 1080×1920 |
| `pictures/video6_thumbnail.py` | `ThumbnailRace`, `ThumbnailDive`, `ThumbnailLight` | 1280×720 |

Every thumbnail file has a `PREVIEW = True` switch that renders at feed size
(320×180, or 540×960 for Shorts) so you can check legibility before committing.
Thumbnails carry three or four words; the title carries the search terms.

**Safe areas.** YouTube guarantees only the central **1546×423 px** of a 2560×1440
banner — `BeholdBannerSafe` fits the entire lockup inside it, `BeholdBannerGuides`
draws the box. Shorts overlays eat the right edge and the bottom ~20%, so all
9:16 type stays above `y = -4.4` and inside `x ∈ [-3.9, 3.9]`.

## Quick start

```bash
git clone https://github.com/himanshmewada/behold-studio.git
cd behold-studio

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install manim "manim-voiceover[gtts]" numpy
```

You also need **ffmpeg** and a **LaTeX** distribution (TeX Live / MiKTeX) on `PATH` —
`MathTex` will not compile without one.

```bash
# macOS
brew install ffmpeg py3cairo pango
brew install --cask mactex-no-gui

# Debian / Ubuntu
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev texlive-full
```

gTTS needs internet. Films 03–06 set `TRANSCRIPTION_MODEL = None`, so no Whisper
weights are downloaded; film 02 uses `"base"` for bookmark-accurate syncing.

## Render commands

> Docstrings inside the files still reference their original working filenames
> (`behold_banner.py`, `golden.py`, `pascal_secret.py`, …). Use the **paths below**,
> which match the repository.

```bash
# ── stills: -s saves the last frame as PNG into media/images/ ─────────────
manim -s pictures/banner_image.py BeholdBannerSafe
manim -s pictures/picture.py BeholdSeedHead
manim -s pictures/video2_thumbnail.py ThumbnailHeart
manim -s pictures/video5_thumbnail.py "*"        # all three variants

# ── films: preview first, then the real thing ────────────────────────────
manim -pql videos/video2.py TimesTablesOnACircle          # 480p15 draft
manim -qh  videos/video3.py TheMostIrrationalNumber       # 1080p + narration
manim -qh  videos/video4.py TheSquareThatBreaksAFraction  # 9:16 Short
manim -qh  videos/video5.py PascalsSecret
manim -qh  videos/video6.py TheFastestFall
```

Films write to `media/videos/<file>/<quality>/`, stills to `media/images/`.
Set `PREVIEW = True` at the top of a film for an 854×480 (or 540×960) draft, and
`USE_VOICEOVER = False` for a paced silent cut with identical choreography.

## What is actually computed

| Figure | Construction | Asserted |
|---|---|---|
| Cardioid | chords `k → 2k (mod N)`; envelope `E(t) = (2e^{it} + e^{2it})/3` | every chord non-degenerate; `N−1` chords |
| Seed head | Vogel: `r = c√n`, `θ = n · 137.5077640°` | parastichy families contain **exactly 34 and 55** spirals |
| Hurwitz chart | `\|x − p/q\|·q²` for convergents of φ, √2, π | φ never dips below `1/√5`; π dives at 355/113 |
| Tennenbaum | `b = a/√2`, overlap `2b−a`, gaps `a−b` | `2b² = a²`, `(2b−a)² = 2(a−b)²`, ratio `√2−1` |
| Pascal gasket | cell lit iff `(k AND n) == k` | cross-checked against `math.comb`; row counts `2^popcount(n)`; blocks `3^m`; thirds **243/243/243** |
| Brachistochrone | θ_B by bisection on `(θ−sinθ)/(1−cosθ) = bx/by` | Snell invariant exact to 1e-12; Thales tangent property; `T_cyc < T_arc < T_line`; tautochrone `π√(R/g)` from every start |
| Odd square | `(2k+1)² = 4k² + 2k + 2k + 1` | 7×7 tiled by **24** dominoes, one cell left over |

Run any file and these checks print to the console before a single frame is written.

## House rules

These are the constraints the later films were rewritten around. Follow them and
the layout defects do not come back.

1. **One layout primitive.** `stack()` advances a cursor by each mobject's *real*
   height plus a buffer. Never mix a centre-anchored `move_to` with a top-anchored
   stack in the same region — that is what collided.
2. **Wrap, never shrink.** Long copy goes through `wrap()`; `fit()` is a width clamp
   of last resort, not a typesetting strategy.
3. **`\tfrac` inline, `\cfrac` on display.** Stacked rows must not inherit display
   fraction height.
4. **One `.animate` chain per mobject per `play()`.**
5. **Clear updaters before any `FadeOut`.** Pre-sync `DecimalNumber` with `.update(0)`
   and rebuild it only when the value changes, or it resizes mid-fade.
6. **Own row per band.** HUD chip on `HUD_Y`, act titles on `TITLE_Y`, progress rail
   on `RAIL_Y`. They can never share a band.
7. **Every phase clears the previous phase's panel.**
8. **Recolour only what carries the meaning.** In the gasket finale, only *odd* cells
   take a hue — painting the even cells fills the holes and destroys the fractal.
9. No `set_width` / `set_height` kwargs; use `.scale()`.

## Palette

Shared across every film and still, so a thumbnail and its film read as one object.

| Token | Hex | Role |
|---|---|---|
| `BG` | `#07070f` | ink-violet night |
| `SURFACE` / `EDGE` | `#15152a` / `#2b2b48` | panels, rules |
| `INK` / `DIM` | `#f1eff9` / `#8f8bad` | type, captions |
| `BLUE` | `#4d7cff` | structure, the a-square |
| `CYAN` | `#2ee6d6` | the 34-family, gaps, Snell |
| `MAGENTA` | `#ff2d95` | the 55-family, double-counted |
| `GOLD` | `#ffc233` | the answer, φ, the cycloid |
| `ACID` | `#b6ff3d` | verdicts, safe-area guides |

## Project layout

```
behold-studio/
├── pictures/
│   ├── banner_image.py     # 2560×1440 banner, three modes
│   ├── picture.py          # 1024×1024 avatars
│   └── video1..6_thumbnail.py
├── videos/
│   ├── template.py         # bare VoiceoverScene starting point
│   └── video1..6.py
├── LICENSE
└── README.md
```

## Adding a film

1. Copy `videos/template.py`, rename the `Videon` class, and set `config.pixel_*`
   at the top for your format.
2. Paste in the silent-fallback block from `videos/video5.py` so the file renders
   without a speech service.
3. Write the maths as functions that **return numbers**, then assert the identities
   at import. If a number appears on screen, it must have been computed.
4. Add `pictures/videoN_thumbnail.py` with three angles: the recommended one, the
   surprise, and the question. Check all three at `PREVIEW = True`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `latex: command not found` | Install TeX Live / MiKTeX; `MathTex` needs a real LaTeX |
| `ModuleNotFoundError: manim_voiceover` | Films 02–06 fall back to silent automatically; film 01 needs `pip install "manim-voiceover[gtts]"` |
| gTTS `HTTPError` / no audio | gTTS is online-only — set `USE_VOICEOVER = False` for a silent cut |
| Bookmarks never fire | Set `TRANSCRIPTION_MODEL = None`; `wait_until_bookmark` degrades to plain timing |
| Text renders as boxes | Pango needs a font with the glyphs; install `fonts-dejavu` / `pango` |
| Stills render as video | Use `-s`, not `-p`/`-q` — these scenes have no animations |
| Nothing appears from `template.py` | It is a stub: the voiceover string is empty by design |

## License

MIT © 2026 Himansh Mewada — see [LICENSE](LICENSE).

Built with [Manim](https://www.manim.community/) and
[manim-voiceover](https://voiceover.manim.community/).
