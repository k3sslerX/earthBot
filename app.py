import discord
from data.config import TOKEN
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.load_extension('data.events')
bot.load_extension('modules.economy')
bot.run(TOKEN)