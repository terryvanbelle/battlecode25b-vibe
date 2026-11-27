# PROMPTS.md

Every prompt the owner gave this project, verbatim, in order. Times are PDT.

## #1 (2026-11-25 ~08:00 PDT)

We are going to build a world-class champion MIT Battlecode bot.  Battlecode is a contest where the contestants implement bots to play against other bots in an arena.  Each year’s rules are different from prior years, but they all share some common features.  We have built bots for several prior years already (Github repositories, in order of attempt:  battlecode22-vibe, battlecode26-vibe, battlecode25-vibe, battlecode21-vibe, battlecode20-vibe, battlecode24-vibe, battlecode23-vibe, battlecode19-vibe, and battlecode26b-vibe.  Each attempt was built on previous attempts, so weight the findings of later projects higher than earlier ones).  Read through the code and documentation for these projects thoroughly to learn what has already been done, and what has worked or not worked.  Pay particular attention to files called LEARNINGS.md and TRAINING_ALGORITHM.md.   Feel free to steal any code that might be useful to you.  The repository battlecode-vibe also has many files at the top level that will be helpful to you.  Read them thoroughly and take them to heart.  You are forbidden from reading post-mortems from the current year.  Post-mortems from any other year are fair game.

We’re not participating in an actual Battlecode tournament, we’re practicing.  In an actual tournament, you would have two sources of data:  local fights against old versions of yourself, and online scrimmages against a variety of opponents in the tournament standings.  We can’t perfectly replicate this latter source of data, but we should try to get as close as possible. 
Please do a thorough check of the web, especially github, for competitor bots from the relevant year that are publicly accessible.  Download all of them to serve as your benchmark.  You may not read their code, except to initially verify that they don’t pose any security risk, but you are encouraged to analyze their tactics in games.

Build a replica of the official Battlecode judging infrastructure using galaxy as a base.  You will use this infrastructure for your online scrimmages.  Enter your current competitor and the downloaded bots in the ladder and challenge bots slightly better and worse than you to scrimmages.  In the spare VM cycles, have random bots on the ladder do the same.  You are only allowed to play benchmark bots via the replica.  You can play your own bots any way you like.  Ensure that none of this work has any effect on the official Battlecode infrastructure.

When you have thoroughly read all recommended repositories, formulate your own TRAINING_ALGORITHM.md file, based on best practices from previous years.  This file should be concise, complete, and formulated in year-agnostic terms.

You should start by building a strong, robust foundation in the basics:  good economy management; ensuring that your bots can move freely and efficiently to their destinations without getting stuck; board exploration; exploiting map symmetries; effective combat; and ensuring no bytecode overruns.  These basics are fundamental.  If you don’t have them right, nothing built on top of them will be effective.  Invest time at the beginning in building a good code architecture and good tools for understanding everything that happens in a game replay file.  Ensure that all moves your bot makes are symmetric when switching sides.  If your enemy effectively uses a tactic against you, adopt that tactic.  Generate graphs that illustrate your progress, and keep them up to date.  Write comprehensive unit tests for the bot and all tooling, keep them up to date, and run them after every change.

Make sure that your attempts are a good combination of incremental tweaks and big swings.  If you get stuck for ideas, review principles that have worked in other years.  There will be times when no attempts are successful for a long period.  At those times, it’s important to keep trying new things, and to not give up.  If you believe that a complete rewrite will help, then you should do so.  If you believe in an idea, it’s worth temporarily getting worse as you perfect it, if you expect to get better in the end.  AT NO TIME SHOULD YOU STOP AND WAIT FOR ME TO GIVE YOU A NEW IDEA.

Starting with this one, save all of my prompts in a document called PROMPTS.md.  Note that the user is in the PDT timezone.

This year we will compete again in Battlecode 2025.  Store all results in a new Github repository called battlecode25b-vibe.  Start from scratch, and do not look into or reuse anything from the original battlecode25-vibe, except that you may add the original battlecode25-vibe bot to your benchmark.  The purpose of this iteration is to see how much we’ve improved since the last time we tried that year, so reusing any learnings from the previous effort would taint the findings.  Download the rules and begin.

## #2 (2026-11-25 ~08:00 PDT)

I like the local tournament configuration we used in battlecode26b-vibe.  I'd like this setup to be like that one

## #3 (2026-11-25 08:55 PDT)

