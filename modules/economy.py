import discord
from app import bot
from discord import reaction
from data.config import get_nick
from discord.ext import commands
from data.database import db
from data.config import staff
import asyncio

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
            embed = discord.Embed(title=f'Баланс пользователя — {await get_nick(member)}')
            embed.add_field(name='• Коины:', value=f'```{cash}```')
            embed.add_field(name='• Камни:', value=f'```{stones}```')
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['give'])
    @commands.has_any_role(703942596011229190, 857609646915059712)
    async def __give(self, ctx, member: discord.Member = None, amount: int = None):
        if member is not None and amount is not None:
            await db.execute_table(f'UPDATE earth_users SET cash = cash + {amount} WHERE member = {member.id}')
            await ctx.send(f'{amount} коинов были выданы пользователю {member}')

    @commands.command(aliases=['send', 'передать'])
    async def __send(self, ctx, member: discord.Member = None, amount: int = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is not None and amount is not None:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') >= amount and amount > 25:
                    zero_comission = False
                    for role in ctx.author.roles:
                        if role.id in staff:
                            zero_comission = True
                    new_amount = round(amount / 100 * 95)
                    if zero_comission:
                        new_amount = amount

                    if not zero_comission:
                        embed = discord.Embed(title=f'Подтвердите перевод — {ctx.author}', description=f'Вы хотите передать __{new_amount} коинов__ **(включая комиссию 5%)** пользователю **{await get_nick(member)}**')
                    else:
                        embed = discord.Embed(title=f'Подтвердите перевод — {ctx.author}', description=f'Вы хотите передать __{new_amount} коинов__ пользователю **{await get_nick(member)}**')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == ctx.author

                    try:
                        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title='Отказ!', description='Окно было закрыто из-за неактивности')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.edit(embed=embed)
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '✅':
                            await db.execute_table(f'UPDATE earth_users SET cash = cash + {new_amount} WHERE member = {member.id}')
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - {new_amount} WHERE member = {ctx.author.id}')
                            if not zero_comission:
                                embed = discord.Embed(title='Подтверждено!', description=f'{ctx.author.mention} успешно перевёл {new_amount} коинов пользователю {member.mention} (Включая комиссию 5%)')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.edit(embed=embed)
                                await message.clear_reactions()
                            else:
                                embed = discord.Embed(title='Подтверждено!', description=f'{ctx.author.mention} успешно перевёл {new_amount} коинов пользователю {member.mention}')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.edit(embed=embed)
                                await message.clear_reactions()
                            embed = discord.Embed(title='Вам отправили коины!')
                            embed.add_field(name='Отправитель:', value=f'```{await get_nick(ctx.author)} — {ctx.author}```')
                            embed.add_field(name='Сумма:', value=f'```{new_amount} коинов```')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await member.send(embed=embed)
                        if str(reaction.emoji) == '❌':
                            embed = discord.Embed(title='Отказ!', description=f'{ctx.author.mention} отменил перевод!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()


def setup(Bot):
    Bot.add_cog(Economy(Bot))