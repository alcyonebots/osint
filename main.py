#!/usr/bin/env python3
"""
Telegram CSV lookup bot – /who <id|@username|number>
Author : you
"""

import csv, os, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN     = "8008133840:AAEGM6EsCNfUJUQ6jZS12foIMpzX5NGAJ-U"
CSV_PATH  = "telegram_users.csv"          # <-- change if elsewhere

# ---------- in-memory index --------------------------------------------------
by_id = {}        # int  -> row(list)
by_user = {}      # str  -> row(list)   (key stored lower-cased, no @)
by_phone = {}     # str  -> row(list)

def reload_db():
    """Rebuild all indexes from disk."""
    by_id.clear(); by_user.clear(); by_phone.clear()
    with open(CSV_PATH, newline='', encoding='utf-8') as fh:
        next(fh)                      # skip header
        for row in csv.reader(fh, delimiter='|'):
            if len(row) != 5:
                continue              # malformed line
            name, number, tid, username, ts = row
            by_id[int(tid)] = row
            if username:
                by_user[username.lower().lstrip('@')] = row
            if number:
                by_phone[number] = row
    logging.info("DB reloaded: %d id, %d username, %d phone entries",
                 len(by_id), len(by_user), len(by_phone))

# ---------- command handler --------------------------------------------------
async def who(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: /who <id|@username|phone>")
        return
    q = ctx.args[0]

    row = None
    try:                       # 1. try as user-id
        row = by_id[int(q)]
    except ValueError:
        pass
    if not row:                # 2. try as username
        row = by_user.get(q.lower().lstrip('@'))
    if not row:                # 3. try as phone
        row = by_phone.get(q)
    if not row:
        await update.message.reply_text("❌ Not found in database.")
        return

    name, number, tid, username, ts = row
    await update.message.reply_text(
        f"Name : {name}\n"
        f"Phone: {number}\n"
        f"ID   : {tid}\n"
        f"User : {username or '(none)'}\n"
        f"TS   : {ts}"
    )

# ---------- main -------------------------------------------------------------
def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    reload_db()                       # initial load
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("who", who))
    app.run_polling()

if __name__ == '__main__':
    main()
  
