# LinAlg Master Sheet — Even G2 viewer

Flip through the linear algebra (ch. 1–3) master sheet on Even Realities G2
glasses as pre-rendered math cards. Live at:

**https://sontem.github.io/g2-mastersheet/**

## One-time setup (~2 min, needs the phone once)

1. Sign in at <https://hub.evenrealities.com> with the **same account** as the
   Even Realities phone app. This unlocks the developer section — no approval
   process.
2. Force-quit and reopen the Even Realities app. The **Even Hub** tab now shows
   a developer section (top right) with a QR scanner.
3. Scan `QR-scan-with-even-app.png` (points at the URL above). The first card
   appears on the glasses; the phone can go in your pocket.

## Controls (temple touchpad or R1 ring)

| Gesture | Action |
|---|---|
| tap | next card |
| swipe down | next card |
| swipe up | previous card |
| double-tap | exit dialog |

Last card position is remembered between launches.

## How it works

- `render_cards.py` renders 39 cards (576×288, white on black, matplotlib
  mathtext for ℝⁿ/⊆/matrices) and splits each into four 288×144 PNG tiles —
  the G2's max image-container size. A 2×2 tile grid covers the full canvas.
- `src/main.ts` is an Even Hub plugin: an invisible full-screen text container
  captures input; four image containers display the tiles via
  `updateImageRawData` (serial sends, stale-flip guard, neighbor prefetch).
- Opened in a normal browser, the page falls back to a keyboard-driven preview
  (← / →).

## Updating the cards

```bash
python3 render_cards.py     # edit CARDS in the script first
npm run build
cd dist && git init -b gh-pages && git add -A \
  && git commit -m deploy \
  && git push -f https://github.com/SonTEM/g2-mastersheet.git gh-pages
```
