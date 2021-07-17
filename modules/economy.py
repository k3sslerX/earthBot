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
import datetime
from datetime import timedelta
from Cybernator import Paginator

class Economy(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Economy module connected!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        while after.channel is not None:
            if after.channel is not None:
                await asyncio.sleep(60)
                if await db.select_value(f'SELECT hours FROM earth_rooms WHERE room = {after.channel.id}') is None:
                    await db.execute_table(f'INSERT INTO earth_rooms VALUES ({after.channel.id}, 0, 0)')
                await db.execute_table(f'UPDATE earth_rooms SET minutes = minutes + 1 WHERE room = {after.channel.id}')
                if await db.select_value(f'SELECT minutes FROM earth_rooms WHERE room = {after.channel.id}') >= 60:
                    await db.execute_table(f'UPDATE earth_rooms SET minutes = 0 WHERE room = {after.channel.id}')
                    await db.execute_table(f'UPDATE earth_rooms SET hours = hours + 1 WHERE room = {after.channel.id}')
            else:
                break

    @commands.command(aliases=['$', 'баланс', 'balance'])
    @commands.cooldown(1, 3, BucketType.member)
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

    @commands.command(aliases=['statistcs', 'статистика'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __statistics(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if member is None:
            member = ctx.author
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            hours = await db.select_value(f'SELECT hours FROM earth_users WHERE member = {member.id}')
            minutes = await db.select_value(f'SELECT minutes FROM earth_users WHERE member = {member.id}')
            messages = await db.select_value(f'SELECT messages FROM earth_users WHERE member = {member.id}')
            embed = discord.Embed(title=f'Статистика пользователя — {await get_nick(member)}', color=discord.Colour(0x36393E))
            embed.add_field(name='• Голосовой онлайн', value=f'```{hours} часов {minutes} минут```')
            embed.add_field(name='• Сообщений:', value=f'```{messages}```')
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['награда', 'daily'])
    @commands.cooldown(1, 43200, BucketType.member)
    async def __daily(self, ctx):
        await ctx.message.delete()
        reward = random.randint(20, 100)
        await db.execute_table(f'UPDATE earth_users SET cash = cash + {reward} WHERE member = {ctx.author.id}')
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
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

    @commands.command(aliases=['reward', 'наградить'])
    @commands.has_role(862638189284818974)
    async def __reward(self, ctx, member: discord.Member = None, amount: int = None):
        await ctx.message.delete()
        if member is not None and amount is not None:
            if amount > 20 and amount < 500:
                await db.execute_table(f'UPDATE earth_users SET cash = cash + {amount} WHERE member = {member.id}')
                await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(amount / 100 * 30)} WHERE member = {ctx.author.id}')
                channel = discord.utils.get(ctx.guild.text_channels, id=857607120224124959)
                embed = discord.Embed(title=f'Выдача награды', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                embed.add_field(name='Кто выдал:', value=f'{ctx.author.mention} — {ctx.author}', inline=False)
                embed.add_field(name='Кому выданы:', value=f'{member.mention} — {member}', inline=False)
                embed.add_field(name='Сколько выдано:', value=f'```{amount} монет```')
                await channel.send(embed=embed)
                embed = discord.Embed(title='Вы получили награду!', 
                description=f'Отправитель: {ctx.author.mention} — {ctx.author}\n`ID: {ctx.author.id}`', color=discord.Colour(0x36393E))
                embed.add_field(name='Получено:', value=f'```{amount} коинов```')
                embed.add_field(name='Баланс:', value=f'```{await db.select_value("SELECT cash FROM earth_users WHERE member = {}".format(member.id))} коинов```')
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862281419552325633/icons8---96.png?width=77&height=77')
                await member.send(embed=embed)
                mes = await ctx.send(f'{ctx.author.mention}, :ok_hand:')
                await asyncio.sleep(5)
                await mes.delete()
            else:
                channel = discord.utils.get(ctx.guild.text_channels, id=857607120224124959)
                embed = discord.Embed(title=f'Попытка неверной выдачи награды!', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                embed.add_field(name='Кто пытался:', value=f'{ctx.author.mention} — {ctx.author}', inline=False)
                embed.add_field(name='Сколько:', value=f'```{amount} монет```')
                await channel.send(embed=embed)

    @commands.command(aliases=['give'])
    @commands.has_role(857609646915059712)
    async def __give(self, ctx, member: discord.Member = None, amount: int = None, *, reason: str = None):
        if member is not None and amount is not None:
            await ctx.message.delete()
            channel = discord.utils.get(ctx.guild.channels, id=857607120224124959)
            await db.execute_table(f'UPDATE earth_users SET cash = cash + {amount} WHERE member = {member.id}')
            embed = discord.Embed(title=f'Выдача монет', color=discord.Colour(0x36393E))
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
            embed.add_field(name='Кто выдал:', value=f'{ctx.author.mention} — {ctx.author}', inline=False)
            embed.add_field(name='Кому выданы:', value=f'{member.mention} — {member}', inline=False)
            embed.add_field(name='Сколько выдано:', value=f'```{amount} монет```')
            if reason is not None:
                embed.add_field(name='Причина выдачи:', value=f'```{reason}```', inline=False)
            else:
                embed.add_field(name='Причина выдачи:', value=f'```Причина не указана```', inline=False)
            await channel.send(embed=embed)

    @commands.command(aliases=['stones'])
    @commands.has_role(857609646915059712)
    async def __stones(self, ctx, member: discord.Member = None, amount: int = None):
        if member is not None and amount is not None:
            await db.execute_table(f'UPDATE earth_users SET stones = stones + {amount} WHERE member = {member.id}')
            await ctx.send(f'{amount} камней были выданы пользователю {member}')

    @commands.command(aliases=['top', 'топ'])
    @commands.cooldown(1, 10, BucketType.member)
    async def __top(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            members_record = await db.select_list('SELECT member, cash FROM earth_users ORDER BY cash DESC')
            member = []
            cash = []
            for i in members_record:
                member.append(i['member'])
                cash.append(i['cash'])
            embeds = []
            lists = len(member) // 10 + 1
            if len(member) % 10 == 0:
                lists -= 1
            for i in range(lists):
                embeds.append(discord.Embed(title=f'Топ пользователей по монетам — {await get_nick(ctx.author)}', color=discord.Colour(0x36393E)))
                embeds[i].set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                embeds[i].set_footer(text=f'Страница {i + 1}/{lists}')
            page = 0
            counter = 1
            for i in range(len(member)):
                memberz = discord.utils.get(ctx.guild.members, id=member[i])
                if memberz is not None:
                    if i < (10 * (page + 1)):
                        embeds[page].add_field(name=f'{counter}) {await get_nick(memberz)}', value=f'**Баланс:** __{cash[i]}__ {COINS}', inline=False)
                        counter += 1
                    else:
                        page += 1
                        embeds[page].add_field(name=f'{counter}) {await get_nick(memberz)}', value=f'**Баланс:** __{cash[i]}__ {COINS}', inline=False)
                        counter += 1
                    if member[i] == ctx.author.id:
                        for j in range(len(embeds)):
                            embeds[j].description = f'**Ваша позиция в топе: {counter - 1}**'
            message = await ctx.send(embed=embeds[0])
            page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embeds, timeout=30, footer=False, use_exit=True, exit_reaction='❌')
            await page.start()
            await message.delete()

    @commands.command(aliases=['topvoice', 'топвойс'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __topvoice(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            members_record = await db.select_list('SELECT member, hours, minutes FROM earth_users ORDER BY hours DESC, minutes DESC')
            member = []
            hours = []
            minutes = []
            for i in members_record:
                member.append(i['member'])
                hours.append(i['hours'])
                minutes.append(i['minutes'])
            embeds = []
            lists = len(member) // 10 + 1
            if len(member) % 10 == 0:
                lists -= 1
            for i in range(lists):
                embeds.append(discord.Embed(title=f'Топ пользователей по онлайну — {await get_nick(ctx.author)}', color=discord.Colour(0x36393E)))
                embeds[i].set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                embeds[i].set_footer(text=f'Страница {i + 1}/{lists}')
            page = 0
            counter = 1
            for i in range(len(member)):
                memberz = discord.utils.get(ctx.guild.members, id=member[i])
                if memberz is not None:
                    if i < (10 * (page + 1)):
                        embeds[page].add_field(name=f'{counter}) {await get_nick(memberz)}', value=f'**{hours[i]}** часов **{minutes[i]}** минут', inline=False)
                        counter += 1
                    else:
                        page += 1
                        embeds[page].add_field(name=f'{counter}) {await get_nick(memberz)}', value=f'**{hours[i]}** часов **{minutes[i]}** минут', inline=False)
                        counter += 1
                    if member[i] == ctx.author.id:
                        for j in range(len(embeds)):
                            embeds[j].description = f'**Ваша позиция в топе: {counter - 1}**'
            message = await ctx.send(embed=embeds[0])
            page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embeds, timeout=30, footer=False, use_exit=True, exit_reaction='❌')
            await page.start()
            await message.delete()

    @commands.command(aliases=['topchannels', 'топкомнат'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __topchannels(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            rooms_record = await db.select_list('SELECT room, hours, minutes FROM earth_rooms ORDER BY hours DESC')
            room = []
            hours = []
            minutes = []
            for i in rooms_record:
                room.append(i['room'])
                hours.append(i['hours'])
                minutes.append(i['minutes'])
            embeds = []
            lists = len(room) // 10 + 1
            if len(room) % 10 == 0:
                lists -= 1
            for i in range(lists):
                embeds.append(discord.Embed(title=f'Топ комнат за всё время — {await get_nick(ctx.author)}', color=discord.Colour(0x36393E)))
                embeds[i].set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862273876478132224/icons8--96_2.png?width=77&height=77')
                embeds[i].set_footer(text=f'Страница {i + 1}/{lists}')
            page = 0
            for i in range(len(room)):
                channel = discord.utils.get(ctx.guild.voice_channels, id=room[i])
                if i < (10 * (page + 1)):
                    embeds[page].add_field(name=f'{i + 1}) {channel.name}', value=f'**{hours[i]}** часов **{minutes[i]}** минут', inline=False)
                else:
                    page += 1
                    embeds[page].add_field(name=f'{i + 1}) {channel.name}', value=f'**{hours[i]}** часов **{minutes[i]}** минут', inline=False)
            message = await ctx.send(embed=embeds[0])
            page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embeds, timeout=30, footer=False, use_exit=True, exit_reaction='❌')
            await page.start()
            await message.delete()

    @commands.command(aliases=['переводы', 'transactions'])
    @commands.cooldown(1, 3, BucketType.member)
    async def __transactions(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is None:
                member = ctx.author
            gets_record = await db.select_list(f'SELECT member, amount, sender, date FROM earth_transactions WHERE member = {member.id} OR sender = {member.id} ORDER BY id DESC')
            members = []
            amounts = []
            senders = []
            dates = []
            for i in gets_record:
                members.append(i['member'])
                amounts.append(i['amount'])
                senders.append(i['sender'])
                dates.append(i['date'])
            embeds = []
            lists = len(members) // 3 + 1
            if len(members) % 3 == 0:
                lists -= 1
            for i in range(lists):
                embeds.append(discord.Embed(title=f'История переводов — {await get_nick(member)}', description=f'**Всего: {len(amounts)}**', color=discord.Colour(0x36393E)))
                embeds[i].set_thumbnail(url='https://cdn.discordapp.com/attachments/859153448309096458/863040949685190656/icons8-----96.png')
                embeds[i].set_footer(text=f'Страница {i + 1}/{lists}')
            page = 0
            for i in range(len(members)):
                if members[i] == member.id:
                    sender = await bot.fetch_user(senders[i])
                    date = datetime.date(year=int(str(dates[i])[0:4]), month=int(str(dates[i])[4:6]), day=int(str(dates[i])[6:8]))
                    if i < (3 * (page + 1)):
                        embeds[page].add_field(name=f'{i + 1}) Входящий перевод', value=f'Сумма: __{amounts[i]}__ {COINS}\nОтправитель: {sender.mention} — {sender}\nДата: __{date}__', inline=False)
                    else:
                        page += 1
                        embeds[page].add_field(name=f'{i + 1}) Входящий перевод', value=f'Сумма: __{amounts[i]}__ {COINS}\nОтправитель: {sender.mention} — {sender}\nДата: __{date}__', inline=False)
                elif senders[i] == member.id:
                    new_member = await bot.fetch_user(members[i])
                    date = datetime.date(year=int(str(dates[i])[0:4]), month=int(str(dates[i])[4:6]), day=int(str(dates[i])[6:8]))
                    if i < (3 * (page + 1)):
                        embeds[page].add_field(name=f'{i + 1}) Исходящий перевод', value=f'Сумма: __{amounts[i]}__ {COINS}\nПолучатель: {new_member.mention} — {new_member}\nДата: __{date}__', inline=False)
                    else:
                        page += 1
                        embeds[page].add_field(name=f'{i + 1}) Исходящий перевод', value=f'Сумма: __{amounts[i]}__ {COINS}\nПолучатель: {new_member.mention} — {new_member}\nДата: __{date}__', inline=False)
            if len(embeds) > 0:
                message = await ctx.send(embed=embeds[0])
                page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embeds, timeout=30, footer=False)
                await page.start()
                await message.clear_reactions()
            else:
                embed = discord.Embed(title=f'История переводов — {await get_nick(ctx.author)}', description='Ваша история пуста!', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404190662950922/icons8---96_1.png?width=77&height=77')
                await ctx.send(embed=embed)

    @commands.command(aliases=['send', 'передать'])
    @commands.cooldown(1, 3, BucketType.member)
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
                            date_date = datetime.date.today()
                            end = str(date_date)
                            ends = list(end)
                            ends.remove('-')
                            ends.remove('-')
                            date = ''.join(ends)
                            await db.execute_table(f'UPDATE earth_users SET cash = cash + {new_amount} WHERE member = {member.id}')
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - {new_amount} WHERE member = {ctx.author.id}')
                            id_list = await db.select_list(f'SELECT * FROM earth_transactions')
                            id = len(id_list)
                            id += 1
                            await db.execute_table(f'INSERT INTO earth_transactions VALUES ({id}, {member.id}, {new_amount}, {ctx.author.id}, {date})')
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