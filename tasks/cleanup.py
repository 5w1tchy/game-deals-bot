import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import tasks

import config
from utils.json_utils import read_posted_messages, write_posted_messages

bot = None  # Assigned in tasks/__init__.py


@tasks.loop(hours=24)
async def cleanup_old_posts():
    now = datetime.now(timezone.utc)
    messages_data = read_posted_messages()
    updated_messages = []

    for msg_entry in messages_data["messages"]:
        try:
            post_date = datetime.strptime(
                msg_entry["post_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            age_days = (now - post_date).days

            if age_days > config.POST_THRESHOLD_DAYS:
                channel = bot.get_channel(msg_entry["channel_id"])
                if channel:
                    try:
                        msg = await channel.fetch_message(msg_entry["message_id"])
                        await msg.delete()
                        print(
                            f"[CLEANUP] Deleted old post: {msg.id} (age {age_days} days)")
                        # Message deleted → don't keep entry.
                    except discord.NotFound:
                        print(
                            f"[CLEANUP] Message {msg_entry['message_id']} already gone (404). Removing entry.")
                        # Already deleted → remove from JSON.
                    except discord.Forbidden:
                        print(
                            f"[CLEANUP] Forbidden: cannot delete message {msg_entry['message_id']}. Keeping entry.")
                        updated_messages.append(msg_entry)
                    except Exception as e:
                        print(
                            f"[CLEANUP] Unexpected error deleting message {msg_entry['message_id']}: {e}")
                        updated_messages.append(msg_entry)
                else:
                    print(
                        f"[CLEANUP] Channel {msg_entry['channel_id']} not found. Keeping entry.")
                    updated_messages.append(msg_entry)
            else:
                updated_messages.append(msg_entry)

        except Exception as e:
            print(
                f"[CLEANUP] Skipped invalid entry {msg_entry} due to error: {e}")

    write_posted_messages({"messages": updated_messages})


@cleanup_old_posts.before_loop
async def before_cleanup():
    await bot.wait_until_ready()
    # Delay cleanup start to avoid race conditions with daily/weekly tasks
    print("[CLEANUP] Waiting 2 minutes before starting cleanup to avoid race with daily/weekly tasks...")
    await asyncio.sleep(120)  # wait 2 minutes before first cleanup run
