# Pre-registered test: moderate local gains and the next hour on the replica

Registered 2026-11-26 16:15 PDT (owner prompts #38, #39), before any of the data it will be judged on exists.

## Where it came from

On the windows from 2026-11-25 13:25 to 2026-11-26 16:07 PDT (79 windows), those whose local champion change was
+1 to +44 were followed by a mean replica change of -2.8, against +11.0 for the other 54 windows (difference -13.8,
rotation p = 0.014, Newey-West p = 0.005; absolute mean below zero: p = 0.19). The +1..+44 range was picked after
seeing those numbers, and the effect shrinks for other cutoffs (U = 19: -6.5, p = 0.16; U = 100: -8.9, p = 0.03), so
that result only suggests the hypothesis. This test checks it on new data.

## Definitions (unchanged from the dashboard section "Mean replica change after a local rating change")

- A window ends at a replica sample t (progress/replica-elo.csv). dR = our replica rating at t minus the sample
  nearest t - 60 min (within 20 min). dL = the local rating of the champion holding the title at t - 60 min minus
  that of the champion at t - 120 min, both from the Bradley-Terry fit of all games at evaluation time.
- G = windows with +1 <= dL <= +44.
- Data: only windows with t after 2026-11-26 18:07 PDT, so that both hours of every window come after the
  exploratory data ended (16:07).
- Code: `research/replica/deltatest.py` as committed with this file, run as
  `python3 research/replica/deltatest.py BOARD.json '2026-11-26 18:07'` on a fresh `tools/prod.sh board` export.

## Hypotheses and decision rule

- H1 (primary): the mean dR of G windows is lower than that of the other windows. One-sided rotation test of the
  difference in means (G shifted against dR by 4 to n-4 positions), alpha = 0.05.
- H2 (secondary): the mean dR of G windows is below zero. One-sided Newey-West t-test (lag 2, df = n_G/3 - 1),
  alpha = 0.05.
- Reported as well, not tested: the difference, its Newey-West p, and the event-level list (each distinct
  champion change behind the G windows and its mean dR).

## When

Evaluate once, at the first prod on or after 2026-11-29 16:07 PDT (about 66 hours of windows, about 200). If G then
holds fewer than 30 windows, extend by 24 hours at a time, up to 2026-12-01 16:07 PDT, and report whatever is there
then. No look at the result before the evaluation, and no change to the definitions, cutoffs or code.

H1 holds if rotation p < 0.05 with the difference negative. Anything else means it does not hold on new data.

## Addendum, 2026-11-26 17:25 PDT, before any pre-registered data exists (window data start 18:07)

Nothing above changes: same windows, groups, tests, code and dates. This adds how to read the result.

- From the 17:13 prod on, a bot is crowned only after a confirmation stage (`tools/tourney.py`, owner #46): once it
  clears the lead bar it needs 150 fresh games in which it still leads the champion. Every pre-registered window
  falls under this rule; the exploratory data (H1's -13.8, p 0.014) came from the old rule.
- The leading explanation for the exploratory dip is the winner's curse: the bot that first clears the bar is the
  luckiest one, and moderate local gains are the most likely to be luck. Confirmation should filter those out.
  Owner #48: "If the anomalous dip in the delta Elo chart is truly caused by the winner's curse, this should
  alleviate that. Let's see if it does."
- So, read together with the exploratory result:
  - H1 not holding (and the G-minus-rest difference near 0 or positive) is what the winner's-curse explanation
    predicts under confirmation;
  - H1 holding means the dip persists despite confirmation: the winner's curse alone does not explain it.
- Fewer crownings are expected under confirmation, so G may stay small; the extension rule above applies unchanged.
- Report the difference next to the exploratory -13.8 (Newey-West SE included) so the change is visible.
