#!/usr/bin/env python3
"""
CSV receiver – Pyrogram user-session
Listens for private documents and saves them as user_<uid>.csv
"""

import os, asyncio, csv, logging
from pyrogram import Client, filters
from pyrogram.types import Message

# --------------------------- env ---------------------------------------------
API_ID          = int(os.ge"API_ID"))
API_HASH        = os.getenv("API_HASH")
SESSION_STRING  = os.getenv("SESSION_STRING")
OWNER_ID        = int(os.getenv("OWNER_ID"))   # your user-id (decimal)

# --------------------------- logging -----------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
log = logging.getLogger("csv_receiver")

# --------------------------- client ------------------------------------------
app = Client(
    "csv_receiver",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    no_updates=False
)

# --------------------------- handler -----------------------------------------
@app.on_message(filters.private & filters.document & filters.user(OWNER_ID))
async def handle_csv(client: Client, msg: Message):
    log.debug("Update received: %s", msg)
    doc = msg.document
    log.info("Document from %s: %s (%s bytes)", msg.from_user.id, doc.file_name, doc.file_size)

    # basic mime / extension check
    if not (doc.mime_type == "text/csv" or str(doc.file_name).lower().endswith(".csv")):
        await msg.reply("❌  Send a CSV file (pipe-separated).")
        return

    target = f"user_{msg.from_user.id}.csv"
    await msg.reply("📥  Downloading …")
    await client.download_media(doc.file_id, file_name=target)

    # quick validation
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

# --------------------------- main --------------------------------------------
async def main():
    log.info("Starting Pyrogram client …")
    await app.start()
    me = await app.get_me()
    log.info("Authorised as %s (id=%s  dc=%s)", me.first_name, me.id, me.dc_id)

    # poke the server so updates start flowing
    await app.send_message("me", "👂  CSV receiver is on-line")
    log.info("CSV receiver is listening for documents …")
    await asyncio.Event().wait()          # run forever

if __name__ == "__main__":
    asyncio.run(main())
