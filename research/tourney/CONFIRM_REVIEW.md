# Is the confirmation stage helping? (owner #66, 2026-11-27 15:29 PDT)

The confirmation stage (owner #46, live from 2026-11-26 17:13 PDT) crowned a qualifier only after 150 fresh games
in which it still led the champion. The owner asked for evidence that it helps. If there was none, it would go.

**Verdict: no measurable benefit. Removed on 2026-11-27.** The qualifying bar stays: 200 games and a lead of more than
one combined SE.

Method: one Bradley-Terry fit over all 173,408 games as of 15:30 PDT. The true gain of a bot over the champion it
challenged is the difference of their current ratings. These ratings rest on far more games than either bot had at
the time. Scripts: `analyze.py` and `quals.py` in the session scratchpad. The numbers below are their output.

## 1. Crown quality before and after the rule

| | Crownings | Mean true gain over the base | Gain ≤ 0 | Gain below −1 SE |
|---|---|---|---|---|
| Before #46 (v02 to y211) | 40 | +45.9 | 1 (y170, −4 ±10) | 0 |
| The last 8 before #46 (t70 to y211) | 8 | +18 | 1 | 0 |
| After #46 (y221 to t140) | 6 | +22.0 | 1 (t135, −1 ±7) | 0 |

The rule was motivated by an early reading that 16 of 40 champions rated below the bot they replaced. With today's
games that is no longer true: 39 of 40 rate above their base, and the exception is within noise. The bar of one SE
already prevented regressions. One neutral crowning (t135, −1) passed the 150-game check anyway: a mild bar over 150
games passes a truly neutral bot about half the time.

Gains per crowning had already fallen to about +18 before the rule began. The plateau is diminishing returns, not
the rule.

## 2. Each reign: what the rule crowned vs what the bar alone would have crowned

| Reign | Qualifiers (true lead vs that champion) | With the check | Without it (first qualifier) | Delay |
|---|---|---|---|---|
| y211 | y221 +36, t102 +38, t105 +19 | y221 | y221 or t102 | 25 min |
| y221 | t111 +14, y224 +4 | t111 | t111 or y224 | ≈0 |
| t111 | t118 +36 | t118 | t118 | 16 min |
| t118 | y250 +6 (00:12), t122 +11 (00:30) | t122 (+11) | y250 (+6) | 55 min |
| t122 | y260 −5 (02:09), y266 −11, t134 −2, t135 −1, t136 −1 | t135 (−1) | y260 (−5) | 4 h |
| t135 | t140 +36, t138 +19, y279 +2 | t140 | t140 or t138 | 12 min |
| t140/r140 | t145 −20 ±15, y284 −7 ±13 (09:34) | none (held) | t145 or y284 | – |

- Bots that qualified but were never crowned (18 in all) had a mean true lead of +0.3. Ten were at or below 0.
  Three were below −1 SE.
- The only case where the check plausibly avoided a regression is the last row: t145 or y284, −7 to −20.
  Neither is significant (within 1.3 SE).
- In the t122 reign, the check held the crown for 4 hours. It then crowned an equally neutral bot.

## 3. Costs of the check
- A delay of 12 minutes to 4 hours per crowning.
- A tenth of each run went to qualifier-vs-champion games.
- Neutral qualifiers passed about half the time, after a delay. So the check did not stop neutral changes outright,
  it slowed them.

## What changed
- `tools/tourney.py rank` crowns the top qualifier at once, and `plan` no longer gives qualifiers extra games.
  `confirm.txt` stays empty, and the dashboard's confirm fields stay false.
- Safety nets that remain: the bar of 200 games plus a lead of one SE, and the guardrail. The guardrail is the replica
  slots' head-to-head record against the champion (owner #59/#60).
- To restore the check: git history, commit "drop the confirmation stage (owner #66)".
