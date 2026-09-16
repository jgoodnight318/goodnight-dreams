# Draft proposal — "AI Automation project" (daily revenue reports → QuickBooks Desktop Enterprise)
# Channel: Upwork. Draft only — James sends (costs Connects, speaks as him).

Hi — this is squarely what I build, so I'll be specific instead of generic.

Your daily flow, as I read it: a revenue report lands in a spreadsheet, and someone
has to open it, identify which entity each line belongs to, and key those revenues
into QuickBooks Desktop Enterprise. That last step is the tedious, error-prone one,
and it's exactly the kind of thing that's cheap to get 95% right and expensive to get
100% right — so I'd build it to be right.

How I'd approach it:
1. A watcher on the spreadsheet source (folder, email, or Drive — whatever you use)
   that triggers on each new daily report, so there's no "remember to run it" step.
2. A parsing + entity-matching pass (I use Claude here, as you prefer) that reads the
   sheet, maps each row to the correct QuickBooks entity/account, and — importantly —
   flags anything ambiguous for a 5-second human confirm instead of guessing. Silent
   wrong entries are the one failure mode that matters in accounting.
3. Posting into QuickBooks Desktop Enterprise. QB Desktop is local-only, so this is
   done via the QuickBooks SDK (qbXML through the Web Connector / QBFC) rather than a
   cloud API — I'll confirm your QB version and hosting (local vs. hosted desktop) up
   front, because that decides the exact integration path.
4. A daily log: what was posted, what was flagged, what was skipped — so you can trust
   it and audit it.

I'd want to see one real (redacted) sample report and your QuickBooks setup before
quoting a fixed number; from what you've described this is a small, well-scoped build,
not a big project. I can start with a paid diagnostic on one day's real report so you
see the entity-matching working on your actual data before committing to the full
automation.

Quick question so I can scope it exactly: is your QuickBooks Desktop running locally on
a Windows machine, or hosted (e.g. Right Networks)? That's the one detail that changes
the integration.

— James
