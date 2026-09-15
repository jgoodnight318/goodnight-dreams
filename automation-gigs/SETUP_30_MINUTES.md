# Your part: 30 minutes, once

Platforms require a verified human to open a seller account and to press
"Deliver" on each order. Everything else is automated in this folder.

## A. Fiverr seller account (15 min)
1. fiverr.com → Join → use jms.goodnight@gmail.com (the intake poller
   reads this inbox). Become a Seller → complete the profile:
   - Display name: James G. · Occupation: Programming & Tech / AI Development
   - Description: paste the **Overview** from `listings/upwork/profile.md`
   - Skills: n8n, Automation, AI Agents, Python, API Integration
   - Phone verification: your cell.
2. Create Gig 1 → copy title, category, tags, packages, description, FAQ
   and requirements from `listings/fiverr/gig-1-n8n-workflow.md`.
   Gig image: use `../assets/covers/automation-gigs.png` once generated,
   or a plain dark image with the gig title (Fiverr requires 3 images;
   screenshots of the three portfolio workflows work).
3. Repeat for `gig-2-claude-agent.md` and `gig-3-automation-audit.md`.
4. Fiverr → Settings → Notifications: email ON for orders and messages.

## B. Upwork (10 min)
1. upwork.com → create freelancer profile with the same email.
   Paste title, rate, skills, overview from `listings/upwork/profile.md`.
   Add the 3 portfolio items (link each to its folder on GitHub).
2. Project Catalog → create the 3 projects in `listings/upwork/project-catalog.md`.
3. Turn on email notifications for messages and offers.

## C. Wire the poller to the Mac mini (5 min)
1. Google Account → Security → App passwords → create one named "gigs".
2. Create `~/.config/automation-gigs.env`:
   ```
   GIGS_IMAP_USER=jms.goodnight@gmail.com
   GIGS_IMAP_PASS=<the 16-char app password>
   GIGS_NOTIFY_TO=jms.goodnight@gmail.com
   ```
3. From this repo on the mini:
   ```
   cp automation-gigs/launchd/com.james.automation-gigs.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.james.automation-gigs.plist
   ```
   It polls every 15 minutes. Test: `python3 automation-gigs/pipeline/intake.py`.

## Per order (2 minutes, from your phone)
You get an email "[gigs] READY: <order>" with the delivery message and a
`deliverable.zip`. Open the order on Fiverr/Upwork → Deliver → paste the
message → attach the zip → send. If the email says NEEDS_INFO, forward the
listed questions to the buyer first; the poller re-runs when they answer.

Why this can't be zero: Fiverr and Upwork terms forbid bots operating a
seller account, and enforcement bans the account. The paste is the price
of keeping the account.
