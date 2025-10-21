#!/usr/bin/env python3
"""
Pyrogram side-car – listens to your user-account and saves incoming CSV files.
"""

import os, asyncio, csv, logging
from pyrogram import Client, filters
from pyrogram.types import Message
from settings import make_pyrogram_client, ACCOUNT_USER_ID

# -------------- logging -------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,                   # DEBUG = everything
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
log = logging.getLogger("csv_receiver")

# -------------- client --------------------------------------------------------
app = make_pyrogram_client()

@app.on_message(filters.private & filters.document)
async def handle_csv(_, msg: Message):
    log.debug("Update received: %s", msg)
    if msg.from_user and msg.from_user.id != ACCOUNT_USER_ID:
        log.debug("Skipping – wrong user %s", msg.from_user.id)
        return

    doc = msg.document
    log.info("Document from %s: %s (%s bytes)",
             msg.from_user.id, doc.file_name, doc.file_size)

    if not (doc.mime_type == "text/csv" or str(doc.file_name).lower().endswith(".csv")):
        await msg.reply("❌  Send a CSV file (pipe-separated).")
        return

    target = f"user_{msg.from_user.id}.csv"
    await msg.reply("📥  Downloading …")
    await app.download_media(doc.file_id, file_name=target)

    # quick sanity check
    try:
        with open(target, newline='', encoding='utf-8') as fh:
            next(csv.reader(fh, delimiter='|'))
    except Exception as e:
        os.remove(target)
        await msg.reply(f"❌  File malformed: {e}")
        log.warning("Malformed CSV removed: %s  (%s)", target, e)
        return

    await msg.reply("✅  CSV saved and indexed.  You can now use /who in the bot.")
    log.info("Saved and indexed: %s", target)

# -------------- main ----------------------------------------------------------
async def main():
    log.info("Starting Pyrogram client …")
    await app.start()
    me = await app.get_me()
    log.info("Authorised as %s (id=%s  dc=%s)",
             me.first_name, me.id, me.dc_id)
    log.info("CSV receiver is listening for documents …")
    await asyncio.Event().wait()          # run forever

if __name__ == "__main__":
    asyncio.run(main())
