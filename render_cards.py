#!/usr/bin/env python3
"""Render the Linear Algebra Master Sheet as 576x288 cards for the Even G2,
then split each card into four 288x144 tiles (the G2's max image container).

White-on-black: white pixels = bright green on the micro-LED display, black = off.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

W, H = 576, 288
DPI = 100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "tiles")
PREVIEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PREVIEW, exist_ok=True)

plt.rcParams["mathtext.fontset"] = "dejavusans"
plt.rcParams["font.family"] = "DejaVu Sans"

FG = "#ffffff"      # main text  -> brightest green
DIM = "#8c8c8c"     # header/footer -> mid green
MID = "#c8c8c8"     # secondary emphasis

# Each card: header label, list of body lines. A line is (text, opts) where opts
# may set size, x, ha, color, extra gap before the line.
CARDS = [
    {
        "header": "",
        "lines": [
            (r"LINEAR ALGEBRA", dict(size=22, x=0.5, ha="center", gap=0.10)),
            (r"MASTER SHEET  ·  CH. 1–3", dict(size=13, x=0.5, ha="center", color=MID)),
            (r"tap: next   ·   swipe up: back", dict(size=10.5, x=0.5, ha="center", color=DIM, gap=0.10)),
            (r"double-tap: exit", dict(size=10.5, x=0.5, ha="center", color=DIM)),
        ],
    },
    {
        "header": "1. DIMENSION MAP",
        "lines": [
            (r"A is m×n:   $A:\mathbb{R}^n \to \mathbb{R}^m$", dict(size=15)),
            (r"$x \in \mathbb{R}^n$,    $Ax$ and $b \in \mathbb{R}^m$", dict(size=15)),
            (r"columns of A:  n vectors in $\mathbb{R}^m$", dict(size=14, gap=0.05)),
            (r"rows of A:  m vectors in $\mathbb{R}^n$", dict(size=14)),
        ],
    },
    {
        "header": "1. DIMENSION MAP",
        "lines": [
            (r"$\mathrm{Col}(A) = \mathrm{Range}(A) \subseteq \mathbb{R}^m$", dict(size=16)),
            (r"= all possible outputs $Ax$", dict(size=14, x=0.14)),
            (r"$\mathrm{Nul}(A) \subseteq \mathbb{R}^n$", dict(size=16, gap=0.06)),
            (r"= all $x$ satisfying $Ax=0$", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "1. DIMENSION MAP",
        "lines": [
            (r"$\mathrm{rank}(A) = \dim \mathrm{Col}(A) =$ # pivots", dict(size=15)),
            (r"$\mathrm{nullity}(A) = \dim \mathrm{Nul}(A) =$ # free vars", dict(size=15)),
            (r"Ex: 4×3 matrix:  $A:\mathbb{R}^3 \to \mathbb{R}^4$", dict(size=14, gap=0.07)),
            (r"3 columns lie in $\mathbb{R}^4$", dict(size=14, x=0.14)),
            (r"$\mathrm{Col}(A) \subseteq \mathbb{R}^4$,   $\mathrm{Nul}(A) \subseteq \mathbb{R}^3$", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "2. PIVOT RULES",
        "lines": [
            (r"pivot in EVERY ROW  $\Rightarrow$  ONTO", dict(size=16)),
            (r"$\mathrm{Col}(A) = \mathbb{R}^m$", dict(size=15, x=0.14)),
            (r"$Ax=b$ consistent for every $b \in \mathbb{R}^m$", dict(size=14, x=0.14)),
            (r"hook: ROWS → reach every output", dict(size=13, color=MID, gap=0.07)),
            (r"(onto / existence)", dict(size=12, color=DIM, x=0.14)),
        ],
    },
    {
        "header": "2. PIVOT RULES",
        "lines": [
            (r"pivot in EVERY COLUMN  $\Rightarrow$  ONE-TO-ONE", dict(size=15)),
            (r"columns independent,  $\mathrm{Nul}(A)=\{0\}$", dict(size=14, x=0.14)),
            (r"at most one solution", dict(size=14, x=0.14)),
            (r"hook: COLUMNS → inputs unique", dict(size=13, color=MID, gap=0.05)),
            (r"BOTH (square) $\Rightarrow$ invertible: exactly 1 sol.", dict(size=14, gap=0.05)),
        ],
    },
    {
        "header": "3. CONSISTENCY",
        "lines": [
            (r"$[\;0\;\;0\;\;\cdots\;\;0\;\;|\;\;c\;]\,,\;\; c \neq 0$", dict(size=17, x=0.5, ha="center")),
            (r"$\Rightarrow$ INCONSISTENT: no solutions", dict(size=15, x=0.5, ha="center", gap=0.04)),
            (r"consistent + no free variables", dict(size=14, gap=0.08)),
            (r"$\Rightarrow$ exactly one solution (a point)", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "3. CONSISTENCY",
        "lines": [
            (r"consistent + free vars $\Rightarrow$ $\infty$ many sols:", dict(size=15)),
            (r"1 free var → a line", dict(size=14, x=0.14)),
            (r"2 free vars → a plane", dict(size=14, x=0.14)),
            (r"k free vars → affine k-dim set in $\mathbb{R}^n$", dict(size=14, x=0.14)),
            (r"# solutions: 0, 1, or ∞ — never 2, 3, 10…", dict(size=13.5, color=MID, gap=0.06)),
        ],
    },
    {
        "header": "4. RANK–NULLITY",
        "lines": [
            (r"$\mathrm{rank}(A) + \mathrm{nullity}(A) = n$", dict(size=19, x=0.5, ha="center")),
            (r"(n = number of columns)", dict(size=12.5, x=0.5, ha="center", color=DIM)),
            (r"$\mathrm{rank}(A) = \dim\mathrm{Col}(A) = $ # pivots", dict(size=14, gap=0.06)),
            (r"$\mathrm{nullity}(A) = $ # free vars $= n - \mathrm{rank}(A)$", dict(size=14)),
            (r"$\mathrm{rank}(A) \leq \min(m,n)$", dict(size=14)),
        ],
    },
    {
        "header": "4. RANK–NULLITY — TRAP",
        "lines": [
            (r"do NOT merge rank and nullity:", dict(size=15)),
            (r"$\dim\mathrm{Col}(A) = \mathrm{rank}(A)$,  NOT nullity", dict(size=15, x=0.14, gap=0.04)),
            (r"$\mathrm{nullity}(A) = \dim\mathrm{Nul}(A)$  always", dict(size=15, x=0.14)),
            (r"rank + nullity = # columns", dict(size=15, gap=0.05)),
        ],
    },
    {
        "header": "5. HOMOGENEOUS vs NOT",
        "lines": [
            (r"$Ax=0$:  always consistent, has $x=0$", dict(size=15)),
            (r"solution set $= \mathrm{Nul}(A)$, a subspace", dict(size=14, x=0.14)),
            (r"$Ax=b$:  if consistent,", dict(size=15, gap=0.06)),
            (r"all solutions $= x_p + \mathrm{Nul}(A)$", dict(size=15, x=0.14)),
        ],
    },
    {
        "header": "5. HOMOGENEOUS vs NOT",
        "lines": [
            (r"$x_1, x_2$ solve $Ax=b$ $\Rightarrow$ $A(x_1{-}x_2)=0$", dict(size=14.5)),
            (r"solutions $x = p + t\,d$ :", dict(size=15, gap=0.05)),
            (r"$p$ = one particular solution", dict(size=14, x=0.14)),
            (r"$\mathrm{Nul}(A) = \mathrm{Span}\{d\}$", dict(size=14, x=0.14)),
            (r"subtract p → line passes through origin", dict(size=13, color=MID, gap=0.04)),
        ],
    },
    {
        "header": "6. INVERTIBLE MATRIX THM  (square A)",
        "lines": [
            (r"all equivalent:", dict(size=13, color=MID)),
            (r"$\bullet$ A invertible $\Leftrightarrow$ $A^{-1}$ exists", dict(size=15)),
            (r"$\bullet$ n pivots — every row AND column", dict(size=15)),
            (r"$\bullet$ $\mathrm{RREF}(A) = I_n$", dict(size=15)),
        ],
    },
    {
        "header": "6. INVERTIBLE MATRIX THM  (square A)",
        "lines": [
            (r"$\bullet$ $\mathrm{Nul}(A) = \{0\}$;   $\mathrm{nullity}(A)=0$", dict(size=15)),
            (r"$\bullet$ columns linearly independent,", dict(size=15)),
            (r"span $\mathbb{R}^n$, form a basis for $\mathbb{R}^n$", dict(size=15, x=0.17)),
        ],
    },
    {
        "header": "6. INVERTIBLE MATRIX THM  (square A)",
        "lines": [
            (r"$\bullet$ $Ax=b$ has exactly one solution", dict(size=15)),
            (r"for every $b \in \mathbb{R}^n$", dict(size=15, x=0.17)),
            (r"$\bullet$ $x \mapsto Ax$ is one-to-one AND onto", dict(size=15, gap=0.04)),
            (r"square A only!", dict(size=12.5, color=DIM, gap=0.06)),
        ],
    },
]

TILE_BOXES = [(0, 0, 288, 144), (288, 0, 576, 144), (0, 144, 288, 288), (288, 144, 576, 288)]


def render_card(idx: int, card: dict, total: int) -> str:
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor("black")

    if card["header"]:
        fig.text(0.035, 0.945, card["header"], fontsize=10.5, color=DIM,
                 ha="left", va="top", fontweight="bold")
    # progress counter is NOT baked in: the app overlays it as a text
    # container, so otherwise-identical tiles stay shareable across cards

    y = 0.80 if card["header"] else 0.72
    for text, opts in card["lines"]:
        size = opts.get("size", 14)
        y -= opts.get("gap", 0.0)
        fig.text(opts.get("x", 0.055), y, text, fontsize=size,
                 color=opts.get("color", FG), ha=opts.get("ha", "left"), va="top")
        y -= (size * (DPI / 72) * 1.55) / H  # pt -> px -> fig fraction, 1.55 leading

    path = os.path.join(PREVIEW, f"card{idx:02d}.png")
    fig.savefig(path, dpi=DPI, facecolor="black")
    plt.close(fig)
    return path


def main():
    import hashlib
    import io

    total = len(CARDS)
    manifest = []
    seen = {}
    for i, card in enumerate(CARDS):
        path = render_card(i, card, total)
        img = Image.open(path).convert("L")
        if img.size != (W, H):
            img = img.resize((W, H))
        img.save(path)  # keep grayscale preview
        tiles = []
        for box in TILE_BOXES:
            tile = img.crop(box)
            buf = io.BytesIO()
            tile.save(buf, format="PNG", optimize=True)
            data = buf.getvalue()
            digest = hashlib.sha1(data).hexdigest()[:12]
            # identical tiles (e.g. all-black halves) share one file, so the
            # app can skip re-sending a tile whose URL is already on screen
            if digest not in seen:
                name = f"t_{digest}.png"
                with open(os.path.join(OUT, name), "wb") as f:
                    f.write(data)
                seen[digest] = name
            tiles.append(f"tiles/{seen[digest]}")
        manifest.append(tiles)
    print(f"{total * 4} tiles, {len(seen)} unique")

    with open(os.path.join(os.path.dirname(OUT), "cards.json"), "w") as f:
        json.dump({"count": total, "cards": manifest}, f, indent=1)

    # contact sheet for review
    cols, rows = 3, (total + 2) // 3
    sheet = Image.new("L", (cols * (W // 2 + 8) + 8, rows * (H // 2 + 8) + 8), 32)
    for i in range(total):
        img = Image.open(os.path.join(PREVIEW, f"card{i:02d}.png")).resize((W // 2, H // 2))
        sheet.paste(img, (8 + (i % cols) * (W // 2 + 8), 8 + (i // cols) * (H // 2 + 8)))
    sheet.save(os.path.join(PREVIEW, "contact_sheet.png"))
    print(f"rendered {total} cards -> {OUT}")


if __name__ == "__main__":
    main()
