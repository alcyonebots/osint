#!/usr/bin/env python3
"""
Private CSV lookup bot – /who <id|@username|phone>
Upload is now handled by the Pyrogram side-car.
"""

import csv, os, logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

from settings import BOT_TOKEN

# ---------- encoding ---------------------------------------------------------
try:
    import chardet
except ImportError:
    raise SystemExit("pip install chardet")

def detect_encoding(path: str, sample_size: int = 50_000) -> str:
    with open(path, 'rb') as f:
        return chardet.detect(f.read(sample_size))['encoding'] or 'utf-8'

# ---------- per-user indexes -------------------------------------------------
USER_DB = {}

def csv_path(uid: int) -> str:
    return f"user_{uid}.csv"

def reload_user_db(uid: int) -> bool:
    path = csv_path(uid)
    if not os.path.exists(path):
        return False
    by_id, by_user, by_phone = {}, {}, {}
    enc = detect_encoding(path)
    with open(path, newline='', encoding=enc) as fh:
        next(fh)  # header
        for row in csv.reader(fh, delimiter='|'):
            if len(row) != 5:
                continue
            name, number, tid, username, ts = row
            by_id[int(tid)] = row
            if username:
                by_user[username.lower().lstrip('@')] = row
            if number:
                by_phone[number] = row
    USER_DB[uid] = {"by_id": by_id, "by_user": by_user, "by_phone": by_phone}
    return True

# ---------- commands ---------------------------------------------------------
async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        await update.message.reply_text("Please talk to me in private.")
        return
    if os.path.exists(csv_path(uid)):
        await update.message.reply_text(
            "Send /who <id|@username|phone> to query your CSV.\n"
            "To update your file, send the new CSV to @YourUserAccount."
        )
    else:
        await update.message.reply_text(
            "No CSV found.  Please send your pipe-separated CSV to "
            "@YourUserAccount first (Name|Number|ID|Username|CreationDateUnixTS)."
        )

async def who(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in USER_DB and not reload_user_db(uid):
        await update.message.reply_text("Upload your CSV to @YourUserAccount first.")
        return
    if not _.args:
        await update.message.reply_text("Usage: /who <id|@username|phone>")
        return
    q = _.args[0]
    db = USER_DB[uid]
    row = None
    try:
        row = db["by_id"][int(q)]
    except ValueError:
        pass
    if not row:
        row = db["by_user"].get(q.lower().lstrip('@'))
    if not row:
        row = db["by_phone"].get(q)
    if not row:
        await update.message.reply_text("❌ Not found.")
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
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("help",  start, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("who",   who,   filters=filters.ChatType.PRIVATE))

    # preload existing user files
    for fname in os.listdir("."):
        if fname.startswith("user_") and fname.endswith(".csv"):
            uid = int(fname[5:-4])
            reload_user_db(uid)

    app.run_polling()

if __name__ == '__main__':
    main()
