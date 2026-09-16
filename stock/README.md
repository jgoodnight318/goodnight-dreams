# stock — AI images on the stock marketplaces that accept them

Adobe Stock, Freepik and Vecteezy all accept generative-AI images in 2026 when they are labelled.
They have their own buyer search traffic, pay per download, and take a folder of files plus a CSV.
That makes stock the most mechanical income lane there is: generate, keyword, upload, repeat.

```
tag.py        Claude looks at each image and writes a title, 40–49 keywords and a category (~$0.05/image)
export.py         stages a batch folder + CSV in Adobe / Freepik / Vecteezy format; remembers what was exported
upload_adobe.sh   SFTP upload of a staged Adobe batch (lftp)
launchd/          nightly: keyword new images -> Adobe batch + upload -> Freepik batch
```

## Money, honestly
| | |
|---|---|
| Adobe Stock royalty on AI images | 33% of net; plan on ~$0.25 per download |
| Vecteezy free program | $5 per 1,000 downloads (photos/vectors), $10 per 1,000 (video) |
| Freepik | per-download, paid monthly, AI accepted from any generator with the `_ai_generated` tag |
| Cost per image | generation (yours) + ~$0.05 keywording |

Stock is a volume game: contributors who report hundreds of dollars a month have thousands of
accepted assets. Expect the first payout in month two or three, then compounding. Wallpapers,
abstract backgrounds, textures and ambient scenes are exactly what these libraries lack in
volume, and the Mac mini already produces them.

## One-time setup (about 30 minutes, each needs a tax form for payout)
1. **Adobe Stock contributor** (contributor.stock.adobe.com): create account, tax + payout info.
   Upload → *Upload via SFTP* shows the SFTP username/password; put them in `~/.config/stock.env`
   as `ADOBE_SFTP_USER` / `ADOBE_SFTP_PASS`. After each batch lands, open Uploaded Files, select
   all, tick **Created using generative AI tools**, submit. (This tick cannot be set by CSV.)
2. **Freepik contributor** (contributor.freepik.com): account + tax; bulk upload accepts the
   `freepik.csv` written by `export.py` (the `ai_generated` column sets the required tag).
3. **Vecteezy contributor** (vecteezy.com/contributors): apply; upload via their portal with `vecteezy.csv`.
4. `STOCK_IMAGES_DIR` in `stock.env` = the folder your image pipeline writes finished 4K images to.
5. `brew install lftp`, copy the plist to `~/Library/LaunchAgents/`, `launchctl load` it.

## Rules the pipeline enforces
- Title 5–200 chars, no brand names, no "AI" in the title (the flag is a separate field).
- Max 49 keywords, lowercase, deduplicated, most relevant first.
- Every asset flagged AI-generated. Unlabelled AI content gets accounts terminated.
- No real people, logos, or copyrighted characters (your generator prompts must avoid them too).

## Try it
```
python3 stock/tag.py /path/to/images --limit 5
python3 stock/export.py /path/to/images --target adobe --out /tmp/adobe-batch
```
