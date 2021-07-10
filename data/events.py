from discord import channel, client
from discord.ext import commands
from .database import db
from app import bot
import asyncio

class Events(commands.Cog):

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
        if after.channel is not None:
            channel = after.channel.id
            while after.channel.id == channel:
                await asyncio.sleep(60)
                await db.execute_table(f'UPDATE earth_users SET cash = cash + 1 WHERE member = {member.id}')
                await db.execute_table(f'UPDATE earth_users SET minutes = minutes + 1 WHERE member = {member.id}')
                if await db.select_value(f'SELECT hours FROM earth_rooms WHERE room = {after.channel.id}') is None:
                    await db.execute_table(f'INSERT INTO earth_rooms VALUES ({after.channel.id}, 0, 0)')
                await db.execute_table(f'UPDATE earth_rooms SET minutes = minutes + 1 WHERE room = {after.channel.id}')
                if await db.select_value(f'SELECT minutes FROM earth_users WHERE member = {member.id}') >= 60:
                    await db.execute_table(f'UPDATE earth_users SET minutes = 0 WHERE member = {member.id}')
                    await db.execute_table(f'UPDATE earth_users SET hours = hours + 1 WHERE member = {member.id}')
                if await db.select_value(f'SELECT minutes FROM earth_rooms WHERE room = {after.channel.id}') >= 60:
                    await db.execute_table(f'UPDATE earth_rooms SET minutes = 0 WHERE room = {after.channel.id}')
                    await db.execute_table(f'UPDATE earth_rooms SET hours = hours + 1 WHERE room = {after.channel.id}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None:
            if message.guild.id == 607467399536705576:
                await db.execute_table(f'UPDATE earth_users SET messages = messages + 1 WHERE member = {message.author.id}')

def setup(Bot):
    Bot.add_cog(Events(Bot))