import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from telethon import TelegramClient, events, errors
from telethon.tl.functions.channels import JoinChannelRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MonitorBot")

# Session for user account
client = TelegramClient("user_monitor_session", API_ID, API_HASH)

# File paths
GROUP_FILE = "group.txt"
STATE_FILE = "state.json"
SLANG_FILE = "slang.txt"
EMOJI_FILE = "emoji.txt"
ALERT_LOG = "alerts.log"

# Load slang and emoji lists
def load_list(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"{file_path} not found, skipping.")
        return []

SLANG_WORDS = load_list(SLANG_FILE)
EMOJIS = load_list(EMOJI_FILE)

alert_counts = {}

def log_alert(chat_title, message, trigger):
    """Save alert to log file and update count."""
    count = alert_counts.get(chat_title, 0) + 1
    alert_counts[chat_title] = count

    log_entry = (
        f"[ALERT] Group: {chat_title} | "
        f"Trigger: {trigger} | "
        f"Message: {message} | "
        f"Total Flags in this Group: {count}\n"
    )

    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

    logger.warning(log_entry.strip())

# Monitor messages
@client.on(events.NewMessage())
async def handler(event):
    if not (event.is_group or event.is_channel):
        return

    chat = await event.get_chat()
    chat_title = getattr(chat, "title", "Unknown Chat")
    text = event.message.message or ""

    # Check slang words
    for slang in SLANG_WORDS:
        if slang in text:
            log_alert(chat_title, text, slang)
            return

    # Check emojis
    for emoji in EMOJIS:
        if emoji in text:
            log_alert(chat_title, text, emoji)
            return

# Manage state file for joining groups
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_index": -1, "last_join_date": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

async def join_next_group():
    state = load_state()
    last_index = state["last_index"]
    last_join_date = state["last_join_date"]

    today = datetime.now().date()
    if last_join_date == str(today):
        logger.info("✅ Already joined a group today. Skipping...")
        return

    # Load group links
    try:
        with open(GROUP_FILE, "r") as f:
            groups = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error("❌ group.txt not found.")
        return

    next_index = last_index + 1
    if next_index >= len(groups):
        logger.info("✅ All groups processed.")
        return

    group_link = groups[next_index]
    logger.info(f"➡️ Trying to join: {group_link}")

    try:
        await client(JoinChannelRequest(group_link))
        logger.info(f"🎉 Successfully joined: {group_link}")

        # Update state
        state["last_index"] = next_index
        state["last_join_date"] = str(today)
        save_state(state)

    except errors.FloodWaitError as e:
        logger.warning(f"⚠️ Rate limit. Sleeping {e.seconds} sec...")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"❌ Failed to join {group_link}: {e}")

async def main():
    logger.info("🚀 Starting Telegram user client...")
    await client.start()

    # Try joining one group per day
    await join_next_group()

    # Show monitored groups
    dialogs = await client.get_dialogs()
    logger.info("✅ Monitoring the following groups/channels:")
    for d in dialogs:
        if d.is_group or d.is_channel:
            logger.info(f"   - {d.title}")

    logger.info("⚡ Ready! Waiting for suspicious messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Monitoring stopped by user.")