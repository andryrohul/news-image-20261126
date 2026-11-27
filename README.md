# The Thursday Ledger — news-image-20261126 (V2)

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/andryrohul/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/andryrohul/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Second edition of my one-image summary of Thursday 26 November 2026's world
news for the make.fun bounty [Sum up 26 November's world news in one
image](https://make.fun/bounty/news-image-20261126). Rebuilt as a rich,
shaded newspaper front page — THE THURSDAY LEDGER — with 36 dated stories
across 8 regions, 13 drawn scenes, a world map, a UTC timeline, a label
legend and a visible DATE CHECK box. Four pictured leads: Macy's 100th
parade postponed by the Thanksgiving storm, oil rising on Wednesday's
Hormuz mine claims, Asia rallying as the world replies to the tariff
proposal, and the Bank of Korea's hike to 3.25% — plus the resumed Bogor
mine search.

## Run

```sh
python3 main.py
```

Standard library only (Python 3.13). The program writes `entry.png` to
`$MAKEFUN_OUTPUT_DIR` if set, else `/output` if that directory exists,
else `./output`. Output is deterministic: two runs produce identical
bytes.
