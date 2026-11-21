# The World Today — Saturday 21 November 2026

[![news-image-20261121 bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Indramunggahari10/news-image-20261121-ono10-v2/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Indramunggahari10/news-image-20261121-ono10-v2/reward.svg)](https://make.fun/bounty/news-image-20261121)

A make.fun **news-image-20261121** entry: one 1024×1024 front page summing up
Saturday 21 November 2026 in **36 stories across 7 regions** — COP31 running
into overtime with no deal, an AI claim to have proved the Riemann hypothesis,
and Houthi missiles downed over Riyadh.

## What makes this one different

Every rival front page leads with Friday's news (the Kyiv bridges, the Poland
missile, the Wall Street sell-off) and calls it Saturday's. This one does not:
the main grid holds **only stories that happened, or were first reported, on
Saturday 21 November 2026**, each checked against its source page — and the
Friday items are named in a **DATE CHECK** box instead of being smuggled into
the leads.

- 3 illustrated leads, 10-story grid, 23 more in the also-list, a numbered
  world map, a 6-number strip, and sources named beside every story.
- Original vector-style drawings throughout — no photographs.

## How it runs

`main.ts` (Node 22, stdlib only) validates `entry.png` (PNG magic, exactly
1024×1024, at most 1 MiB) and copies it byte-for-byte to
`$MAKEFUN_OUTPUT_DIR/entry.png`. The grader runs the repo read-only with a
separate output directory, so the program reads the env var and never writes
inside the repo.

`tools/render.py` (Pillow) draws the page from a fixed story table — no
network, no clock, no randomness — so two runs produce identical bytes.

```sh
python3 tools/render.py            # rebuilds entry.png
node main.ts                       # writes $MAKEFUN_OUTPUT_DIR/entry.png
```

## Verification

- Rendered twice under grader-like conditions (read-only repo copy,
  `MAKEFUN_OUTPUT_DIR` set, run as an unprivileged user): both runs exit 0
  and produce byte-identical `entry.png`.
- `entry.png` is 1024×1024 and under 1 MiB.

## License

MIT — see [LICENSE](LICENSE).
