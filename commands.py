import asyncio
import re
from datetime import datetime, timezone

import discord
from discord.ext import commands

from scrapers.epic_freebies_scraper import fetch_epic_freebies
from scrapers.game_informer_scraper import get_pc_games_for_month
from scrapers.steam_scraper import fetch_steam_deals


def setup_commands(bot):
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def clear(ctx, amount: int = 5):
        amount = min(max(amount, 1), 100)
        def not_pinned(msg): return not msg.pinned
        deleted = await ctx.channel.purge(limit=amount, check=not_pinned)
        await ctx.send(f"🧹 Cleared {len(deleted)} messages (pinned skipped).", delete_after=5)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def clearall(ctx):
        await ctx.send("Clearing all messages in this channel...", delete_after=5)
        def not_pinned(msg): return not msg.pinned
        deleted = 0
        while True:
            msgs = await ctx.channel.purge(limit=100, check=not_pinned)
            deleted += len(msgs)
            if len(msgs) < 100:
                break
        await ctx.send(f"🧹 Cleared {deleted} messages (pinned skipped).", delete_after=5)

    @bot.command()
    async def deals(ctx):
        await ctx.send("Fetching the best game deals, please wait...")
        loop = asyncio.get_running_loop()
        deals = await loop.run_in_executor(None, fetch_steam_deals)
        good_deals = deals['good_deals']
        if not good_deals:
            await ctx.send("No good deals found right now!")
            return
        description = ""
        for deal in good_deals[:10]:
            description += (
                f"**[{deal['title']}]({deal['link']})**\n"
                f"Discount: {deal['discount']} (was {deal['original_price']}, now {deal['final_price']})\n"
                f"Reviews: {deal['review_summary']} with {deal['review_count']} reviews\n\n"
            )
        embed = discord.Embed(title="🔥 Top Good Deals",
                              description=description, color=0x00FF00)
        await ctx.send(embed=embed)

    @bot.command()
    async def baddeals(ctx):
        await ctx.send("Fetching bad big game deals, please wait...")
        loop = asyncio.get_running_loop()
        deals = await loop.run_in_executor(None, fetch_steam_deals)
        bad_deals = deals['bad_deals']
        if not bad_deals:
            await ctx.send("No big bad deals found right now!")
            return
        description = ""
        for deal in bad_deals[:10]:
            description += (
                f"**[{deal['title']}]({deal['link']})**\n"
                f"Discount: {deal['discount']} (was {deal['original_price']}, now {deal['final_price']})\n"
                f"Reviews: {deal['review_summary']} with {deal['review_count']} reviews\n\n"
            )
        embed = discord.Embed(title="⚠️ Top Bad Big Game Deals",
                              description=description, color=0xFF4500)
        await ctx.send(embed=embed)

    @bot.command()
    async def freebies(ctx):
        await ctx.send("Fetching Epic's current free games, please wait...")
        freebies = fetch_epic_freebies()
        if not freebies:
            await ctx.send("No free games found right now!")
            return
        for freebie in freebies:
            embed = discord.Embed(
                title=f"🎁 Free: {freebie['title']}",
                url=freebie['link'],
                description=f"[Claim here!]({freebie['link']})",
                color=0x00FFFF
            )
            if freebie['image']:
                embed.set_image(url=freebie['image'])
            await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def monthly(ctx):
        """Posts current month's game releases with rich previews."""
        from utils.steam_utils import get_steam_link_and_image

        await ctx.send("📅 Fetching this month's releases, please wait...")

        now = datetime.now(timezone.utc)
        month_name = now.strftime("%B")
        year = now.year

        games = await get_pc_games_for_month(month_name, year)
        if not games:
            await ctx.send("No upcoming PC releases found this month.")
            return

        for game in games:
            try:
                title = game["title"]
                release_date = game["date"]
                informer_link = game["link"]

                # Clean the title for Steam search
                clean_title = re.sub(r"[\(\[].*?[\)\]]", "", title)
                clean_title = re.sub(
                    r"[\u2122\u00AE\u00A9]", "", clean_title).strip()

                # Fetch Steam details
                steam_link, image_url, description, price = await get_steam_link_and_image(clean_title)
                if not steam_link:
                    fallback = clean_title.split(":")[0].split("-")[0].strip()
                    steam_link, image_url, description, price = await get_steam_link_and_image(fallback)

                # Prepare embed
                embed = discord.Embed(
                    title=title,
                    url=steam_link or informer_link,
                    description=f"📅 **Release Date:** {release_date}",
                    color=discord.Color.blue()
                )
                if price:
                    embed.description += f"\n💰 **Price:** {price}"
                if description:
                    embed.description += f"\n\n{description[:500]}"

                if image_url:
                    embed.set_image(url=image_url)

                await ctx.send(embed=embed)
                await asyncio.sleep(2)

            except Exception as e:
                print(
                    f"[monthly command] Error for game '{game.get('title')}': {e}")
                continue
