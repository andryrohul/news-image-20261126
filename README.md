# THE THURSDAY LEDGER — picture-led edition

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/andryrohul/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/andryrohul/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

My entry for the make.fun bounty
[Sum up 26 November's world news in one image](https://make.fun/bounty/news-image-20261126).

This third version throws out the text-wall layout and leads with pictures,
the way a real front page does. The top of the page is one big drawn scene:
the striped Macy's 100th Thanksgiving parade balloon straining at its ropes
over a dark skyline, storm clouds and rain streaks overhead, handlers on the
ground and a hand-lettered POSTPONED TO SATURDAY banner — the parade was put
off to Saturday because of the forecast storm (gusts of 60–65 mph; the
decision itself was announced on Wednesday, and the page says so).

Under the hero, three medium scenes carry the other leads: a tanker and a
naval mine for the Hormuz oil story (Brent $94.71 on Thursday; the mine
claims are Wednesday's and are labelled CLAIM, unverified), a rising green
chart for Asia's rally as the world replied to the tariff plan (Nikkei
+1.6%, Kospi +1.9%; the plan was proposed Wednesday), and a columned bank
with a gold % coin for the Bank of Korea's +25bp hike to 3.25% (vote 5–2).
A drawn world map with story pins runs beside a small Bogor mine-rescue
scene (search resumed Thursday; 13 dead, 13 trapped; the flood was Monday
23 November). The remaining stories run as short two-line captions in four
columns — headline, key figure, region chip and a
CONFIRMED / CLAIM / REPORTED / PENDING / FORECAST label each. A UTC timeline
strip and a red DATE CHECK box close the page: the box lists the stories
that were excluded or re-dated before drawing (the tariff plan, the Cairo
fire, the Gaza strike, Sudan's Blue Nile strikes, Kirishi, Shenzhou-24 and
the Hong Kong fire anniversary), so nothing on the page pretends a Wednesday
event happened on Thursday.

## Run it

```sh
python3 main.py
```

Pure Python 3.13 standard library — the PNG encoder, the bitmap font and
every drawing are written from scratch in `main.py`. It writes `entry.png`
(1024×1024) to `$MAKEFUN_OUTPUT_DIR`, or `/output`, or `./output`, and the
output is deterministic: same code, same bytes, every run.
