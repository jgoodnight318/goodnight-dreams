#!/usr/bin/env bash
# Upload a staged Adobe batch over SFTP. Adobe Stock contributor SFTP: host sftp.contributor.adobe.com,
# username = your contributor login, password = the SFTP password shown in the contributor portal
# (Upload → "Upload via SFTP"). Files land in the portal's Uploaded Files with the CSV metadata applied.
#   ADOBE_SFTP_USER=... ADOBE_SFTP_PASS=... ./upload_adobe.sh <batch_dir>
set -euo pipefail
BATCH="${1:?batch dir}"
command -v lftp >/dev/null || { echo "install lftp (brew install lftp)"; exit 1; }
lftp -u "$ADOBE_SFTP_USER","$ADOBE_SFTP_PASS" sftp://sftp.contributor.adobe.com <<CMDS
set sftp:auto-confirm yes
mirror -R --only-newer "$BATCH" /
bye
CMDS
echo "uploaded $(ls "$BATCH" | wc -l | tr -d ' ') files"
