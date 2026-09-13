# Zoom meeting talking script
*Read naturally, conversational. ~7–8 minutes, leaving plenty of time for discussion. Cues in [brackets] are for you, not to read aloud.*

---

**[Opening — before sharing slides]**

Hi Professor Poast, thanks so much for making the time. Before we dive in — we've put together a short update on the arms-supplier overlap project, just to walk you through where we are and get your read on whether the results hold up. It should only take about ten minutes, and then we'd love to open it up for your feedback. We were also hoping to use a few minutes at the end to talk briefly about the first draft of Jerry's paper, if that works for you.

Let me share my screen.

**[Slide 1 — Title]**

So this is the project we discussed earlier — "Strategic Symmetry," on arms-supplier overlap and the onset of militarized disputes. Jerry and I have been working on it together over the summer.

**[Slide 2 — Motivation & contribution]**

The basic question is simple: when two countries buy their weapons from the same set of suppliers, are they less likely to get into a militarized dispute with each other?

The contribution is mostly in how we look at it. Most of the arms-transfers literature is monadic — it asks whether a given country arms up. We instead look at it dyadically, as a network: how much two countries' supplier portfolios overlap. We've taken it global, 1990 to 2014, and we find there's actually quite a bit of regional variation.

The thing we've spent the most time on is identification. The obvious worry — and I'm sure this is your first reaction too — is that overlap might just be a proxy for being in the same bloc. So a lot of what I'll show is us trying to rule that out.

**[Slide 3 — Data]**

Quickly on the data. The core independent variable comes from the full SIPRI trade register — every supplier-to-recipient deal globally. The outcome is dispute onset, which we build from MID 5.0. And then we pulled in the standard controls — regime type from V-Dem, capabilities, alliances, contiguity, capital distance, bilateral trade — plus UN voting ideal points, which become important for the identification. Everything's harmonized to Correlates of War country codes.

**[Slide 4 — Measurement]**

Two quick definitions. Overlap is just the share-weighted similarity of two countries' supplier portfolios — it's one if they buy from exactly the same mix, zero if they share no suppliers. And we lag it a year. Onset is tie formation — a new dispute that wasn't there the year before, so we're modeling escalation, not persistence. The panel is about 134,000 dyad-years, and onset is rare — about half a percent.

**[Slide 5 — Descriptive overview]**

This is just to give a feel for the data. The main thing to flag is the right-hand panel: arms-import coverage is uneven, so overlap is really only meaningful where countries actually buy major weapons — strong in the Middle East and Asia-Pacific, thin in Sub-Saharan Africa. That shapes how much we trust each region.

**[Slide 6 — Empirical strategy]**

The strategy is: start with a pooled logit with clustered standard errors and the full control set; then look region by region; and then throw the identification tests at it. We've also got region-level network models — TERGMs — planned as a robustness check.

**[Slide 7 — Result 1]**

Here's the headline. Globally, with all the controls in, the odds ratio on overlap is about 0.29 and it's highly significant. So more overlap, substantially lower odds of a new dispute — and it's not being driven by distance, alliances, trade, regime, or capabilities. This is the result we wanted to make sure is actually valid before we lean on it.

**[Slide 8 — Result 2]**

But it's not uniform. When we split by region, it's strongly negative globally and in most regions, but Asia-Pacific is basically a null. We actually think that heterogeneity is a feature, not a bug — overlap seems to act as a constraint in some arms markets and not others, and that's something worth explaining.

**[Slide 9 — Identification I]**

Now the part we'd most like your reaction to. Is overlap just alignment in disguise? First, overlap and UN-voting distance are basically uncorrelated to begin with — minus 0.03. Second, when we add UN ideal-point distance as a direct control, the overlap effect doesn't weaken — it actually gets a touch stronger. And third, on the right, we run dyad fixed effects, which absorbs any time-invariant bloc membership entirely. The effect survives — odds ratio 0.335. So within the same pair of countries, when their overlap rises over time, their dispute risk falls.

**[Slide 10 — Identification II]**

Then we go further and look only at dyads that are clearly not aligned — no defense pact, and far apart in UN voting. Even there, overlap still predicts fewer disputes, odds ratio about 0.28, significant. So it really does seem to carry information beyond just being in the same camp.

**[Slide 11 — Identification III, construction]**

And the piece we're most excited about — a shift-share, or Bartik, instrument. The idea is to isolate the part of overlap that's driven by global supply trends rather than a country's own political choices. We fix each country's supplier mix in the 1980s, before our window, and then reweight it by how each supplier's global exports move over time, leaving out the country's own purchases. That gives us a predicted overlap that's plausibly exogenous to the dyad's politics.

**[Slide 12 — Identification III, results]**

And it works. The first stage is very strong — an F around 1,280, so no weak-instrument problem. The reduced form and the two-stage results both come through negative and significant. One thing we'd love your take on: the IV estimate is about five times the OLS, which to us suggests the simple correlation is, if anything, understating the effect — not inflated by reverse causality. But we want to make sure we're reading that right.

**[Slide 13 — Robustness & caveats]**

Finally, the honest caveats. The shift-share design rests on the global supply shocks only affecting conflict through overlap, which we'd like to probe more — dropping dominant suppliers, checking pre-trends. We're using a linear probability model on a rare outcome, so we want to add an IV probit. And the data stops in 2014 because of MID. Those are the main things on our list.

**[Closing]**

So that's where we are. The main questions for you are really: does the identification story feel convincing, especially the bloc-proxy concern and the instrument? And where would you push us next? And then, if there's time, we'd love to spend a few minutes on Jerry's draft. Thank you — we'd really value your thoughts.
