#!/usr/bin/env python3
"""
Listens to *your* user-account; when a private document arrives
it saves it as user_<sender-id>.csv and notifies the console.
"""

import asyncio, csv, os
from settings import make_pyrogram_client
from pyrogram import filters
from pyrogram.types import Message

ACCOUNT_USER_ID = int(os.getenv("ACCOUNT_USER_ID"))  # your own user-id

@make_pyrogram_client()
async def recv(app):
    @app.on_message(filters.private & filters.document)
    async def handle(_, msg: Message):
        # accept only from yourself (or remove filter to accept from anyone)
        if msg.from_user and msg.from_user.id != ACCOUNT_USER_ID:
            return
        doc = msg.document
        # basic sanity – must be text/csv or filename ends with .csv
        if not (doc.mime_type == "text/csv" or doc.file_name.endswith(".csv")):
            await msg.reply("❌  Send a CSV file (pipe-separated).")
            return
        target = f"user_{msg.from_user.id}.csv"
        await msg.reply("📥  Downloading …")
        await app.download_media(doc.file_id, file_name=target)
        # quick validation
        try:
            with open(target, newline='', encoding='utf-8') as fh:
                next(csv.reader(fh, delimiter='|'))
        except Exception as e:
            os.remove(target)
            await msg.reply(f"❌  File malformed: {e}")
            return
        await msg.reply("✅  Saved and indexed.  You can now use /who in the bot.")
        print(f"[+]  {target}  updated")

    print("[+]  CSV receiver started – listening for documents …")
    await asyncio.Event().wait()  # run forever

if __name__ == "__main__":
    asyncio.run(recv())
              
