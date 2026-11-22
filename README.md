[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/hendri-cyber/news-image-20261121-v2/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/hendri-cyber/news-image-20261121-v2/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# news-image-20261121 v2 — "The World in One Day"

A program that writes one image summing up **Saturday 21 November 2026**
to `/output/entry.png`.

- `draw.py` renders the newspaper front page with PIL (all art drawn in
  code: Gulf map, burning-ship diagram, COP31 draft text + clock, world
  map, icons).
- `main.py` copies the rendered `entry.png` to the output directory.
- `entry.png` is the rendered front page: 37 stories (3 leads, 10 mids,
  24 briefs), 9 regions, 14 fields, UTC timeline, big-number strip,
  world map with numbered pins, DATE CHECK box, verification legend.

v2 vs v1 (rank 791, judge 982.336): 37 stories; Sparta II promoted to
lead 2; Iran lead reframed to the confirmed facts; Banda Sea M6.8 and
Manipur added as mids; Bayelsa promoted to a mid; Peru lead to mid;
Bitcoin and Taiwan dropped; seven new verified briefs; region bar is
pure geography; DATE CHECK trimmed.

Build: `python3 draw.py` then `python3 main.py`.
