# pinterest — the traffic engine for the Gumroad catalog

Gumroad has no search traffic (its Discover feed needs $100 of prior sales, and the catalog has
$0). Pinterest is the one channel where wallpaper and aesthetic-product searches are native, pins
keep surfacing for months, and posting is allowed through an official API. This job posts four
pins a day, rotating through every live product with a fresh angle each time, linking straight to
the Gumroad product with the existing cover art as the image.

Setup, once (no identity documents, about 10 minutes):
1. pinterest.com → create a **business** account with the Goodnight Dreams brand. Create one board
   ("Ambient wallpapers & sleep sounds"). Copy the board id from the URL or the API.
2. developers.pinterest.com → My apps → Create app → request Trial access (form, same day) →
   generate an access token with scopes `pins:write`, `boards:read`.
3. `~/.config/pinterest.env`:
   ```
   PINTEREST_ACCESS_TOKEN=...
   PINTEREST_BOARD_ID=...
   ```
4. `cp pinterest/launchd/com.james.pinterest-daily.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.james.pinterest-daily.plist`

Test without an account: `python3 pinterest/pin.py --dry-run` writes the pins to `pinterest/queue/`.

Expectation, per the 2026 sources: pins compound slowly; first meaningful clicks in 4–8 weeks,
not days. Trial API access is capped at a few pins a day, which is what this job does anyway.
