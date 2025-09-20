import asyncio
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
from twilio.rest import Client as TwilioClient
import threading
import warnings

# =========================
# SUPPRESS WARNINGS
# =========================
warnings.filterwarnings("ignore", category=UserWarning, module="telethon")

# =========================
# CONFIGURATION & SETUP
# =========================
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Telegram recipient for alerts ("me" = Saved Messages, or @channelusername)
ALERT_RECIPIENT = os.getenv("TELEGRAM_ALERT_RECIPIENT", "me")

# Twilio WhatsApp setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g., whatsapp:+14155238886
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")              # e.g., whatsapp:+91XXXXXXXXXX

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MonitorBot")

# =========================
# CLIENT SETUP
# =========================
client = TelegramClient("user_monitor_session", API_ID, API_HASH)

# Initialize Twilio client
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =========================
# HELPER FUNCTIONS
# =========================
def load_list(file_path):
    """Loads a list of words/emojis from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"{file_path} not found, skipping.")
        return []

# Load slang and emoji lists
SLANG_WORDS = load_list("slang.txt")
EMOJIS = load_list("emoji.txt")

# Alert log file and in-memory count
ALERT_LOG = "alerts.log"
alert_counts = {}  # keeps per-group detection count

# =========================
# TELEGRAM ALERT FUNCTION
# =========================
async def send_telegram_alert(chat_title, message, trigger, total_flags):
    """Send flagged alerts to Telegram in the exact log format."""
    alert_text = (
        f"[ALERT] Group: {chat_title} | "
        f"Trigger: {trigger} | "
        f"Message: {message} | "
        f"Total Flags in this Group: {total_flags}"
    )
    try:
        await client.send_message(ALERT_RECIPIENT, alert_text)
        logger.info(f"Sent Telegram alert ✅ to {ALERT_RECIPIENT}")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

# =========================
# WHATSAPP ALERT FUNCTION (Twilio)
# =========================
def send_whatsapp_twilio(message):
    """Send flagged alerts to WhatsApp using Twilio."""
    if not (TWILIO_WHATSAPP_FROM and WHATSAPP_PHONE):
        logger.error("Twilio WhatsApp not configured properly.")
        return
    try:
        msg = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=message,
            to=WHATSAPP_PHONE
        )
        logger.info(f"Sent WhatsApp alert via Twilio SID={msg.sid}")
    except Exception as e:
        logger.error(f"Failed to send WhatsApp alert via Twilio: {e}")

# =========================
# LOG ALERT FUNCTION
# =========================
def log_alert(chat_title, message, trigger):
    """Logs alerts, updates count, and triggers notifications."""
    count = alert_counts.get(chat_title, 0) + 1
    alert_counts[chat_title] = count

    log_entry = (
        f"[ALERT] Group: {chat_title} | "
        f"Trigger: {trigger} | "
        f"Message: {message} | "
        f"Total Flags in this Group: {count}"
    )

    # Save to log file
    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

    logger.warning(log_entry)

    # Send Telegram alert asynchronously
    asyncio.create_task(send_telegram_alert(chat_title, message, trigger, count))

    # Send WhatsApp alert via Twilio in a background thread
    threading.Thread(target=send_whatsapp_twilio, args=(log_entry,)).start()

# =========================
# TELETHON HANDLER
# =========================
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Monitors incoming messages for predefined slang and emojis."""
    if not (event.is_group or event.is_channel):
        return  # Ignore private chats

    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", "Unknown Chat")
        text = event.message.message or ""

        # Check for triggers (slang or emoji)
        found_trigger = None
        for slang in SLANG_WORDS:
            if slang in text:
                found_trigger = slang
                break
        if not found_trigger:
            for emoji in EMOJIS:
                if emoji in text:
                    found_trigger = emoji
                    break

        if found_trigger:
            log_alert(chat_title, text, found_trigger)

    except Exception as e:
        logger.error(f"Error in message handler: {e}")

# =========================
# MAIN EXECUTION
# =========================
async def main():
    """Starts the client and runs it until disconnected."""
    logger.info("🚀 Starting Telegram user client...")
    await client.start()  # asks for phone/code on first run

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
