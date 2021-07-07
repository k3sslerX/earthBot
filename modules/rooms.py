import discord
from discord import reaction
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from data.database import db
from data.config import get_nick, COINS
import datetime
from datetime import timedelta
import asyncio
from app import bot


class PrivateRooms(commands.Cog):

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Private Rooms connected!')

    @commands.command(aliases=['моякомната', 'myroom'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __myroom(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}') is not None:
                role_id = await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                text_id = await db.select_value(f'SELECT text_channel FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                voice_id = await db.select_value(f'SELECT voice_channel FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                paided_str = await db.select_value(f'SELECT paided FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                inrole = 0
                for member in ctx.guild.members:
                    if role in member.roles:
                        inrole += 1
                paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                embed = discord.Embed(description=f'**Информация о личной комнате — {await get_nick(ctx.author)}**\n{role.mention}', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.add_field(name='Текстовый канал:', value=f'<#{text_id}>')
                embed.add_field(name='Голосовой канал:', value=f'<#{voice_id}>')
                embed.add_field(name='ID роли:', value=f'```{role.id}```', inline=False)
                embed.add_field(name='Оплачена до:', value=f'```{paided}```')
                embed.add_field(name='Пользователи в комнате:', value=f'```{inrole}```')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной комнаты. Используйте !создатькомнату чтобы создать её", color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(aliases=['пригласить', 'invite'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __invite(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is not None:
                if await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}') is not None:
                    role_id = await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                    role = discord.utils.get(ctx.guild.roles, id=role_id)
                    embed = discord.Embed(title=f'Приглашению в комнату — {await get_nick(ctx.author)}', description=f'{member.mention}, вас пригласили в комнату __{role.name}__', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user == member

                    try:
                        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(title=f'Приглашению в комнату — {await get_nick(ctx.author)}', description=f'Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.edit(embed=embed)
                        await message.clear_reactions()
                    else:
                        if str(reaction.emoji) == '✅':
                            embed = discord.Embed(title=f'Приглашению в комнату — {await get_nick(ctx.author)}', description=f'{member.mention} принял приглашение в комнату __{role.name}__', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()
                            await member.add_roles(role)
                        elif str(reaction.emoji) == '❌':
                            embed = discord.Embed(title=f'Приглашению в комнату — {await get_nick(ctx.author)}', description=f'{member.mention} отклонил приглашение в комнату __{role.name}__', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.edit(embed=embed)
                            await message.clear_reactions()

    @commands.command(aliases=['оплатитькомнату', 'payroom'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __payroom(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}')
            if role_id is not None:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Оплатить комнату — {await get_nick(ctx.author)}', description=f'Вы дейстивтельно хотите оплатить команту {role.name} на **30 дней**? Вы заплатите **5000** {COINS}', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Оплатить комнату — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') >= 5000:
                            paided_str = await db.select_value(f'SELECT paided FROM earth_private_rooms WHERE owner = {ctx.author.id}')
                            paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                            paided = paided + timedelta(days=30)
                            ends = list(str(paided))
                            ends.remove('-')
                            ends.remove('-')
                            end = ''.join(ends)
                            await db.execute_table(f'UPDATE earth_private_rooms SET paided = {end} WHERE role = {role_id}')
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - 5000 WHERE member = {ctx.author.id}')
                            embed = discord.Embed(title=f'Оплатить комнату — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно **оплатили** вашу комнату {role.name} и заплатили **5000** {COINS}!', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f'Оплатить комнату — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, у вас нет **5000** {COINS} чтобы оплатить комнату!', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Оплатить комнату — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы **отменили** оплату', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['цветкомнаты', 'roomcolour'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __roomcolour(self, ctx, colour: discord.Colour = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}')
            if role_id is not None and colour is not None:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'**Текущий цвет:** __{role.colour}__\n**Новый цвет:** __{colour}__\nВы заплатите: **0** {COINS}', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        await role.edit(colour=colour)
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно изменили цвет вашей комнатной роли!\nНовый цвет: __{colour}__\nПревью: {role.mention}', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} отменил изменения', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['названиекомнаты', 'roomname'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __roomname(self, ctx, *, name: str = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}')
            if role_id is None:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной комнаты. Используйте !создатькомнату чтобы создать её", color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            elif name is None:
                embed = discord.Embed(description=f"{ctx.author.mention}, укажите новое название комнаты! Максимальная длинна названия - 32 символа", color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            elif len(list(name)) > 32:
                embed = discord.Embed(title=f'Ошибка! — {await get_nick(ctx.author)}', description=f'Максимальная длина названия роли - **32 символа!**', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                text_channel = discord.utils.get(ctx.guild.text_channels, id=await db.select_value(f'SELECT text_channel FROM earth_private_rooms WHERE owner = {ctx.author.id}'))
                voice_channel = discord.utils.get(ctx.guild.voice_channels, id=await db.select_value(f'SELECT voice_channel FROM earth_private_rooms WHERE owner = {ctx.author.id}'))
                embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'**Текущее название:** __{role.name}__\n**Новое назвние:** __{name}__\nВы заплатите: **500** {COINS}', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < 500:
                            embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, у вас нет 500 {COINS} для подтверждения изменений!', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        else:
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - 500 WHERE member = {ctx.author.id}')
                            await role.edit(name=name)
                            await text_channel.edit(name=name)
                            await voice_channel.edit(name=name)
                            embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно изменили название вашей комнаты! Новое название: __{name}__\nПревью: {role.mention}', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} отменил изменения', color=discord.Colour(0x36393E))
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['createroom', 'создатькомнату'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __createroom(self, ctx, colour: discord.Colour = None, *, name: str = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if colour is None or name is None:
                embed = discord.Embed(title='Что-то пошло не так! Попробуйте использовать эту команду так:',
                description=f'`!создатькомнату #COLOUR *name*`\n\n**Пример:**\n`!создатькомнату #ff0000 крутая комната!`', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            elif len(list(name)) > 32:
                embed = discord.Embed(title=f'Ошибка! — {await get_nick(ctx.author)}', description=f'Максимальная длина названия комнаты - **32 символа!**', color=discord.Colour(0x36393E))
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                cash = await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}')
                if await db.select_value(f'SELECT role FROM earth_private_rooms WHERE owner = {ctx.author.id}') is None:
                    if cash >= 10000:
                        embed = discord.Embed(title=f'Покупка личной комнаты — {await get_nick(ctx.author)}',
                        description=f'**Название:** `{name}`\n**Цвет:** `{colour}` \nВаш текущий баланс: {cash} {COINS}\nВаш баланс после покупки: {cash - 10000}', color=discord.Colour(0x36393E))
                        embed.set_footer(text='Вы сможете изменять название комнаты и цвет роли после покупки')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        message = await ctx.send(embed=embed)
                        await message.add_reaction('✅')
                        await message.add_reaction('❌')

                        def check(reaction, user):
                            return user.id == ctx.author.id

                        try:
                            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=f'Покупка личной комнаты — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности', color=discord.Colour(0x36393E))
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        else:
                            if str(reaction.emoji) == '✅':
                                date = datetime.date.today() + timedelta(days=30)
                                end = str(date)
                                ends = list(end)
                                ends.remove('-')
                                ends.remove('-')
                                end = ''.join(ends)
                                support = discord.utils.get(ctx.guild.roles, id=861605034394517505)
                                position = support.position + 1
                                role = await ctx.guild.create_role(name=name, colour=colour)
                                await role.edit(position=position)
                                category = discord.utils.get(ctx.guild.categories, id=862212109034192918)
                                permissions = {
                                    ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
                                    role: discord.PermissionOverwrite(connect=True)
                                }
                                voice_channel = await ctx.guild.create_voice_channel(name=name, category=category, overwrites=permissions)
                                category = discord.utils.get(ctx.guild.categories, id=862212067662757968)
                                permissions = {
                                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False),
                                    role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                                }
                                text_channel = await ctx.guild.create_text_channel(name=name, category=category, overwrites=permissions)
                                await ctx.author.add_roles(role)
                                await db.execute_table(f'INSERT INTO earth_private_rooms VALUES ({voice_channel.id}, {text_channel.id}, {role.id}, {end}, {ctx.author.id})')
                                await db.execute_table(f'UPDATE earth_users SET cash = cash - 10000 WHERE member = {ctx.author.id}')
                                embed = discord.Embed(title=f'Покупка личной комнаты — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно приобрели личную комнату {role.name} и связали её с ролью {role.mention}!\n\n```Комната была оплачена на 30 дней, Для большей информации используйте !моякомната```', color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                            elif str(reaction.emoji) == '❌':
                                embed = discord.Embed(title=f'Покупка личной комнаты — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы отменили покупку!', color=discord.Colour(0x36393E))
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                    else:
                        message = await ctx.send(f'{ctx.author.mention}, у вас недостаточно коинов!')
                        await asyncio.sleep(5)
                        await message.delete()
                else:
                    message = await ctx.send(f'{ctx.author.mention}, у вас уже есть личная комната')
                    await asyncio.sleep(5)
                    await message.delete()


def setup(Bot):
    Bot.add_cog(PrivateRooms(Bot))