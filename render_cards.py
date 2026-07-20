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
from matplotlib.lines import Line2D
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
    {
        "header": "6. IMT — HOW TO USE IT",
        "lines": [
            (r"translate ANY statement into 'n pivots'", dict(size=15)),
            (r"non-eigenvalue argument:", dict(size=13, color=MID, gap=0.07)),
            (r"$Av = 3v$, $v \neq 0$ $\Rightarrow$ $(A-3I)v = 0$", dict(size=14.5, x=0.14)),
            (r"$\Rightarrow$ $A - 3I$ is NOT invertible", dict(size=14.5, x=0.14)),
        ],
    },
    {
        "header": "7. ONE-TO-ONE",
        "lines": [
            (r"different inputs → different outputs", dict(size=15)),
            (r"$T(x_1) = T(x_2)$ $\Rightarrow$ $x_1 = x_2$", dict(size=15, x=0.14)),
            (r"$\mathrm{Nul}(A) = \{0\}$;  pivot in EVERY column", dict(size=14, gap=0.05)),
            (r"columns independent", dict(size=14, x=0.14)),
            (r"at most one solution for each b", dict(size=13, color=MID, gap=0.04)),
        ],
    },
    {
        "header": "7. ONTO",
        "lines": [
            (r"every codomain vector is reached", dict(size=15)),
            (r"$\forall\, b \in \mathbb{R}^m$ some x has $Ax = b$", dict(size=15, x=0.14)),
            (r"$\mathrm{Col}(A) = \mathbb{R}^m$;  pivot in EVERY row", dict(size=14, gap=0.05)),
            (r"columns span the codomain", dict(size=14, x=0.14)),
            (r"at least one solution for each b", dict(size=13, color=MID, gap=0.04)),
        ],
    },
    {
        "header": "7. ONE-TO-ONE vs ONTO",
        "lines": [
            (r"can be one-to-one but NOT onto,", dict(size=14.5)),
            (r"or onto but NOT one-to-one", dict(size=14.5, x=0.14)),
            (r"SQUARE matrix:", dict(size=14.5, gap=0.07)),
            (r"one-to-one ⇔ onto ⇔ invertible", dict(size=15.5, x=0.14)),
        ],
    },
    {
        "header": "7. DIRECT KERNEL TEST",
        "lines": [
            (r"to test one-to-one: solve $T(x) = 0$", dict(size=15)),
            (r"only the zero input ⇒ one-to-one", dict(size=14.5, x=0.14)),
            (r"Ex: $T(x,y,z) = (x,\; x{+}z,\; 3x{-}4y{+}z,\; x)$", dict(size=13.5, gap=0.07)),
            (r"$T=0$ gives $x=0$, $z=0$, $y=0$", dict(size=13.5, x=0.14)),
            (r"⇒ T is one-to-one", dict(size=13.5, x=0.14)),
        ],
    },
    {
        "header": "8. LINEAR TRANSFORMATIONS",
        "lines": [
            (r"$T(u + v) = T(u) + T(v)$", dict(size=16)),
            (r"$T(cu) = c\,T(u)$", dict(size=16)),
            (r"$T(c_1 u + c_2 v) = c_1 T(u) + c_2 T(v)$", dict(size=14.5, gap=0.05)),
            (r"every matrix transf. $T(x) = Ax$ is linear", dict(size=13, color=MID, gap=0.05)),
        ],
    },
    {
        "header": "8. LINEARITY — QUICK FAILURE TEST",
        "lines": [
            (r"if $T(0) \neq 0$:  NOT linear", dict(size=16)),
            (r"(passing this alone proves nothing!)", dict(size=13, color=MID, x=0.14)),
            (r"nonlinear signs: added constants,", dict(size=14.5, gap=0.07)),
            (r"powers ($x^2$), products ($xy$), sin, ln, …", dict(size=14.5, x=0.14)),
        ],
    },
    {
        "header": "9. STANDARD MATRIX",
        "lines": [
            (r"$A = [\;T(e_1)\;\;\; T(e_2)\;\; \cdots \;\; T(e_n)\;]$", dict(size=16)),
            (r"for $T:\mathbb{R}^n \to \mathbb{R}^m$:  A is m×n", dict(size=14.5, gap=0.06)),
            (r"coefficients of each input variable", dict(size=14, gap=0.05)),
            (r"form the corresponding column", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "9. STD MATRICES — REFLECTIONS (ℝ²)",
        "lines": [],
        "matrices": [
            {"x": 0.30, "y": 0.55, "rows": [["1", "0"], ["0", "-1"]], "label": "across x-axis:  (x,−y)"},
            {"x": 0.75, "y": 0.55, "rows": [["-1", "0"], ["0", "1"]], "label": "across y-axis:  (−x,y)"},
            {"x": 0.30, "y": 0.17, "rows": [["0", "1"], ["1", "0"]], "label": "across y=x:  (y,x)"},
            {"x": 0.75, "y": 0.17, "rows": [["0", "-1"], ["-1", "0"]], "label": "across y=−x:  (−y,−x)"},
        ],
    },
    {
        "header": "9. STD MATRICES — IDENTITY & PROJECTIONS (ℝ²)",
        "lines": [],
        "matrices": [
            {"x": 0.18, "y": 0.38, "rows": [["1", "0"], ["0", "1"]], "label": "identity"},
            {"x": 0.50, "y": 0.38, "rows": [["1", "0"], ["0", "0"]], "label": "onto x-axis: (x,0)"},
            {"x": 0.82, "y": 0.38, "rows": [["0", "0"], ["0", "1"]], "label": "onto y-axis: (0,y)"},
        ],
    },
    {
        "header": "9. STD MATRICES — ROTATIONS (CCW)",
        "lines": [],
        "matrices": [
            {"x": 0.30, "y": 0.38, "colw": 0.115,
             "rows": [[r"\cos\theta", r"-\sin\theta"], [r"\sin\theta", r"\cos\theta"]],
             "label": "rotate by θ"},
            {"x": 0.78, "y": 0.38, "rows": [["0", "-1"], ["1", "0"]], "label": "rotate 90°:  (−y,x)"},
        ],
    },
    {
        "header": "9. PROJECTIONS FROM ℝ³",
        "lines": [],
        "matrices": [
            {"x": 0.28, "y": 0.33, "rows": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "0"]],
             "label": "to xy-plane, stay in ℝ³"},
            {"x": 0.76, "y": 0.38, "rows": [["1", "0", "0"], ["0", "1", "0"]],
             "label": "forget z, land in ℝ²"},
        ],
    },
    {
        "header": "10. COMPOSITION",
        "lines": [
            (r"$(T \circ U)(x) = T(U(x))$", dict(size=16)),
            (r"apply U FIRST, then T (read right → left)", dict(size=14, x=0.14)),
            (r"$[T \circ U] = AB$,    $[U \circ T] = BA$", dict(size=15, gap=0.06)),
            (r"sizes: (m×n)(n×p) ⇒ m×p", dict(size=14.5, gap=0.06)),
            (r"inner must match; outer = answer size", dict(size=13, color=MID, x=0.14)),
        ],
    },
    {
        "header": "10. WORKED COMPOSITION",
        "lines": [
            (r"$T(x,y) = (x{+}2y,\; 2x{+}y,\; x{-}y)$,   $U(x,y,z) = (-y,\, x)$", dict(size=13)),
        ],
        "matrices": [
            {"x": 0.15, "y": 0.28, "rows": [["1", "2"], ["2", "1"], ["1", "-1"]], "label": "T:  A"},
            {"x": 0.48, "y": 0.33, "rows": [["0", "-1", "0"], ["1", "0", "0"]], "label": "U:  B"},
            {"x": 0.82, "y": 0.33, "rows": [["-2", "-1"], ["1", "2"]], "label": "[U∘T] = BA"},
        ],
    },
    {
        "header": "RECIPE — IS Ax=b CONSISTENT?",
        "lines": [
            (r"1. row-reduce $[\,A \;|\; b\,]$", dict(size=15)),
            (r"2. look for row $[\,0 \;\cdots\; 0 \;|\; c\,]$, $c \neq 0$", dict(size=15)),
            (r"3. no contradiction row ⇒ consistent", dict(size=15)),
        ],
    },
    {
        "header": "RECIPE — POINT / LINE / PLANE",
        "lines": [
            (r"1. confirm the system is consistent", dict(size=15)),
            (r"2. count free variables:", dict(size=15)),
            (r"0 → point,  1 → line,  2 → plane", dict(size=15, x=0.14)),
            (r"3 → 3-space", dict(size=15, x=0.14)),
            (r"solutions live in $\mathbb{R}^n$, n = # variables", dict(size=13, color=MID, gap=0.04)),
        ],
    },
    {
        "header": "RECIPE — BASIS FOR Col(A)",
        "lines": [
            (r"1. row-reduce A, note pivot COLUMN", dict(size=15)),
            (r"positions", dict(size=15, x=0.14)),
            (r"2. go back to the ORIGINAL A", dict(size=15)),
            (r"3. take original columns at those spots", dict(size=15)),
            (r"never use RREF columns for Col(A)!", dict(size=13, color=MID, gap=0.04)),
        ],
    },
    {
        "header": "RECIPE — BASIS FOR Nul(A)",
        "lines": [
            (r"1. solve $Ax = 0$ in RREF", dict(size=15)),
            (r"2. assign parameters to free variables", dict(size=15)),
            (r"3. write x = combination of parameter", dict(size=15)),
            (r"vectors — those vectors = the basis", dict(size=15, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — IS THIS A BASIS FOR W?",
        "lines": [
            (r"1. every proposed vector belongs to W", dict(size=15)),
            (r"2. vectors are linearly independent", dict(size=15)),
            (r"3. count = dim(W),", dict(size=15)),
            (r"or directly verify they span W", dict(size=15, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — SUBSPACE TEST",
        "lines": [
            (r"1. check 0 belongs", dict(size=15)),
            (r"2. closed under addition", dict(size=15)),
            (r"3. closed under scalar multiplication", dict(size=15)),
            (r"shortcut: any Span{…} or Nul(A)", dict(size=13.5, color=MID, gap=0.05)),
            (r"is automatically a subspace", dict(size=13.5, color=MID, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — VECTOR OUTSIDE THE RANGE",
        "lines": [
            (r"1. write the general output $Ax$", dict(size=14.5)),
            (r"2. find a relation all outputs satisfy", dict(size=14.5)),
            (r"3. pick a codomain vector violating it", dict(size=14.5)),
            (r"Ex: outputs $(s{-}t,\; 2t,\; 3t)$: need $3b = 2c$", dict(size=13, gap=0.05)),
            (r"$(0,1,0)$ violates ⇒ outside the range", dict(size=13, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — TEST 1-TO-1 / TEST ONTO",
        "lines": [
            (r"one-to-one:  solve $Ax=0$ or $T(x)=0$", dict(size=14.5)),
            (r"only zero solution / pivot every column", dict(size=14, x=0.14)),
            (r"onto:  pivot in every row", dict(size=14.5, gap=0.06)),
            (r"rank = m / $\mathrm{Col}(A)=\mathbb{R}^m$ /", dict(size=14, x=0.14)),
            (r"$Ax=b$ consistent for every b", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — STD MATRIX & COMPOSING",
        "lines": [
            (r"std matrix:  compute $T(e_1),\ldots,T(e_n)$", dict(size=14.5)),
            (r"place outputs as columns; size is m×n", dict(size=14, x=0.14)),
            (r"compose:  check domains/codomains,", dict(size=14.5, gap=0.06)),
            (r"rightmost transformation acts first,", dict(size=14, x=0.14)),
            (r"$[T \circ U] = AB$", dict(size=14, x=0.14)),
        ],
    },
    {
        "header": "RECIPE — ∞ SOLUTIONS (PARAMETERS)",
        "lines": [
            (r"1. row-reduce symbolically", dict(size=15)),
            (r"2. require NO contradiction in", dict(size=15)),
            (r"the augmented column", dict(size=15, x=0.14)),
            (r"3. require ≥ 1 free variable", dict(size=15)),
            (r"row $[\,0 \cdots 0\; \alpha \;|\; \beta\,]$ ⇒ need $\alpha=0$ AND $\beta=0$", dict(size=13.5, gap=0.05)),
        ],
    },
]

TILE_BOXES = [(0, 0, 288, 144), (288, 0, 576, 144), (0, 144, 288, 288), (288, 144, 576, 288)]


def draw_matrix(fig, m):
    """Draw a bracketed matrix centred at (m['x'], m['y']) in figure coords."""
    rows = m["rows"]
    nr, nc = len(rows), len(rows[0])
    size = m.get("size", 13)
    colw = m.get("colw", 0.055)
    rowh = size * (100 / 72) * 1.6 / H
    w, h = nc * colw, nr * rowh
    x0, ytop = m["x"] - w / 2, m["y"] + h / 2
    for i, row in enumerate(rows):
        for j, entry in enumerate(row):
            fig.text(x0 + colw * (j + 0.5), ytop - rowh * (i + 0.5), f"${entry}$",
                     fontsize=size, color=FG, ha="center", va="center")
    tick, pad = 0.014, 0.006
    for bx, dirn in ((x0 - pad, 1), (x0 + w + pad, -1)):
        fig.add_artist(Line2D(
            [bx + dirn * tick, bx, bx, bx + dirn * tick],
            [ytop + 0.012, ytop + 0.012, ytop - h - 0.012, ytop - h - 0.012],
            transform=fig.transFigure, color=FG, linewidth=1.3))
    if m.get("label"):
        fig.text(m["x"], ytop + m.get("labeldy", 0.055), m["label"],
                 fontsize=11.5, color=MID, ha="center", va="bottom")


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

    for m in card.get("matrices", []):
        draw_matrix(fig, m)

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
