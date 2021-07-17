import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from data.config import events, get_nick, limits, descs, picts


class Events(commands.Cog):

    def __init__(self, Bot):
        self.Bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Events module connected!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            if after.channel.id == 864468150748577814:
                channel = discord.utils.get(after.channel.guild.channels, id=865211840015630336)
                embed = discord.Embed(title=f'Список доступных ивентов — {await get_nick(member)}', color=discord.Colour(0x36393E))
                description = ''
                for i in range(len(events)):
                    description += f'**{i + 1}) {events[i]}** (Макс. участников: {limits[i]})\n'
                embed.description = description
                embed.set_footer(text='Чтобы запустить ивент используйте команду !ивент *номер*')
                embed.set_thumbnail(url='https://media.discordapp.net/attachments/606564810255106210/862404230479216690/icons8--96.png')
                msg = await channel.send(f'{member.mention}', embed=embed)
                await asyncio.sleep(30)
                await msg.delete()
    
    @commands.command(aliases=['ивент' , 'event'])
    @commands.has_any_role(857610144250200075, 862638189284818974)
    @commands.cooldown(1, 3, BucketType.member)
    async def __event(self, ctx, num: int = None):
        await ctx.message.delete()
        if len(events) >= num:
            if ctx.author.voice.channel is not None:
                if ctx.author.voice.channel.id == 864468150748577814:
                    emoji = '<:earth_right1:862402924154978325>'
                    name1 = events[num - 1]
                    name = '・' + name1
                    category = discord.utils.get(ctx.guild.categories, id=864466750493556736)
                    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=True, send_messages=False),
                                  ctx.author: discord.PermissionOverwrite(manage_permissions=True, manage_channels=True, connect=True, send_messages=True)}
                    await ctx.guild.create_text_channel(name=name, overwrites=overwrites, category=category)
                    voice = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, category=category, user_limit=limits[num - 1])
                    await ctx.author.move_to(voice)
                    invite = await voice.create_invite()
                    channel = discord.utils.get(ctx.guild.channels, id=865211769629966336)
                    embed = discord.Embed(color=discord.Colour(0x36393E))
                    embed.description = f'{emoji} Ивент: «**{name1}**».\n\n{emoji} Ведущий: {ctx.author.mention}.\n\n```{descs[num - 1]}```\n\n{emoji} Ссылка на канал: [подключиться]({invite})'
                    embed.set_image(url=picts[num - 1])
                    await channel.send('<@&865216611639754753>', embed=embed)
        else:
            embed = discord.Embed(title=f'Ошибка! — {await get_nick(ctx.author)}',
            description='Ивента с таким порядковым номером не найдено!', color=discord.Colour(0x36393E))
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/859153448309096458/863041118300274688/icons8----96.png')
            await ctx.send(embed=embed)

    
def setup(Bot):
    Bot.add_cog(Events(Bot))