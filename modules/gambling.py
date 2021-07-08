import discord
from discord import reaction
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from data.config import get_nick, COINS
import asyncio
from data.database import db
from app import bot
import random


class Gambling(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Gambling module connected!')

    @commands.command(aliases=['монетка', 'coinflip'])
    @commands.cooldown(1, 30, BucketType.member)
    async def __coinflip(self, ctx, bet: int = None, member: discord.Member = None):
        await ctx.message.delete()
        if ctx.channel.id == 862245382843006986:
            if bet is None:
                mes = await ctx.send(f'{ctx.author.mention}, укажите ставку!')
                await asyncio.sleep(5)
                await mes.delete()
            elif bet < 50:
                embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, **минимальная** ставка для игры в монетку - **50** {COINS}')
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                mes = await ctx.send(embed=embed)
                await asyncio.sleeo(5)
                await mes.delete()
            elif member is None:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < bet:
                    mes = await ctx.send(f'{ctx.author.mention}, у вас недостаточно коинов!')
                    await asyncio.sleep(5)
                    await mes.delete()
                else:
                    embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} хочет сыграть в монетку на __{bet}__ {COINS} с **любым** пользователем', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')

                    def check(reaction, user):
                        return not user.bot and str(reaction.emoji) == '✅'
                    
                    try:
                        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} никто не принял вашу игру!', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                        await message.edit(embed=embed)
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '✅':
                            if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {user.id}') >= bet:
                                x = random.randint(0, 1)
                                if x == 1:
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {user.id}')
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(bet / 100 * 95)} WHERE member = {ctx.author.id}')
                                    embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', 
                                    description=f'В игре **победу одержал** {ctx.author.mention} и забрал **{bet + round(bet / 100 * 95)}** {COINS} с собой', 
                                    color=discord.Colour(0x36393E))
                                    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862367490607415346/icons8-----96.png?width=77&height=77')
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)
                                else:
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {ctx.author.id}')
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(bet / 100 * 95)} WHERE member = {user.id}')
                                    embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', 
                                    description=f'В игре **победу одержал** {user.mention} и забрал **{bet + round(bet / 100 * 95)}** {COINS} с собой', 
                                    color=discord.Colour(0x36393E))
                                    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862367505674141706/icons8-----96.png?width=77&height=77')
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)
                            else:
                                embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{user.mention} принял коинфлип, но у него недостаточно {COINS}', color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                                await message.clear_reactions()
                                await message.edit(embed=embed)
            else:
                if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < bet:
                    mes = await ctx.send(f'{ctx.author.mention}, у вас недостаточно коинов!')
                    await asyncio.sleep(5)
                    await mes.delete()
                elif await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}') < bet:
                    mes = await ctx.send(f'{ctx.author.mention}, у {member.mention} недостаточно коинов!')
                    await asyncio.sleep(5)
                    await mes.delete()
                else:
                    embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} хочет сыграть с в монетку на __{bet}__ {COINS} с **пользователем** {member.mention}', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == member
                    
                    try:
                        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, пользователь {member.mention} не принял вашу игру!', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                        await message.edit(embed=embed)
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '✅':
                            x = random.randint(0, 1)
                            if x == 1:
                                await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {user.id}')
                                await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(bet / 100 * 95)} WHERE member = {ctx.author.id}')
                                embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', 
                                description=f'В игре **победу одержал** {ctx.author.mention} и забрал **{bet + round(bet / 100 * 95)}** {COINS} с собой', 
                                color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862367490607415346/icons8-----96.png?width=77&height=77')
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                            else:
                                await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {ctx.author.id}')
                                await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(bet / 100 * 95)} WHERE member = {user.id}')
                                embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', 
                                description=f'В игре **победу одержал** {user.mention} и забрал **{bet + round(bet / 100 * 95)}** {COINS} с собой', 
                                color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862367505674141706/icons8-----96.png?width=77&height=77')
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                        elif str(reaction.emoji) == '❌':
                            embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', 
                            description=f'{member.mention} отказался от игры!', 
                            color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                            await message.clear_reactions()
                            await message.edit(embed=embed)

    @__coinflip.error
    async def coinflip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы **уже бросали** монетку. Попробуйте ещё раз через **{round(error.retry_after)} секунд!**')
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()


def setup(Bot):
    Bot.add_cog(Gambling(Bot))