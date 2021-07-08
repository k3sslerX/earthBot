import discord
from app import bot
from discord import reaction
from data.config import get_nick
from discord.ext import commands
from data.database import db
from data.config import staff, COINS
import asyncio
from discord.ext.commands.cooldowns import BucketType
import random

class Economy(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Economy module connected!')

    @commands.command(aliases=['$', 'баланс', 'balance'])
    async def __balance(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if member is None:
            member = ctx.author
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            cash = await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}')
            stones = await db.select_value(f'SELECT stones FROM earth_users WHERE member = {member.id}')
            embed = discord.Embed(title=f'Баланс пользователя — {await get_nick(member)}', color=discord.Colour(0x36393E))
            embed.add_field(name='• Коины:', value=f'```{cash}```')
            embed.add_field(name='• Камни:', value=f'```{stones}```')
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['награда', 'daily'])
    @commands.cooldown(1, 43200, BucketType.member)
    async def __daily(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            reward = random.randint(20, 100)
            await db.execute_table(f'UPDATE earth_users SET cash = cash + {reward} WHERE member = {ctx.author.id}')
            embed = discord.Embed(title=f'Ежедневная награда — {await get_nick(ctx.author)}', color=discord.Colour(0x36393E))
            embed.add_field(name='• Ваша награда:', value=f'```{reward} коинов```')
            embed.set_footer(text='Возвращайтесь через 12 часов', icon_url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
            await ctx.send(embed=embed)

    @__daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
                hours = round(error.retry_after // 3600)
                minutes = round((error.retry_after - hours * 3600) // 60)
                embed = discord.Embed(title=f'Ежедневная награда — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, Вы **уже забирали** ежедневную награду', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                if hours > 0:
                    embed.set_footer(text=f'Возвращайтесь через {hours} часов {minutes} минут', icon_url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
                else:
                    embed.set_footer(text=f'Возвращайтесь через {minutes} минут', icon_url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
                await ctx.send(embed=embed)

    @commands.command(aliases=['give'])
    @commands.has_role(857609646915059712)
    async def __give(self, ctx, member: discord.Member = None, amount: int = None):
        if member is not None and amount is not None:
            await db.execute_table(f'UPDATE earth_users SET cash = cash + {amount} WHERE member = {member.id}')
            await ctx.send(f'{amount} {COINS} были выданы пользователю {member}')

    @commands.command(aliases=['stones'])
    @commands.has_role(857609646915059712)
    async def __stones(self, ctx, member: discord.Member = None, amount: int = None):
        if member is not None and amount is not None:
            await db.execute_table(f'UPDATE earth_users SET stones = stones + {amount} WHERE member = {member.id}')
            await ctx.send(f'{amount} камней были выданы пользователю {member}')

    @commands.command(aliases=['send', 'передать'])
    async def __send(self, ctx, member: discord.Member = None, amount: int = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is not None and amount is not None:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') >= amount and amount > 50 and member != ctx.author:
                    zero_comission = False
                    for role in ctx.author.roles:
                        if role.id in staff:
                            zero_comission = True
                    new_amount = round(amount / 100 * 95)
                    if zero_comission:
                        new_amount = amount

                    if not zero_comission:
                        embed = discord.Embed(title=f'Перевод — {ctx.author}', description=f'Вы действительно хотите передать __{new_amount} {COINS}__ **(включая комиссию 5%)** пользователю **{member.mention}**?', color=discord.Colour(0x36393E))
                    else:
                        embed = discord.Embed(title=f'Перевод — {ctx.author}', description=f'Вы действительно хотите передать __{new_amount} {COINS}__ пользователю **{member.mention}**?', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == ctx.author

                    try:
                        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title='Отказ!', description='Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.edit(embed=embed)
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '✅':
                            await db.execute_table(f'UPDATE earth_users SET cash = cash + {new_amount} WHERE member = {member.id}')
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - {new_amount} WHERE member = {ctx.author.id}')
                            if not zero_comission:
                                embed = discord.Embed(title=f'Перевод — {ctx.author}', description=f'{ctx.author.mention} успешно перевёл __{new_amount}__ {COINS} пользователю {member.mention} (включая комиссию 5%)', color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.edit(embed=embed)
                                await message.clear_reactions()
                            else:
                                embed = discord.Embed(title=f'Перевод — {ctx.author}', description=f'{ctx.author.mention} успешно перевёл __{new_amount}__ {COINS} пользователю {member.mention}', color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.edit(embed=embed)
                                await message.clear_reactions()
                            embed = discord.Embed(title='Вам отправили коины!', 
                            description=f'Отправитель: {ctx.author.mention} — {ctx.author}\n`ID: {ctx.author.id}`', color=discord.Colour(0x36393E))
                            embed.add_field(name='Получено:', value=f'```{new_amount} коинов```')
                            embed.add_field(name='Баланс:', value=f'```{await db.select_value("SELECT cash FROM earth_users WHERE member = {}".format(member.id))} коинов```')
                            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862281419552325633/icons8---96.png?width=77&height=77')
                            await member.send(embed=embed)
                        if str(reaction.emoji) == '❌':
                            embed = discord.Embed(title=f'Перевод — {ctx.author}', description=f'{ctx.author.mention} отменил перевод!', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()


def setup(Bot):
    Bot.add_cog(Economy(Bot))