I'd like you to schedule a prod every 20 minutes that reports on the current state of the local tournament, replica, and things like disk usage

## #4 (2026-11-25 09:04 PDT)

Clean out all VM disk under 2026b, bc26b, and bc26a0

## #5 (2026-11-25 09:14 PDT)

Please start a graph in progress/ to track the Elo ratings of the local tournament champions, using wallclock time on the x axis.  Keep it up to date as part of crowning a new champion

## #6 (2026-11-25 10:44 PDT)

New that we're above 1000 Elo on the replica, let's start a graph showing our replica Elo versus wallclock time.  Also include lines for the Elo of the 15th, 10th, 5th and 1st place bots.  Don't include any data points before now

## #7 (2026-11-25 12:19 PDT)

Can you add a panel to replica-elo.png to plot the current Elo minus the Elo for #15, #10, #5 and #1?

## #8 (2026-11-25 15:40 PDT)

Do not put a non-champion on the replica.  Instead, learn to employ the enemy's tactics

## #9 (2026-11-25 15:41 PDT)

If they're truly beating us, then it should win in our local tournament

## #10 (2026-11-25 16:41 PDT)
How about in replica-elo.png you use the vertical lines to mark the champions that had an especially high improvement in local Elo score?

## #11 (2026-11-25 16:42 PDT)
Also, the table in local-elo.md is stale

## #12 (2026-11-25 18:15 PDT)
From now on, let's use the t prefix to indicate a bot that arose from imitating an enemy tactic

## #13 (2026-11-25 20:54 PDT)
Please add a line for 20th place to replica-elo.png, and also one for our previous 2025 bot attempt

## #14 (2026-11-25 21:03 PDT)
I'd like you to do an audit of ReplayDump to verify that it's capable of extracting all the information from a replay that is available

## #15 (2026-11-25 21:34 PDT)
I'd also like you to make a pass over recent games to see if any of our units are not pulling their weight, and if so, track down why

## #16 (2026-11-26 06:10 PDT)
Good morning!  How was it overnight?

## #17 (2026-11-26 06:15 PDT)
Based on what I see in the replay-elo graph, y74 seems to be the pivot that moved us from tracking #20 to tracking #15

## #18 (2026-11-26 06:20 PDT)
No, that's fine, thanks.  By the way, are there any features of Claude Code that we aren't using that would make you more effective in doing Battlecode?

## #19 (2026-11-26 06:22 PDT)
Yes, please do.  5 also sounds like a cool feature, but only if you have the time

## #20 (2026-11-26 06:46 PDT)
Looks good!  Do we really have all-new challengers this round?

## #21 (2026-11-26 07:41 PDT)
Can you give me a sense for how the different Opus 5.5 effort levels (Low-Max, plus Ultracode) affects your effectiveness in building a world champion Battlecode bot?

## #22 (2026-11-26 07:43 PDT)
Is there any way to automatically adjust effort level to the task at hand?  It's not really practical for me to keep doing the adjustments manually

## #23 (2026-11-26 07:48 PDT)
Re #1:  Yes, please switch it over
Re #2:  I've now run slash hooks in the CLI

## #24 (2026-11-26 09:19 PDT)
On the dashboard, right after the Replica Elo graph, can you insert a version of the second panel of replica-elo.png, and also a version of local-elo.png?

## #25 (2026-11-26 09:27 PDT)
Looks great!  Two requests:  First, can you make the zero line more prominent in the second graph?  I can barely see it, but it's an important reference.  Second, can you align the timestamps so that the local and replica tournament graphs are comparable, horizontally?

## #26 (2026-11-26 09:36 PDT)
Can you show me a scatterplot of local Elo vs. replica Elo at a set of timestamps?

## #27 (2026-11-26 09:40 PDT)
Let's remove any points from the early ramp-up phase, and lag the replica timestamp by an hour to allow for the champion's effect to be reflected in the replica Elo

## #28 (2026-11-26 09:43 PDT)
Let's leave the overnight problem alone for now.  I like the simplicity of our current setup, and the counterintuitive motion in the scatterplot is an interesting artifact

## #29 (2026-11-26 09:46 PDT)
Also, please add the graph to the dashboard, right after the Local Elo chart

## #30 (2026-11-26 09:52 PDT)
Can you get the aspect ratio of the scatterplot in the dashboard to be more square?

