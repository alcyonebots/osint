"""Shared between bot and receiver"""
import os
from pyrogram import Client

API_ID   = 28561722
API_HASH = "a538ba07656f746def99bed7032121cc"
SESSION_STRING = "BQGz0ToADlcmxsZ0IAhuXo-4Tl097Ky2F0KRiiqLn-waTjHZSlBifaPX_smVd53hjvi1_PIbwXT3HGzTLBdYKO-7gRo2X0mjJC7p1zhXPcSi4WbXioPhd2RhV97ox1l05rszNfwEmcQPAVwsDaBNV8aBoW_5i8Gj7HUwSiMjEqoLHPxrOdlEJRAxvXmwwkBDD9wO-qtmucMmrnA3dmVTIsghlA1oi_P4l7C_7GwbZqFCv6YzS4x1PTvypazusrTqn86SLogHSaZ2YbTiBsA2CcbhhZsAbqWzj-fCz0qO29KHxAHKiFl6ynUErrg7i6FCXkH_VjpRx3dRpjgvoFs756vAkt6WlAAAAAG_DEnxAA"   # <-- paste here or .env
BOT_TOKEN = "8008133840:AAEGM6EsCNfUJUQ6jZS12foIMpzX5NGAJ-U"

def make_pyrogram_client() -> Client:
    return Client(
        "csv_receiver",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        no_updates=False          # we *do* want updates
    )
  
