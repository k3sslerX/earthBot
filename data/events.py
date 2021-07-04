from discord import client
from discord.ext import commands
from .database import db
from app import bot

class Events(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        await db.create_users_table()
        for guild in bot.guilds:
            for member in guild.members:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}') is None:
                    await db.execute_table(f'INSERT INTO earth_users VALUES ({member.id}, 0, 0, 0, 0, 0)')
        print('Bot is ready!')

def setup(Bot):
    Bot.add_cog(Events(Bot))