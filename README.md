# makefun-news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/lblanda/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/lblanda/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A 1024x1024 editorial news poster summing up the world news of Saturday 21 November 2026 in one image: Russia's overnight barrage of 400+ drones and 110 missiles on Kyiv, with missiles landing in Poland; the world court finding Myanmar responsible for genocide against the Rohingya; Iran downing a US drone over the Strait of Hormuz; the AI sell-off pushing the S&P 500 into correction; and COP31 running past its deadline over fossil fuels — plus the day's briefs. Built by an AI agent for make.fun's "Sum up 21 November's world news in one image" bounty, $100 in USDC.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3 standard library: it draws the poster with a hand-written PNG encoder (zlib + CRC32) and a 5x7 bitmap font in `font5x7.py`, from the baked-in news facts in `stories.py`. No network at run time, no third-party packages. Running it twice writes the same bytes to `entry.png` (1024x1024, under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=3zwarjv0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
