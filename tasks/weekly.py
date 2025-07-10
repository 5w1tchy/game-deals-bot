from datetime import datetime, timezone

import discord
from discord.ext import tasks

import config
from scrapers.epic_freebies_scraper import fetch_epic_freebies
from utils.json_utils import read_weekly_status, write_weekly_status

bot = None  # Assigned by tasks/__init__.py


@tasks.loop(minutes=1)
async def weekly_poster():
    now = datetime.now(timezone.utc)
    status = read_weekly_status()

    if now.weekday() == 3 and now.hour == config.TARGET_HOUR_UTC:  # Thursday at target hour
        if status["weekly_post_date"] != str(now.date()):
            print(f"[WEEKLY] Running weekly freebie post for {now.date()}")
            try:
                free_channel = bot.get_channel(config.FREE_CHANNEL)

                # Purge previous messages
                deleted = await free_channel.purge(limit=100, check=lambda m: not m.pinned)
                print(
                    f"[WEEKLY] Deleted {len(deleted)} messages in freebie channel.")

                # Post new freebies
                freebies = fetch_epic_freebies()

                if freebies:
                    for game in freebies:
                        embed = discord.Embed(
                            title=f"🎁 Free: {game['title']}",
                            url=game['link'],
                            description=game.get(
                                "description", "No description available."),
                            color=0x00FFFF
                        )
                        if game.get("price"):
                            embed.description += f"\n\n💰 Original Price: {game['price']}"

                        if game.get("image"):
                            embed.set_image(url=game["image"])

                        await free_channel.send(embed=embed)
                else:
                    await free_channel.send("No free Epic games found this week. 🎁")

                # ✅ Only update the post date if freebies were actually sent
                status["weekly_post_date"] = str(now.date())
                write_weekly_status(status)

            except Exception as e:
                print(f"[WEEKLY] Error: {e}")
                log_channel = bot.get_channel(
                    getattr(config, "LOG_CHANNEL_ID", None))
                if log_channel:
                    await log_channel.send(f"⚠️ Error during weekly poster:\n```{e}```")
