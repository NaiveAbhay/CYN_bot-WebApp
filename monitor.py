# # import logging
# # import os
# # from telethon import TelegramClient, events
# # from collections import defaultdict
# # from dotenv import load_dotenv

# # # =========================
# # # LOAD ENV VARS
# # # =========================
# # load_dotenv()
# # API_ID = int(os.getenv("TELEGRAM_API_ID"))
# # API_HASH = os.getenv("TELEGRAM_API_HASH")
# # BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# # # =========================
# # # LOGGING SETUP
# # # =========================
# # logging.basicConfig(
# #     filename="alerts.log",
# #     level=logging.INFO,
# #     format="%(asctime)s - %(levelname)s - %(message)s"
# # )

# # # =========================
# # # LOAD SLANG + EMOJI LISTS
# # # =========================
# # def load_list(filename):
# #     try:
# #         with open(filename, "r", encoding="utf-8") as f:
# #             return [line.strip() for line in f if line.strip()]
# #     except FileNotFoundError:
# #         print(f"⚠️ File {filename} not found. Continuing with empty list.")
# #         return []

# # slang_words = load_list("slang.txt")
# # emoji_list = load_list("emoji.txt")

# # # =========================
# # # TELEGRAM CLIENT
# # # =========================
# # client = TelegramClient("monitor_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# # # =========================
# # # FLAGGED COUNTS
# # # =========================
# # flagged_counts = defaultdict(int)

# # # =========================
# # # HANDLER
# # # =========================
# # @client.on(events.NewMessage())
# # async def handler(event):
# #     text = event.raw_text

# #     if any(slang in text for slang in slang_words) or any(e in text for e in emoji_list):
# #         flagged_counts[event.chat_id] += 1
# #         logging.info(
# #             f"[FLAG] Chat: {event.chat_id} | Count: {flagged_counts[event.chat_id]} | Message: {text}"
# #         )

# # # =========================
# # # MAIN
# # # =========================
# # if __name__ == "__main__":
# #     print("🚀 Bot is running. Add it to a group/channel to monitor messages.")
# #     client.run_until_disconnected()
   
   
#  # tries to self join group but was getting banned  
   
# # import os
# # import asyncio
# # import logging
# # from telethon import TelegramClient, events, errors
# # from telethon.tl.functions.channels import JoinChannelRequest
# # from dotenv import load_dotenv

# # # Load environment variables
# # load_dotenv()

# # API_ID = int(os.getenv("TELEGRAM_API_ID"))
# # API_HASH = os.getenv("TELEGRAM_API_HASH")

# # # Session file for user login
# # SESSION_NAME = "user_monitor"

# # # Files
# # GROUP_FILE = "group.txt"
# # SLANG_FILE = "slang.txt"
# # EMOJI_FILE = "emoji.txt"
# # ALERT_LOG = "alert_log.txt"

# # # Configure logging
# # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# # # Initialize client (user mode)
# # client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# # # Load slang and emojis
# # with open(SLANG_FILE, "r", encoding="utf-8") as f:
# #     SLANGS = [line.strip() for line in f if line.strip()]

# # with open(EMOJI_FILE, "r", encoding="utf-8") as f:
# #     EMOJIS = [line.strip() for line in f if line.strip()]

# # # Track alerts per group/channel
# # alert_counts = {}

# # async def join_groups_from_file():
# #     """Read group.txt and join each invite link."""
# #     if not os.path.exists(GROUP_FILE):
# #         logging.error(f"{GROUP_FILE} not found!")
# #         return

# #     with open(GROUP_FILE, "r", encoding="utf-8") as f:
# #         links = [line.strip() for line in f if line.strip()]

# #     for link in links:
# #         try:
# #             entity = await client.get_entity(link)
# #             await client(JoinChannelRequest(entity))
# #             chat_type = "Group" if getattr(entity, "megagroup", False) else "Channel"
# #             logging.info(f"✅ Joined {chat_type}: {entity.title} ({link})")
# #         except errors.UserAlreadyParticipantError:
# #             logging.info(f"🔹 Already a member of: {link}")
# #         except Exception as e:
# #             logging.error(f"❌ Failed to join {link}: {e}")

# # @client.on(events.NewMessage())
# # async def handler(event):
# #     """Monitor incoming messages for slang/emoji."""
# #     try:
# #         chat = await event.get_chat()
# #         chat_name = getattr(chat, "title", "Unknown")
# #         chat_id = event.chat_id
# #         text = event.raw_text

# #         if not text:
# #             return

# #         flagged = []

