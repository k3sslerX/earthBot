import asyncio
import discord
from discord import colour
from discord.ext import commands
from data.database import db
from data.config import get_nick
import datetime
from discord.ext.commands.cooldowns import BucketType

class Base(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Base commands connected!')

    @commands.command(aliases=['аватар', 'avatar'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __avatar(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is None:
                member = ctx.author
                embed = discord.Embed(type='image', title=f'Аватарка — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, ниже показана **ваша** аватарка', color=discord.Colour(0x36393E))
            else:
                embed = discord.Embed(type='image', title=f'Аватарка — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, ниже показана аватарка **пользователя** {member.mention}', color=discord.Colour(0x36393E))
            embed.set_image(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['inforole', 'инфороль'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __inforole(self, ctx, role: discord.Role = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if role is None:
                msg = await ctx.send(embed=discord.Embed(title=f'Ошибка!  — {await get_nick(ctx.author)}', description=f'Упоминание **роли** или её ID **не найдено**', color=discord.Colour(0x36393E)))
                await asyncio.sleep(5)
                await msg.delete()
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
                        room_id = await db.select_value(f'SELECT voice_channel FROM earth_private_rooms WHERE role = {role.id}')
                        embed.add_field(name='Комната:', value=f'<#{room_id}>', inline=False)
                    else:
                        embed.add_field(name='Комната:', value=f'```Отсутствует```', inline=False)
                    inrole = 0
                    for member in ctx.guild.members:
                        if role in member.roles:
                            inrole += 1
                    embed.add_field(name='Участники:', value=f'```{inrole}```')
                    if private:
                        paided_str = await db.select_value(f'SELECT paided FROM earth_private_roles WHERE owner = {owner}')
                        paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                    else:
                        paided_str = await db.select_value(f'SELECT paided FROM earth_private_rooms WHERE owner = {owner}')
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
                else:
                    embed = discord.Embed(title=f'Информация о роли  — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, данная роль **не является** личной!', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
                    msg = await ctx.send(embed=embed)
                    await asyncio.sleep(5)
                    await msg.delete()

def setup(Bot):
    Bot.add_cog(Base(Bot))