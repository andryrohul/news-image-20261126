# The Thursday Ledger — news-image-20261126

One-image summary of Thursday 26 November 2026's world news, drawn as a
clean newspaper front page: four pictured leads (oil and the Hormuz mine
claims, Asia's rally in reply to the tariff proposal, the Bank of Korea's
hike to 3.25%, and the resumed Bogor mine search), 31 further dated briefs
grouped by region, a UTC timeline strip, a label legend, and a visible
DATE CHECK box listing the stories kept off the page because they belong
to another day.

## Run

```sh
python3 main.py
```

Standard library only (Python 3.13). The program writes `entry.png` to
`$MAKEFUN_OUTPUT_DIR` if set, else `/output` if that directory exists,
else `./output`. Output is deterministic: two runs produce identical
bytes.
