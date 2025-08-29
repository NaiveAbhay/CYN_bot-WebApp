import os
import re
import cv2
import asyncio
import logging
import random
import sys
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import (
    UsernameInvalidError, PeerIdInvalidError, PeerFloodError,
    FloodWaitError, ChatWriteForbiddenError
)

# ---------------- ENV + Logging ---------------- #
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("bot-monitor")

client = TelegramClient("bot_monitor_session", API_ID, API_HASH)

# ---------------- Patterns ---------------- #
BTC_REGEX = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
ETH_REGEX = r'\b0x[a-fA-F0-9]{40}\b'
USDT_REGEX = r'T[1-9A-HJ-NP-Za-km-z]{33}'
URL_REGEX = r'https?://[^\s]+|[a-zA-Z0-9-]+\.(onion|shop|market)'

def load_list(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

SLANG = load_list("slang.txt")
EMOJIS = load_list("emoji.txt")
MONITORED_BOT_IDS = set()

# ---------------- Alert System ---------------- #
def log_alert(bot_username, msg_type, triggers, content):
    log_line = f"[BOT ALERT] @{bot_username} | Type: {msg_type} | Triggers: {triggers} | Content: {content}\n"
    with open("bot_alerts.log", "a", encoding="utf-8") as f:
        f.write(log_line)
    log.warning(log_line.strip())

def log_failed(bot_username, reason):
    with open("failed_bots.log", "a", encoding="utf-8") as f:
        f.write(f"{bot_username} | {reason}\n")

# ---------------- Analyzers ---------------- #
async def analyze_text(bot_username, text):
    triggers = []
    for word in SLANG + EMOJIS:
        if word in text.lower():
            triggers.append(word)

    if re.search(BTC_REGEX, text): triggers.append("BTC")
    if re.search(ETH_REGEX, text): triggers.append("ETH")
    if re.search(USDT_REGEX, text): triggers.append("USDT")
    if re.search(URL_REGEX, text): triggers.append("Suspicious URL")

    if triggers:
        log_alert(bot_username, "text", triggers, text[:200])

def scan_qr(file_path):
    try:
        img = cv2.imread(file_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            return [data]
        return []
    except Exception as e:
        log.error(f"QR scan failed for {file_path}: {e}")
        return []

async def analyze_media(bot_username, event):
    try:
        file_path = await event.download_media(file="downloads/")
        log.info(f"📷 Media saved: {file_path}")

        qr_results = scan_qr(file_path)
        if qr_results:
            for qr in qr_results:
                log_alert(bot_username, "QR Code", ["QR detected"], qr)

    except Exception as e:
        log.error(f"❌ Error analyzing media from {bot_username}: {e}")

# ---------------- Interaction ---------------- #
START_COMMANDS = ["/start", "/menu", "/help", "/buy", "/order"]

async def interact_with_bot(username: str):
    try:
        if not username.startswith("@"):
            username = username.replace("https://t.me/", "@")

        entity = await client.get_entity(username)
        MONITORED_BOT_IDS.add(entity.id)
        log.info(f"🤖 Interacting with {username}")

        for cmd in START_COMMANDS:
            await client.send_message(entity, cmd)
            log.info(f"📩 Sent {cmd} to {username}")
            await asyncio.sleep(random.uniform(2, 4))
    
    except UsernameInvalidError:
        log.error(f"❌ Invalid username: {username}")
        log_failed(username, "Invalid username")
    except PeerIdInvalidError:
        log.error(f"❌ Could not resolve {username}")
        log_failed(username, "PeerIdInvalid")
    except ChatWriteForbiddenError:
        log.error(f"🚫 Cannot send messages to {username}")
        log_failed(username, "ChatWriteForbidden")
    except PeerFloodError:
        log.error(f"⚠️ PeerFloodError: rate limited. Waiting 1 min...")
        await asyncio.sleep(60)
        log_failed(username, "PeerFloodError")
    except FloodWaitError as e:
        log.error(f"⏳ FloodWaitError: wait {e.seconds} sec before retrying {username}")
        await asyncio.sleep(e.seconds + 5)
        log_failed(username, f"FloodWait {e.seconds}s")
    except Exception as e:
        log.error(f"❌ Unexpected error with {username}: {repr(e)}")
        log_failed(username, repr(e))

# ---------------- Global Message Handler ---------------- #
@client.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    if sender and sender.id in MONITORED_BOT_IDS:
        bot_username = getattr(sender, 'username', 'Unknown')
        log.info(f"Received message from @{bot_username}")
        if event.message.message:
            await analyze_text(bot_username, event.message.message)
        if event.message.media:
            await analyze_media(bot_username, event)

# ---------------- Main ---------------- #
async def main():
    await client.start()
    log.info("🚀 Bot monitor started...")

    bots_to_monitor = sys.argv[1:]

    if not bots_to_monitor:
        log.error("⚠️ No bots provided. Please run the script with bot usernames as arguments.")
        await client.disconnect()
        return

    for b in bots_to_monitor:
        await interact_with_bot(b)
        await asyncio.sleep(random.uniform(5, 10))  # slow down to avoid ban

    log.info("Finished sending initial commands. Waiting for bot responses...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())