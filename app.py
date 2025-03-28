import discord
from data.config import TOKEN
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.load_extension('data.events')
bot.load_extension('modules.economy')
bot.load_extension('modules.roles')
bot.load_extension('modules.base')
bot.load_extension('modules.rooms')
bot.load_extension('modules.gambling')
bot.load_extension('modules.events')
bot.remove_command('help')
bot.run(TOKEN)