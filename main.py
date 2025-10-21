#!/usr/bin/env python3
"""
Private CSV lookup bot – each user uploads their own pipe-separated CSV
and queries it with /who <id|@username|phone>
"""

import csv, os, logging, tempfile
from telegram import Update, Document
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = "8008133840:AAEGM6EsCNfUJUQ6jZS12foIMpzX5NGAJ-U"

# ---------- encoding ---------------------------------------------------------
try:
    import chardet
except ImportError:
    raise SystemExit("pip install chardet")

def detect_encoding(path: str, sample_size: int = 50_000) -> str:
    with open(path, 'rb') as f:
        return chardet.detect(f.read(sample_size))['encoding'] or 'utf-8'

# ---------- per-user indexes -------------------------------------------------
USER_DB = {}   # user_id -> {by_id: {}, by_user: {}, by_phone: {}}

def csv_path(uid: int) -> str:
    return f"user_{uid}.csv"

def reload_user_db(uid: int) -> bool:
    """Rebuild indexes for one user. Return True on success."""
    path = csv_path(uid)
    if not os.path.exists(path):
        return False
    by_id, by_user, by_phone = {}, {}, {}
    enc = detect_encoding(path)
    with open(path, newline='', encoding=enc) as fh:
        next(fh)  # skip header
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

# ---------- conversation states ---------------------------------------------
AWAIT_CSV = 1

# ---------- start / help ------------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if update.effective_chat.type != update.effective_chat.PRIVATE:
        await update.message.reply_text("Please talk to me in private.")
        return
    if os.path.exists(csv_path(uid)):
        await update.message.reply_text(
            "Send /who <id|@username|phone> to query your CSV.\n"
            "Send /upload if you want to replace your file."
        )
    else:
        await update.message.reply_text(
            "Hello! Please upload your pipe-separated CSV first.\n"
            "Header: Name|Number|ID|Username|CreationDateUnixTS"
        )
        return AWAIT_CSV

# ---------- upload flow -------------------------------------------------------
async def upload_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the new CSV file (pipe-separated).")
    return AWAIT_CSV

async def receive_csv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    doc: Document = update.message.document
    uid = update.effective_user.id
    tmp = tempfile.NamedTemporaryFile(delete=False)
    await (await doc.get_file()).download_to_memory(tmp)
    tmp.close()
    # basic validation
    enc = detect_encoding(tmp.name)
    try:
        with open(tmp.name, newline='', encoding=enc) as fh:
            header = next(fh).strip()
            if header != "Name|Number|ID|Username|CreationDateUnixTS":
                raise ValueError("bad header")
            # try at least one row
            r = next(csv.reader(fh, delimiter='|'))
            if len(r) != 5:
                raise ValueError("bad row length")
    except Exception as e:
        os.remove(tmp.name)
        await update.message.reply_text(f"❌ Invalid file: {e}")
        return AWAIT_CSV
    # save permanently
    os.replace(tmp.name, csv_path(uid))
    reload_user_db(uid)
    await update.message.reply_text("✅ CSV saved and indexed.")
    return ConversationHandler.END

# ---------- lookup -----------------------------------------------------------
async def who(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in USER_DB:
        await update.message.reply_text("Upload your CSV first.")
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /who <id|@username|phone>")
        return
    q = ctx.args[0]
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
    app = Application.builder().token(TOKEN).build()

    # conversation for upload
    conv = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_cmd)],
        states={AWAIT_CSV: [MessageHandler(filters.Document.ALL, receive_csv)]},
        fallbacks=[]
    )
    app.add_handler(conv)
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
