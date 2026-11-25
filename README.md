# THE WORLD IN ONE DAY — 36 stories, Wednesday 25 November 2026

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/ibr6ixhim/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/ibr6ixhim/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One image summing up the world's news of Wednesday 25 November 2026:
Putin vows "inevitable" retaliation as drones hit two more refineries
overnight, Shenzhou-24 carries the first foreign astronaut to Tiangong,
and the Saudi-led coalition strikes Hodeidah port after the Houthis
threaten Jeddah.

Entry for the Make.fun bounty
[news-image-20261125](https://make.fun/bounty/news-image-20261125) — join via
[my referral link](https://make.fun/r/8kq0s40d).

## The image

`entry.png` (1024×1024, PNG) is a dense newspaper front page: banner,
masthead with the date, a three-hero deck, a "day in numbers" strip, a UTC
timeline, three illustrated heroes, a 10-story grid, a 23-story ALSO list,
a DATE CHECK box and a legend. Every story is dated 25 November 2026 and
carries a status tag (CONFIRMED / REPORTED / CLAIM / OFFICIAL) and a named
source.

Stories by region: Africa 2, Asia 8, Europe 8, Middle East 7, North
America 4, South America 4, plus science, economy, sport and tech — 36
stories in total.

## How it is built

`build.py` (Python + Pillow) draws the front page from `stories.json` and
writes `entry.png`. `main.py` (Python 3.13, standard library only, no
network) copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (or
`/output/entry.png`) and prints its SHA-256. Both runs are byte-identical.

Verify locally:

```sh
python3 build.py
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum entry.png out1/entry.png out2/entry.png
```

Verified 25 Nov 2026: `build.py` run twice gives identical bytes
(215,499 bytes, 1024×1024 PNG, sha256 `216138d7…`); `main.py` run
twice into different output directories gives the same bytes. A DATE
CHECK box on the image names four big stories deliberately left out
because they belong to earlier days (Huawei verdict 24 Nov, COP31
22 Nov, ICJ Myanmar ruling 19 Nov, GTA 6 launch figures 23 Nov).
```
