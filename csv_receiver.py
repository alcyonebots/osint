#!/usr/bin/env python3
"""
Download the first CSV document sent by user-id 8034717776
Pyrogram v2 – session-string login – no local session file
"""

import os
import sys
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# --------------- config ------------------------------
SESSION_STRING = "BQGz0ToADlcmxsZ0IAhuXo-4Tl097Ky2F0KRiiqLn-waTjHZSlBifaPX_smVd53hjvi1_PIbwXT3HGzTLBdYKO-7gRo2X0mjJC7p1zhXPcSi4WbXioPhd2RhV97ox1l05rszNfwEmcQPAVwsDaBNV8aBoW_5i8Gj7HUwSiMjEqoLHPxrOdlEJRAxvXmwwkBDD9wO-qtmucMmrnA3dmVTIsghlA1oi_P4l7C_7GwbZqFCv6YzS4x1PTvypazusrTqn86SLogHSaZ2YbTiBsA2CcbhhZsAbqWzj-fCz0qO29KHxAHKiFl6ynUErrg7i6FCXkH_VjpRx3dRpjgvoFs756vAkt6WlAAAAAG_DEnxAA"
TARGET_USER_ID = 8034717776          # <-- user-id, not phone
DOWNLOAD_FOLDER = os.getcwd()        # repo root (change if you want)
# -----------------------------------------------------

if not SESSION_STRING:
    sys.exit("Env-var TG_SESSION_STRING is missing")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Client(
    "csv_bot",
    session_string=SESSION_STRING,
    no_updates=False
)

@app.on_message(filters.document & filters.user(TARGET_USER_ID))
async def catch_csv(_, msg: Message):
    doc = msg.document
    if not doc.file_name.lower().endswith(".csv"):
        return                                   # ignore non-csv

    logging.info("CSV found → %s", doc.file_name)
    target_path = os.path.join(DOWNLOAD_FOLDER, doc.file_name)
    await app.download_media(doc, file_name=target_path)
    logging.info("Saved → %s", target_path)

    # stop after first success (remove these two lines to stay alive)
    await app.stop()
    sys.exit(0)

if __name__ == "__main__":
    app.run()
