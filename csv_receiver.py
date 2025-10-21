#!/usr/bin/env python3
"""
CSV receiver – Pyrogram user-session
Listens for private documents and saves them as user_<uid>.csv
"""

import os, asyncio, csv, logging
from pyrogram import Client, filters
from pyrogram.types import Message

# --------------------------- env ---------------------------------------------
API_ID   = 28561722
API_HASH = "a538ba07656f746def99bed7032121cc"
OWNER_ID = 8034717776
SESSION_STRING = "BQGz0ToADlcmxsZ0IAhuXo-4Tl097Ky2F0KRiiqLn-waTjHZSlBifaPX_smVd53hjvi1_PIbwXT3HGzTLBdYKO-7gRo2X0mjJC7p1zhXPcSi4WbXioPhd2RhV97ox1l05rszNfwEmcQPAVwsDaBNV8aBoW_5i8Gj7HUwSiMjEqoLHPxrOdlEJRAxvXmwwkBDD9wO-qtmucMmrnA3dmVTIsghlA1oi_P4l7C_7GwbZqFCv6YzS4x1PTvypazusrTqn86SLogHSaZ2YbTiBsA2CcbhhZsAbqWzj-fCz0qO29KHxAHKiFl6ynUErrg7i6FCXkH_VjpRx3dRpjgvoFs756vAkt6WlAAAAAG_DEnxAA"   # <-- paste here or .env
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
