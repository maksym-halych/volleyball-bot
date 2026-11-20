"""Log in to Telegram once on your own computer and print a session string.

Store the printed string as the TG_SESSION Actions secret. It gives full access
to the Telegram account, so never commit it or share it.
"""

import os

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = int(os.environ.get("TG_API_ID") or input("api_id: "))
api_hash = os.environ.get("TG_API_HASH") or input("api_hash: ")
phone = os.environ.get("TG_PHONE") or input("phone (e.g. +380...): ")

client = TelegramClient(StringSession(), api_id, api_hash).start(phone=phone)
print("\nTG_SESSION:\n")
print(client.session.save())
client.disconnect()
