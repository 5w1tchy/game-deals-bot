import discord
from discord.ext import commands

import config
from commands import setup_commands
from tasks import start_tasks

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    setup_commands(bot)
    start_tasks(bot)

bot.run(config.DISCORD_TOKEN)
