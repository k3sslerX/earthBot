import discord
from discord import colour
from discord.ext import commands
from Cybernator import Paginator
from discord.ext.commands.cooldowns import BucketType
from data.database import db
from data.config import get_nick, COINS
import datetime
from datetime import timedelta
import asyncio
from app import bot


class PrivateRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Private Roles connected!')

    @commands.command(aliases=['мояроль'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __myRole(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}') is not None:
                role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                paided_str = await db.select_value(f'SELECT paided FROM earth_private_roles WHERE owner = {ctx.author.id}')
                inrole = 0
                for member in ctx.guild.members:
                    if role in member.roles:
                        inrole += 1
                paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                embed = discord.Embed(description=f'**Информация о личной роли — {await get_nick(ctx.author)}**\n{role.mention}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.add_field(name='Название:', value=f'```{role}```', inline=False)
                embed.add_field(name='ID:', value=f'```{role.id}```')
                embed.add_field(name='Оплачена до:', value=f'```{paided}```', inline=False)
                embed.add_field(name='Пользователи с вашей ролью:', value=f'```{inrole} members```', inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной роли. Используйте !создать роль чтобы создать её")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(aliases=['оплатитьроль', 'payrole'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __payrole(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
            if role_id is not None:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Оплатить роль — {await get_nick(ctx.author)}', description=f'Вы дейстивтельно хотите оплатить роль {role.mention} на **30 дней**? Вы заплатите **1500** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Оплатить роль — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') >= 1500:
                            paided_str = await db.select_value(f'SELECT paided FROM earth_private_roles WHERE owner = {ctx.author.id}')
                            paided = datetime.date(year=int(paided_str[0:4]), month=int(paided_str[4:6]), day=int(paided_str[6:8]))
                            paided = paided + timedelta(days=30)
                            ends = list(str(paided))
                            ends.remove('-')
                            ends.remove('-')
                            end = ''.join(ends)
                            await db.execute_table(f'UPDATE earth_private_roles SET paided = {end} WHERE role = {role_id}')
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - 1500 WHERE member = {ctx.author.id}')
                            embed = discord.Embed(title=f'Оплатить роль — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно **оплатили** вашу роль {role.mention} и заплатили **1500** {COINS}!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f'Оплатить роль — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, у вас нет **1500** {COINS} чтобы оплатить роль!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Оплатить роль — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы **отменили** оплату')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['цвет', 'colour'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __colour(self, ctx, colour: discord.Colour = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
            if role_id is not None and colour is not None:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'**Текущий цвет:** __{role.colour}__\n**Новый цвет:** __{colour}__\nВы заплатите: **0** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        await role.edit(colour=colour)
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно изменили цвет вашей роли!\nНовый цвет: __{colour}__\nПревью: {role.mention}')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} отменил изменения')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['название', 'name'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __name(self, ctx, *, name: str = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
            if role_id is not None and name is not None:
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'**Текущее название:** __{role.name}__\n**Новое назвние:** __{name}__\nВы заплатите: **200** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < 200:
                            embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, у вас нет 200 {COINS} для подтверждения изменений!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        else:
                            await db.execute_table(f'UPDATE earth_users SET cash = cash - 200 WHERE member = {ctx.author.id}')
                            await role.edit(name=name)
                            embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно изменили название вашей роли! Новое название: __{name}__\nПревью: {role.mention}')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Подтвердите изменения — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} отменил изменения')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['выставить', 'expose'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __expose(self, ctx, price: int = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if price is None:
                embed = discord.Embed(description=f'{ctx.author.mention}, укажите цену вашей роли! Цена должна быть не меньше чем **100** {COINS} и не больше чем **10000** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            elif 10000 < price < 100:
                embed = discord.Embed(description=f'{ctx.author.mention}, цена должна быть не меньше чем **100** {COINS} и не больше чем **10000** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
            elif await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}') is None:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной роли. Используйте !создатьроль чтобы создать её")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                embed = discord.Embed(title=f'Выставить роль на продажу — {await get_nick(ctx.author)}', description=f'Вы действительно хотите выставить вашу роль {role.mention} на продажу за __{price}__ {COINS}. Вы заплатите **200** {COINS}')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')

                def check(reaction, user):
                    return user.id == ctx.author.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                except asyncio.TimeoutError:
                    embed = discord.Embed(title=f'Выставить роль на продажу — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await message.clear_reactions()
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        if await db.select_value(f'SELECT price FROM earth_market WHERE role = {role_id}') is None:
                            if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < 200:
                                embed = discord.Embed(title=f'Выставить роль на проодажу — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, у вас нет **200** {COINS} для подтверждения!')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                            else:
                                await db.execute_table(f'UPDATE earth_users SET cash = cash - 200 WHERE member = {ctx.author.id}')
                                await db.execute_table(f'INSERT INTO earth_market VALUES ({role_id}, {price}, {ctx.author.id})')
                                embed = discord.Embed(title=f'Выставить роль на продажу — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно выставили роль {role.mention} на !магазин за **{price}** {COINS} и заплатили за это **200** {COINS}')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                        else:
                            embed = discord.Embed(title=f'Выставить роль на продажу — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, ваша роль {role.mention} уже есть в !магазин')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                    elif str(reaction.emoji) == '❌':
                        embed = discord.Embed(title=f'Выставить роль на продажу — {await get_nick(ctx.author)}', description=f'{ctx.author.mention} отменил выставление!')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)

    @commands.command(aliases=['market', 'магазин'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __market(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            market_record = await db.select_list('SELECT role, price, owner FROM earth_market')
            roles = []
            prices = []
            owners = []
            page = 0
            for i in market_record:
                roles.append(i['role'])
                prices.append(i['price'])
                owners.append(i['owner'])
            embed = []
            lists = len(roles) // 5 + 1
            if len(roles) % 5 == 0:
                lists -= 1
            for i in range(lists):
                embed.append(discord.Embed(title=f'Магазин ролей — {await get_nick(ctx.author)}'))
                embed[i].set_thumbnail(url=ctx.guild.icon_url)
                embed[i].set_footer(text=f'Страница {i + 1}/{lists}')
            for i in range(len(roles)):
                role = discord.utils.get(ctx.guild.roles, id=roles[i])
                if i < (5 * (page + 1)):
                    embed[page].add_field(name=f'ᅠ', value=f'**{i + 1}.** {role.mention}\n**Цена:** __{prices[i]} {COINS}__\n**Продавец:** <@{owners[i]}>', inline=False)
                else:
                    page += 1
                    embed[page].add_field(name=f'ᅠ', value=f'**{i + 1}.** {role.mention}\n**Цена:** __{prices[i]} {COINS}__\n**Продавец:** <@{owners[i]}>', inline=False)
            if len(embed) >= 1:
                message = await ctx.send(embed=embed[0])
                page = Paginator(bot, message, only=ctx.author, use_more=False, embeds=embed, timeout=30, footer=False, use_exit=True, exit_reaction='❌')
                await page.start()
                await message.delete()
            else:
                embed = discord.Embed(title=f'Магазин ролей', description=f'Магазин пуст!')
                embed.set_thumbnail(url=ctx.guild.icon_url)
                await ctx.send(embed=embed)

    @commands.command(aliases=['withdraw', 'убрать'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __withdraw(self, ctx):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
            if role_id is not None:
                if await db.select_value(f'SELECT price FROM earth_market WHERE role = {role_id}') is not None:
                    embed = discord.Embed(title=f'Снять с продажи — {await get_nick(ctx.author)}', description=f'Вы действительно хотите снять с продажи вашу роль <@&{role_id}>?')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')

                    def check(reaction, user):
                        return user.id == ctx.author.id

                    try:
                        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                    except asyncio.TimeoutError:
                        embed = discord.Embed(title=f'Снять с продажи — {await get_nick(ctx.author)}', description='Окно закрыто из-за неактивности')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        await message.clear_reactions()
                        await message.edit(embed=embed)
                    else:
                        if str(reaction.emoji) == '✅':
                            await db.execute_table(f'DELETE FROM earth_market WHERE role = {role_id}')
                            embed = discord.Embed(title=f'Снять с продажи — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно сняли вашу роль <@&{role_id}> с продажи!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                        elif str(reaction.emoji) == '❌':
                            embed = discord.Embed(title=f'Снять с продажи — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы отменили снятие!')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            await message.clear_reactions()
                            await message.edit(embed=embed)
                else:
                    embed = discord.Embed(title=f'Снять с продажи — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вашей роли нет в магазине!')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной роли. Используйте !создатьроль чтобы создать её")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.command(aliases=['купить', 'buyrole'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __buyrole(self, ctx, number: int = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if number is None:
                mes = await ctx.send(f'{ctx.author.mention}, укажите номер роли!')
                await asyncio.sleep(5)
                await mes.delete()
            else:
                market_record = await db.select_list('SELECT role, price, owner FROM earth_market')
                roles = []
                prices = []
                owners = []
                for i in market_record:
                    roles.append(i['role'])
                    prices.append(i['price'])
                    owners.append(i['owner'])
                if number > len(roles):
                    mes = await ctx.send(f'{ctx.author.mention}, роли с таким номером нет в магазине!')
                    await asyncio.sleep(5)
                    await mes.delete()
                else:
                    if await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}') < prices[number - 1]:
                        mes = await ctx.send(f'{ctx.author.mention}, у вас недостаточно коинов!')
                        await asyncio.sleep(5)
                        await mes.delete()
                    elif discord.utils.get(ctx.guild.roles, id=roles[number - 1]) is not None:
                        inrole = 0
                        ininv = 0
                        inv_record = await db.select_list(f'SELECT role FROM earth_inventory WHERE member = {ctx.author.id}')
                        roles_inv = []
                        for i in inv_record:
                            roles_inv.append(i['role'])
                        for role in ctx.author.roles:
                            if role.id == roles[number - 1]:
                                inrole = 1
                        if roles[number - 1] in roles_inv:
                            ininv = 1
                        if ininv == 0 and inrole == 0:
                            role = discord.utils.get(ctx.guild.roles, id=roles[number - 1])
                            cash = await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}')
                            embed = discord.Embed(title='Покупка роли',
                            description=f'Вы хотите приобрести: {role.mention}\nВаш текущий баланс: {cash} {COINS}\nВаш баланс после покупки: {cash - prices[number - 1]} {COINS}')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            message = await ctx.send(embed=embed)
                            await message.add_reaction('✅')
                            await message.add_reaction('❌')

                            def check(reaction, user):
                                return user.id == ctx.author.id

                            try:
                                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                            except asyncio.TimeoutError:
                                embed = discord.Embed(title=f'Покупка роли', description='Window was closed due to inactivity')
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
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash - {prices[number - 1]} WHERE member = {ctx.author.id}')
                                    await db.execute_table(f'UPDATE earth_users SET cash = cash + {round(prices[number - 1] / 100 * 75 )} WHERE member = {owners[number - 1]}')
                                    await db.execute_table(f'INSERT INTO earth_purchases VALUES ({roles[number - 1]}, {end}, {ctx.author.id})')
                                    await ctx.author.add_roles(role)
                                    embed = discord.Embed(title='Покупка роли', description=f'{ctx.author.mention}, вы успешно приобрели роль {role.mention}! Роли хранятся у вас в течение 30 дней!')
                                    embed.set_thumbnail(url=ctx.author.avatar_url)
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)
                                elif str(reaction.emoji) == '❌':
                                    embed = discord.Embed(title='Покупка роли', description=f'{ctx.author.mention}, вы отменили покупку!')
                                    embed.set_thumbnail(url=ctx.author.avatar_url)
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)
                        elif inrole == 1:
                            await ctx.send(f'{ctx.author.mention}, у вас уже есть эта роль!')
                        elif ininv == 1:
                            role = discord.utils.get(ctx.guild.roles, id=roles[number - 1])
                            embed = discord.Embed(title='Эта роль уже есть в вашем инвентаре!', description='Хотите достать её?')
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            message = await ctx.send(embed=embed)
                            await message.add_reaction('✅')
                            await message.add_reaction('❌')

                            def check(reaction, user):
                                return user.id == ctx.author.id

                            try:
                                reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                            except asyncio.TimeoutError:
                                embed = discord.Embed(title=f'Эта роль уже есть в вашем инвентаре!', description='Окно было закрыто из-за неактивности')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                            else:
                                if str(reaction.emoji) == '✅':
                                    await ctx.author.add_roles(role)
                                    await db.delete_from_2args('inv', 'member', ctx.author.id, 'role', role.id)
                                    embed = discord.Embed(title='Эта роль уже есть в вашем инвентаре!', description=f'{ctx.author.mention}, вы успешно достали роль {role.mention} из вашего инвентаря!', colour=discord.Colour.gold())
                                    embed.set_thumbnail(url=ctx.author.avatar_url)
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)
                                elif str(reaction.emoji) == '❌':
                                    embed = discord.Embed(title='Эта роль уже есть в вашем инвентаре!', description=f'{ctx.author.mention}, вы отменили действие!', colour=discord.Colour.gold())
                                    embed.set_thumbnail(url=ctx.author.avatar_url)
                                    await message.clear_reactions()
                                    await message.edit(embed=embed)   

    @commands.command(aliases=['выдать', 'giverole'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __giveRole(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if member is None:
                message = await ctx.send(f"{ctx.author.mention}, укажите пользователя!")
                await asyncio.sleep(5)
                await message.delete()
            elif await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}') is not None:
                role_id = await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}')
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                inrole = 0
                for roles in member.roles:
                    if roles.id == role.id:
                        inrole = 1
                if inrole == 0:
                    await member.add_roles(role)
                    embed = discord.Embed(description=f'{ctx.author.mention}, вы выдали свою роль {role.mention} пользователю {member.mention}')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f'{ctx.author.mention}, у пользователя {member.mention} уже есть эта роль!')
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"{ctx.author.mention}, У вас нет личной роли. Используйте !создатьроль чтобы создать её")
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
    
    @commands.command(aliases=['createrole', 'создатьроль'])
    @commands.cooldown(1, 5, BucketType.member)
    async def __createrole(self, ctx, colour: discord.Colour = None, *, name: str = None):
        await ctx.message.delete()
        if ctx.channel.id != 856931259258372146 and ctx.channel.id != 857658033122836510:
            if colour is None or name is None:
                embed = discord.Embed(title='Что-то пошло не так! Попробуйте использовать эту команду так:',
                description=f'`!создатьроль #COLOUR *name*`\n\n**Пример:**\n`!создатьроль #ff0000 крутая роль!`')
                embed.set_thumbnail(url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
            else:
                cash = await db.select_value(f'SELECT cash FROM earth_users WHERE member = {ctx.author.id}')
                if await db.select_value(f'SELECT role FROM earth_private_roles WHERE owner = {ctx.author.id}') is None:
                    if cash >= 5000:
                        embed = discord.Embed(title=f'Покупка личной роли — {await get_nick(ctx.author)}',
                        description=f'**Название:** `{name}`\n**Цвет:** `{colour}` \nВаш текущий баланс: {cash} {COINS}\nВаш баланс после покупки: {cash - 5000}')
                        embed.set_footer(text='Вы сможете изменять название и цвет роли после покупки')
                        embed.set_thumbnail(url=ctx.author.avatar_url)
                        message = await ctx.send(embed=embed)
                        await message.add_reaction('✅')
                        await message.add_reaction('❌')

                        def check(reaction, user):
                            return user.id == ctx.author.id

                        try:
                            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=f'Покупка личной роли — {await get_nick(ctx.author)}', description='Окно было закрыто из-за неактивности')
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
                                support = discord.utils.get(ctx.guild.roles, id=861604082073862186)
                                position = support.position + 1
                                role = await ctx.guild.create_role(name=name, colour=colour)
                                await role.edit(position=position)
                                await ctx.author.add_roles(role)
                                await db.execute_table(f'INSERT INTO earth_private_roles VALUES ({role.id}, {end}, {ctx.author.id})')
                                await db.execute_table(f'UPDATE earth_users SET cash = cash - 5000 WHERE member = {ctx.author.id}')
                                embed = discord.Embed(title=f'Покупка личной роли — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы успешно приобрели личную роль {role.mention}!\n\n```Роль была оплачена на 30 дней, Для большей информации используйте !мояроль```')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                            elif str(reaction.emoji) == '❌':
                                embed = discord.Embed(title=f'Покупка личной роли — {await get_nick(ctx.author)}', description=f'{ctx.author.mention}, вы отменили покупку!')
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await message.clear_reactions()
                                await message.edit(embed=embed)
                    else:
                        message = await ctx.send(f'{ctx.author.mention}, у вас недостаточно коинов!')
                        await asyncio.sleep(5)
                        await message.delete()
                else:
                    message = await ctx.send(f'{ctx.author.mention}, у вас уже есть личная роль')
                    await asyncio.sleep(5)
                    await message.delete()


def setup(Bot):
    Bot.add_cog(PrivateRoles(Bot))