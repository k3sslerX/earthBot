from datetime import timedelta
from discord import channel, client
import discord
from discord.ext import commands
from .database import db
from app import bot
import asyncio
import time
timedict = {}

class EventRefrence(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        await db.create_users_table()
        await db.create_privates_table()
        await db.create_market_table()
        await db.create_purchases_table()
        await db.create_inventory_table()
        await db.create_rooms_table()
        await db.create_transactions_table()
        await db.create_rooms_hours_table()
        await db.create_jackpot_table()
        await db.create_jp_bets_table()
        for guild in bot.guilds:
            for member in guild.members:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}') is None:
                    await db.execute_table(f'INSERT INTO earth_users VALUES ({member.id}, 0, 0, 0, 0, 0)')
        print('Bot is ready!')

    @commands.Cog.listener()
    async def on_member_join(member):
        if await db.select_value(f"SELECT cash FROM earth_users WHERE member = {member.id}") is None:
            await db.execute_table(f'INSERT INTO earth_users VALUES ({member.id}, 0, 0, 0, 0, 0)')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            t1 = time.time()
            timedict[member.id] = t1
        elif before.channel is not None and after.channel is None and member.id in timedict:
            t2 = time.time()
            sec = t2 - timedict[member.id]
            await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(sec / 60) // 5} WHERE member = {member.id}')
            await db.execute_table(f'UPDATE earth_users SET minutes = minutes + {round(sec / 60)} WHERE member = {member.id}')
            minutes = await db.select_value(f'SELECT minutes FROM earth_users WHERE member = {member.id}')
            hours = minutes // 60
            await db.execute_table(f'UPDATE earth_users SET hours = hours + {hours} WHERE member = {member.id}')
            await db.execute_table(f'UPDATE earth_users SET minutes = minutes - {hours * 60} WHERE member = {member.id}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None:
            if message.guild.id == 607467399536705576:
                await db.execute_table(f'UPDATE earth_users SET messages = messages + 1 WHERE member = {message.author.id}')

def setup(Bot):
    Bot.add_cog(EventRefrence(Bot))