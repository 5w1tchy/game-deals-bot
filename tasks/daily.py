import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import tasks

import config
from scrapers.steam_scraper import fetch_steam_deals_with_retries
from utils.json_utils import (read_daily_status, read_posted_games,
                              read_posted_messages, write_daily_status,
                              write_posted_games, write_posted_messages)

bot = None  # Will be assigned by tasks/__init__.py


@tasks.loop(minutes=1)
async def daily_poster():
    now = datetime.now(timezone.utc)
    status = read_daily_status()  # read latest status at the start

    if now.hour == config.TARGET_HOUR_UTC:
        if status["daily_post_date"] != str(now.date()):
            print(f"Running daily posts for {now.date()}")

            posted_messages = read_posted_messages()
            posted_games = read_posted_games()  # read per-game tracking

            try:
                good_channel = bot.get_channel(config.GOOD_CHANNEL)
                bad_channel = bot.get_channel(config.BAD_CHANNEL)

                deals = await asyncio.get_running_loop().run_in_executor(None, fetch_steam_deals_with_retries)
                good_deals = deals['good_deals']
                bad_deals = deals['bad_deals']

                # Post good deals
                description = ""
                good_posted_games = []
                for deal in good_deals[:10]:
                    game_title = deal['title']

                    last_post_date_str = posted_games["games"].get(game_title)
                    if last_post_date_str:
                        now_date = now.date()
                        last_post_date = datetime.strptime(
                            last_post_date_str, "%Y-%m-%d").date()
                        age_days = (now_date - last_post_date).days
                        if age_days <= config.POST_THRESHOLD_DAYS:
                            continue  # skip repost

                    description += (
                        f"**[{deal['title']}]({deal['link']})**\n"
                        f"Discount: {deal['discount']} (was {deal['original_price']}, now {deal['final_price']})\n"
                        f"Reviews: {deal['review_summary']} with {deal['review_count']} reviews\n\n"
                    )
                    good_posted_games.append(game_title)

                if description:
                    embed = discord.Embed(
                        title="🔥 Top Good Deals",
                        description=description.strip(),
                        color=0x00FF00
                    )
                    msg = await good_channel.send(embed=embed)
                    posted_messages["messages"].append({
                        "message_id": msg.id,
                        "channel_id": good_channel.id,
                        "post_date": str(now.date())
                    })
                    for game_title in good_posted_games:
                        posted_games["games"][game_title] = str(now.date())
                else:
                    print("[DAILY] No good deals found today. Skipping post.")

                # Post bad deals
                description = ""
                bad_posted_games = []
                for deal in bad_deals[:10]:
                    game_title = deal['title']

                    last_post_date_str = posted_games["games"].get(game_title)
                    if last_post_date_str:
                        now_date = now.date()
                        last_post_date = datetime.strptime(
                            last_post_date_str, "%Y-%m-%d").date()
                        age_days = (now_date - last_post_date).days
                        if age_days <= config.POST_THRESHOLD_DAYS:
                            continue  # skip repost

                    description += (
                        f"**[{deal['title']}]({deal['link']})**\n"
                        f"Discount: {deal['discount']} (was {deal['original_price']}, now {deal['final_price']})\n"
                        f"Reviews: {deal['review_summary']} with {deal['review_count']} reviews\n\n"
                    )
                    bad_posted_games.append(game_title)

                if description:
                    embed = discord.Embed(
                        title="⚠️ Top Bad Big Game Deals",
                        description=description.strip(),
                        color=0xFF4500
                    )
                    msg = await bad_channel.send(embed=embed)
                    posted_messages["messages"].append({
                        "message_id": msg.id,
                        "channel_id": bad_channel.id,
                        "post_date": str(now.date())
                    })
                    for game_title in bad_posted_games:
                        posted_games["games"][game_title] = str(now.date())
                else:
                    print("[DAILY] No big bad deals today. Skipping post.")

            except Exception as e:
                print(f"Error in daily_poster: {e}")
                log_channel = bot.get_channel(
                    getattr(config, "LOG_CHANNEL_ID", None))
                if log_channel:
                    await log_channel.send(f"⚠️ Error during daily poster:\n```{e}```")
            finally:
                # Always update JSONs, whether success or partial failure
                status["daily_post_date"] = str(now.date())
                write_daily_status(status)
                write_posted_messages(posted_messages)
                write_posted_games(posted_games)