## #31 (2026-11-26 10:34 PDT)
I don't think the shading of the dots in the scatterplot by recency is buying us much.  Let's just keep them all at max brightness.  And can you also increase the brightness of the edges, so that we can see the motion better?

## #32 (2026-11-26 13:42 PDT)
What was the bot name where you decided to start clearing out the tournament after every coronation of a new champion?  We seem to be doing quite well on the replica recently, and I wonder if that decision is responsible

## #33 (2026-11-26 13:48 PDT)
Seems like a good idea, regardless

## #34 (2026-11-26 15:50 PDT)
Can you give me a heat map comparing local Elo delta versus replica Elo delta 1 hour later?

## #35 (2026-11-26 15:55 PDT)
Regarding your suggestion:  Yeah, let's keep a permanent slot open in the local tournament for whatever bot holds the replica record, providing it's not already there

## #36 (2026-11-26 16:01 PDT)
Is it possible, on top of the heatmap, to plot the average delta replica Elo per delta local Elo bucket?

## #37 (2026-11-26 16:04 PDT)
Actually, let's get rid of the heatmap, and just have the graph of average delta replica Elo, with vertical error bars.  Also an x-y axis

## #38 (2026-11-26 16:09 PDT)
Can we do a statistical test of the hypothesis that positive, but not too positive, local Elo gains lead to replica Elo losses?

## #39 (2026-11-26 16:12 PDT)
Agreed on your caveat.  Maybe we can pre-register a hypothesis and see if it holds out for future champions in a few days from now

## #40 (2026-11-26 16:17 PDT)
Instead of marking t91 as Behind on the dashboard, let's just keep the status as "Best Replica"

## #41 (2026-11-26 16:21 PDT)
Let's put "Best Replica" in blue to make it stand out

## #42 (2026-11-26 16:28 PDT)
Best Replica looks good now.  That was a good idea of yours, to keep the institutional knowledge in the local tournament at all times

## #43 (2026-11-26 16:33 PDT)
There must be a lot of literature comparing performance on self-play versus performance vs. a set benchmark.  Anything there that we can use?

## #44 (2026-11-26 16:38 PDT)
I like option #1, but I'm worried it won't give us much signal, since we'll generally trounce older versions of ourselves.  Best replica at least has the implicit knowledge of how to beat the field

## #45 (2026-11-26 16:43 PDT)
Yes, let's.  I have a mild worry that bots that close together in time will largely be correlated, but it's probably worth the extra work on the box

## #46 (2026-11-26 16:45 PDT)
I'm also open to option #3, as long as we don't get so strict that we start throwing away bots that might be improvements

## #47 (2026-11-26 17:22 PDT)
I'm having second thoughts on the amount of games you want to allocate to the "vs refs" column.  Let's get rid of the column, and just treat the refs are regular, but permanent, entrants in the tournament

## #48 (2026-11-26 17:24 PDT)
I'm good with your option 3, as stated.  If the anomalous dip in the delta Elo chart is truly caused by the winner's curse, this should alleviate that.  Let's see if it does

## #49 (2026-11-26 17:29 PDT)
There's an error in the Confirming status.  It's showing NaN/NaN instead of 0/150

## #50 (2026-11-26 18:09 PDT)
Let's make sure that TRAINING_ALGORITHM is up to date with the new approach

## #51 (2026-11-26 19:12 PDT)
Go ahead

## #52 (2026-11-26 19:58 PDT)
I'd like the 3 Best Replica bots to be in addition to the 10 bots normally in the tournament, so our new target size is ~13 bots

## #53 (2026-11-26 20:05 PDT)
You probably also want to rebucket the delta Elo graph now that the local Elo values are fixed

## #54 (2026-11-27 06:06 PDT)
Good morning!  Looks like we had a case of diminishing returns last night

## #55 (2026-11-27 06:18 PDT)
OK, then yeah, I don't think we're going to tune our way to #1.  One of two things are likely:  Either the 8 bots above us know how to do things we need to learn how to do, or we have some bugs accumulated that are acting as a drag. Can you also do an audit on the code?  There might be a bug, or the code might have gotten unwieldy enough to be difficult to alter

## #56 (2026-11-27 06:22 PDT)
That all sounds good to me

## #57 (2026-11-27 06:51 PDT)
(answer to "may a verified behaviour-identical refactor become the base for new candidates without being crowned?") R1-R3 now
