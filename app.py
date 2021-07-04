import discord
from data.config import TOKEN

bot = discord.ext.commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.load_extension('data.events')
bot.run(TOKEN)