# #         for slang in SLANGS:
# #             if slang in text:
# #                 flagged.append(slang)

# #         for emoji in EMOJIS:
# #             if emoji in text:
# #                 flagged.append(emoji)

# #         if flagged:
# #             alert_counts[chat_id] = alert_counts.get(chat_id, 0) + 1
# #             msg = (f"[ALERT] Suspicious message in {chat_name} ({chat_id})\n"
# #                    f"Message: {text}\n"
# #                    f"Matched: {', '.join(flagged)}\n"
# #                    f"Total Flags in this chat: {alert_counts[chat_id]}\n"
# #                    f"{'-'*40}\n")
# #             with open(ALERT_LOG, "a", encoding="utf-8") as log_file:
# #                 log_file.write(msg)
# #             logging.warning(msg.strip())

# #     except Exception as e:
# #         logging.error(f"Handler error: {e}")

# # async def main():
# #     logging.info("🚀 Starting Telegram client...")
# #     await client.start()  # asks for phone + code first time
# #     await join_groups_from_file()
# #     logging.info("📡 Monitoring groups/channels...")
# #     await client.run_until_disconnected()

# # if __name__ == "__main__":
# #     asyncio.run(main())

# import asyncio
# import logging
# from telethon import TelegramClient, events
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()
# API_ID = int(os.getenv("TELEGRAM_API_ID"))
# API_HASH = os.getenv("TELEGRAM_API_HASH")

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger("MonitorBot")

# # Create client (as USER, not bot)
# client = TelegramClient("user_monitor_session", API_ID, API_HASH)

# # Load slang and emoji lists
# def load_list(file_path):
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             return [line.strip() for line in f if line.strip()]
#     except FileNotFoundError:
#         logger.warning(f"{file_path} not found, skipping.")
#         return []

# SLANG_WORDS = load_list("slang.txt")
# EMOJIS = load_list("emoji.txt")

# # Alert log file
# ALERT_LOG = "alerts.log"
# alert_counts = {}  # keeps per-group detection count

# def log_alert(chat_title, message, trigger):
#     """Save alert to log file and update count."""
#     count = alert_counts.get(chat_title, 0) + 1
#     alert_counts[chat_title] = count

#     log_entry = (
#         f"[ALERT] Group: {chat_title} | "
#         f"Trigger: {trigger} | "
#         f"Message: {message} | "
#         f"Total Flags in this Group: {count}\n"
#     )

#     with open(ALERT_LOG, "a", encoding="utf-8") as f:
#         f.write(log_entry)

#     logger.warning(log_entry.strip())

# # Monitor messages
# @client.on(events.NewMessage())
# async def handler(event):
#     if not (event.is_group or event.is_channel):
#         return  # Ignore private chats

#     chat = await event.get_chat()
#     chat_title = getattr(chat, "title", "Unknown Chat")
#     text = event.message.message or ""

#     # Check slang words
#     for slang in SLANG_WORDS:
#         if slang in text:
#             log_alert(chat_title, text, slang)
#             return  # one trigger is enough

#     # Check emojis
#     for emoji in EMOJIS:
#         if emoji in text:
#             log_alert(chat_title, text, emoji)
#             return

# async def main():
#     logger.info("🚀 Starting Telegram user client...")
#     await client.start()  # asks for phone + code first time only
#     dialogs = await client.get_dialogs()

#     logger.info("✅ Monitoring the following groups/channels:")
#     for d in dialogs:
#         if d.is_group or d.is_channel:
#             logger.info(f"   - {d.title}")

#     logger.info("⚡ Ready! Waiting for suspicious messages...")
#     await client.run_until_disconnected()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("🛑 Monitoring stopped by user.")

import asyncio
import logging
from telethon import TelegramClient, events
from dotenv import load_dotenv
import os

# =========================
# CONFIGURATION & SETUP
# =========================
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MonitorBot")

# =========================
# CLIENT SETUP
# =========================
# Create client (as USER, not bot)
client = TelegramClient("user_monitor_session", API_ID, API_HASH)

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

def log_alert(chat_title, message, trigger):
    """Saves alert to log file and updates the count."""
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

        # Check for any triggers (slang or emoji)
        found_trigger = None
        for slang in SLANG_WORDS:
            if slang in text:
                found_trigger = slang
                break  # Found a match, no need to check other slang
        
        if not found_trigger:
            for emoji in EMOJIS:
                if emoji in text:
                    found_trigger = emoji
                    break  # Found a match, no need to check other emojis

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
    # This will ask for a phone number and code on the first run.
    # A session file ("user_monitor_session.session") will be created.
    await client.start()
    
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