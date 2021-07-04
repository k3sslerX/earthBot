import discord
from data.config import get_nick
from discord.ext import commands
from data.database import db

class Economy(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Economy module connected!')

    @commands.command(aliases=['$', 'баланс', 'balance'])
    async def __balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            cash = await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}')
            embed = discord.Embed(title=f'Баланс пользователя {await get_nick(member)}', description=f'{cash} :coin:', colour=discord.Color.dark_gray())
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f'Запросил {await get_nick(ctx.author)}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)


def setup(Bot):
    Bot.add_cog(Economy(Bot))