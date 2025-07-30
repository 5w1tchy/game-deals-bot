import asyncio
import re
from datetime import datetime, timezone

import discord
from discord.ext import tasks

import config
from scrapers.game_informer_scraper import get_pc_games_for_month
from utils.state_tracker import read_last_post, write_last_post
from utils.steam_utils import \
    get_steam_link_and_image  # (link, image, desc, price)

bot = None  # Will be injected from bot.py


@tasks.loop(minutes=60)
async def monthly_game_post():
    now = datetime.now(timezone.utc)

    # Only post on the configured day
    if now.day != config.MONTHLY_POST_DAY:
        return

    # Calculate the next month/year to post about
    year = now.year
    next_month = now.month + 1
    if next_month > 12:
        next_month = 1
        year += 1

    current_month = f"{next_month:02d}"
    last = read_last_post()

    if last.get("month") == current_month and last.get("year") == year:
        return  # Already posted

    print(f"Preparing to post {year}-{current_month} releases...")
    month_name = datetime(year, next_month, 1).strftime("%B")

    # Scrape Game Informer
    games = await get_pc_games_for_month(month_name, year)

    post_channel = bot.get_channel(config.MONTHLY_RELEASES_CHANNEL)
    missing_channel = bot.get_channel(config.MISSING_GAMES_CHANNEL)

    for game in games:
        try:
            title = game["title"]
            release_date = game["date"]
            informer_link = game["link"]

            # Clean up title for better matching
            # Remove parentheses/brackets
            clean_title = re.sub(r"[\(\[].*?[\)\]]", "", title)
            clean_title = re.sub(r"[™®©]", "", clean_title).strip()

            print(f"🔍 Searching Steam for: '{clean_title}'")
            steam_link, image_url, description, price = await get_steam_link_and_image(clean_title)

            # Retry with fallback (e.g., strip subtitle after colon/dash)
            if not steam_link:
                fallback_title = clean_title.split(
                    ":")[0].split("-")[0].strip()
                if fallback_title != clean_title:
                    print(f"🔁 Retrying with fallback: '{fallback_title}'")
                    steam_link, image_url, description, price = await get_steam_link_and_image(fallback_title)

            if steam_link:
                # Build and send the embed to main channel
                embed = discord.Embed(
                    title=title,
                    url=steam_link,
                    description=(
                        f"📅 **Release Date:** {release_date}\n"
                        f"💰 **Price:** {price}\n\n"
                        f"{description}"
                    ),
                    color=discord.Color.blurple()
                )
                if image_url:
                    embed.set_image(url=image_url)

                await post_channel.send(embed=embed)
            else:
                print(f"🚫 Could not find Steam link for: {title}")
                await missing_channel.send(f"**Missing on Steam:** {title}\n🔗 {informer_link}")

            await asyncio.sleep(3)  # Prevent hitting rate limits

        except KeyError as e:
            print(f"⚠️ Skipping game due to missing key: {e}")
            continue

    write_last_post(current_month, year)
    print(f"✅ Saved post status: month={current_month}, year={year}")
