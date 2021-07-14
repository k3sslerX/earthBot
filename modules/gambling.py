import discord
from discord import reaction
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from data.config import get_nick, COINS
import asyncio
from data.database import db
from app import bot
import random


async def jackpot_update():
    guild = bot.get_guild(607467399536705576)
    channel = discord.utils.get(guild.channels, id=862245367286071296)
    message = await channel.fetch_message(864743537810997329)
    bets_record = await db.select_list(f'SELECT bet, member FROM earth_jp_bets')
    bets = []
    members = []
    for i in bets_record:
        bets.append(i['bet'])
        members.append(i['member'])
    description = ''
    total = await db.select_value('SELECT total FROM earth_jackpot')
    for i in range(len(members)):
        description += f'**1)** <@{members[i]}> — **{bets[i]}** {COINS}\nШанс победы: {round(bets[i] / total * 100, 1)} %\n'
    embed = discord.Embed(title='Джекпот', description=description, color=discord.Colour(0x36393E))
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
    await message.edit(embed=embed)


async def jackpot_check():
    guild = bot.get_guild(607467399536705576)
    channel = discord.utils.get(guild.channels, id=862245367286071296)
    message = await channel.fetch_message(864743537810997329)
    bets_record = await db.select_list(f'SELECT bet, member FROM earth_jp_bets ORDER BY bet')
    bets = []
    members = []
    for i in bets_record:
        bets.append(i['bet'])
        members.append(i['member'])
    ticket = random.randint(0, 1000)
    chances = []
    total = await db.select_value('SELECT total FROM earth_jackpot')
    for i in range(len(members)):
        chances.append(round(bets[i] / total * 100, 1) * 10)
    for i in range(len(members)):
        if i >= 1:
            chances[i] = chances[i - 1] + chances[i]
    first = True
    for i in range(len(chances)):
        if chances[i] > ticket and first:
            winner = members[i]
            chance = round(bets[i] / total * 100, 1)
            first = False
    embed = discord.Embed(title='Джекпот', description=f'Игра завершена!\nПобедитель: <@{winner}>\nШанс победы: {chance}\nПриз: {round(total / 100 * 90)} {COINS}', color=discord.Colour(0x36393E))
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862367490607415346/icons8-----96.png?width=77&height=77')
    await message.edit(embed=embed)
    await asyncio.sleep(10)
    embed = discord.Embed(title='Джекпот', description='Ожидание ставок...', color=discord.Colour(0x36393E))
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
    await message.edit(embed=embed)
    await db.execute_table(f'UPDATE earth_jackpot SET started = 0')
    await db.execute_table(f'UPDATE earth_jackpot SET total = 0')
    await db.execute_table(f'DELETE FROM earth_bets')


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
            embed = discord.Embed(title=f'Бросить монетку — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы **уже бросали** монетку. Попробуйте ещё раз через **{round(error.retry_after)} секунд!**', color=discord.Colour(0x36393E))
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273961253142538/icons8--96_1.png?width=77&height=77')
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()

    @commands.command()
    @commands.has_any_role(857609908106559529, 857609646915059712)
    async def jp(self, ctx):
        embed = discord.Embed(title='Джекпот', description='Ожидание ставок...', color=discord.Colour(0x36393E))
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
        await ctx.send(embed=embed)
        embed = discord.Embed(title='Сделать ставку', description='Чтобы сделать ставку нажмите на реакцию ниже', color=discord.Colour(0x36393E))
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862365617532043274/icons8--96_1.png?width=77&height=77')
        message = await ctx.send(embed=embed)
        await message.add_reaction('💰')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = bot.get_guild(payload.guild_id)
        channel = discord.utils.get(guild.channels, id=payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
        member = payload.member
        if message.id == 864743540978483230:
            await reaction.remove(member)
            msg = await member.send(embed=discord.Embed(title=f'Ставка на джекпот — {await get_nick(member)}', description=f'Отправьте сообщение со ставкой\nПример:\n```1000```', color=discord.Colour(0x36393E)))
            def check(m):
                return m.content.isdigit() and m.channel == msg.channel
            
            try:
                mes = await bot.wait_for('message', check=check, timeout=10.0)
            except asyncio.TimeoutError:
                await msg.delete()
            else:
                bet = int(mes.content)
                if bet < 50 and bet > 10000:
                    await member.send(embed=discord.Embed(title=f'Ставка отклонена — {await get_nick(member)}', description=f'**Ставка** должна быть не меньше **50** {COINS} и не больше **10000** {COINS}', color=discord.Colour(0x36393E)))
                if await db.select_value(f'SELECT started FROM earth_jackpot') == 0:
                    if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {member.id}') >= bet:
                        if await db.select_value(f'SELECT bet FROM earth_jp_bets WHERE member = {member.id}') is None:
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {member.id}')
                            await db.execute_table(f'INSERT INTO earth_jp_bets VALUES ({bet}, {member.id})')
                            await db.execute_table(f'UPDATE earth_jackpot SET total = total + {bet}')
                            await db.execute_table(f'UPDATE earth_jackpot SET members = members + 1')
                            await jackpot_update()
                            await member.send(embed=discord.Embed(title=f'Ставка принята — {await get_nick(member)}', description=f'Вы успешно сделали ставку в размере {bet} {COINS}', color=discord.Colour(0x36393E)))
                        else:
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - {bet} WHERE member = {member.id}')
                            await db.execute_table(f'UPDATE earth_jp_bets SET bet = bet + {bet} WHERE member = {member.id}')
                            await db.execute_table(f'UPDATE earth_jackpot SET total = total + {bet}')
                            await jackpot_update()
                            new_bet = await db.select_value(f'SELECT bet FROM earth_jp_bets WHERE member = {member.id}')
                            await member.send(embed=discord.Embed(title=f'Ставка принята — {await get_nick(member)}', description=f'Вы успешно повысили вашу ставку до {new_bet} {COINS}', color=discord.Colour(0x36393E)))
                    else:
                        await member.send(embed=discord.Embed(title=f'Ставка отклонена — {await get_nick(member)}', description=f'У вас недостаточно {COINS}!', color=discord.Colour(0x36393E)))
                else:
                    await member.send(embed=discord.Embed(title=f'Ставка отклонена — {await get_nick(member)}', description=f'Игра уже началась!', color=discord.Colour(0x36393E)))

def setup(Bot):
    Bot.add_cog(Gambling(Bot))