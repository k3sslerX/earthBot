import discord
from discord import colour
from discord.ext import commands
from data.database import db
from data.config import get_nick
import datetime

class Base(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Base commands connected!')

    @commands.command(aliases=['inforole', 'инфороль'])
    async def __inforole(self, ctx, role: discord.Role = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if role is None:
                pass
            else:
                private = False
                room = False
                if await db.select_value(f'SELECT owner FROM earth_private_roles WHERE role = {role.id}') is not None:
                    private = True
                elif await db.select_value(f'SELECT owner FROM earth_private_rooms WHERE role = {role.id}') is not None:
                    room = True
                if private or room:
                    if private:
                        owner = await db.select_value(f'SELECT owner FROM earth_private_roles WHERE role = {role.id}')
                    else:
                        owner = await db.select_value(f'SELECT owner FROM earth_private_rooms WHERE role = {role.id}')
                    embed = discord.Embed(title=f'Информация о роли  — {await get_nick(ctx.author)}', description=f'**Роль:** {role.mention}\n**Владелец:** <@{owner}>', color=discord.Colour(0x36393E))
                    if room:
                        room_id = await db.select_value(f'SELECT channel FROM earth_private_rooms WHERE role = {role.id}')
                        embed.add_field(name='Комната:', value=f'<#{room_id}>', inline=False)
                    else:
                        embed.add_field(name='Комната:', value=f'```Отсутствует```', inline=False)
                    inrole = 0
                    for member in ctx.guild.members:
                        if role in member.roles:
                            inrole += 1
                    embed.add_field(name='Участники:', value=f'```{inrole}```')
                    if private:
                        paided_str = await db.select_value(f'SELECT paided FROM earth_private_roles WHERE owner = {ctx.author.id}')
                        paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                    else:
                        paided_str = await db.select_value(f'SELECT paided FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                        paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                    embed.add_field(name='Оплачена до:', value=f'```{paided}```')
                    if private:
                        if await db.select_value(f'SELECT price FROM earth_market WHERE role = {role.id}') is not None:
                            price = await db.select_value(f'SELECT price FROM earth_market WHERE role = {role.id}')
                            embed.add_field(name='Продаётся', value='```Да```')
                            embed.add_field(name='Цена:', value=f'```{price}```')
                        else:
                            embed.add_field(name='Продаётся', value='```Нет```')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)

def setup(Bot):
    Bot.add_cog(Base(Bot))