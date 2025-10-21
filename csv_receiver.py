#!/usr/bin/env python3
"""
Pyrogram side-car – listens to your user-account and saves incoming CSV files.
"""

import os, asyncio, csv
from pyrogram import Client, filters
from pyrogram.types import Message
from settings import make_pyrogram_client, ACCOUNT_USER_ID

app = make_pyrogram_client()

ACCOUNT_USER_ID = 8034717776

@app.on_message(filters.private & filters.document)
async def handle_csv(_, msg: Message):
    # accept only from yourself (remove filter if you want anyone)
    if msg.from_user and msg.from_user.id != ACCOUNT_USER_ID:
        return

    doc = msg.document
    if not (doc.mime_type == "text/csv" or doc.file_name.endswith(".csv")):
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
        return

    await msg.reply("✅  CSV saved and indexed.  You can now use /who in the bot.")
    print(f"[+]  {target}  updated")

async def main():
    print("[+]  CSV receiver started – listening for documents …")
    await app.start()
    await asyncio.Event().wait()          # run forever

if __name__ == "__main__":
    asyncio.run(main())
    
