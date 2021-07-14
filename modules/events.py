import discord
from discord.ext import commands
from data.config import events, get_nick, limits


class Events(commands.Cog):

    def __init__(self, Bot):
        self.Bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Events module connected!')
    
    @commands.command(aliases=['ивент' , 'event'])
    @commands.has_any_role(857610144250200075, 862638189284818974)
    async def __event(self, ctx, num: int = None):
        await ctx.message.delete()
        if len(events) >= num:
            if ctx.author.voice.channel is not None:
                if ctx.author.voice.channel.id == 864468150748577814:
                    name = events[num - 1]
                    name = '・' + name
                    category = discord.utils.get(ctx.guild.categories, id=864466750493556736)
                    overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=True, send_messages=False),
                                  ctx.author: discord.PermissionOverwrite(manage_permissions=True, manage_channels=True, connect=True, send_messages=True)}
                    await ctx.guild.create_text_channel(name=name, overwrites=overwrites, category=category)
                    voice = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, category=category, user_limit=limits[num - 1])
                    await ctx.author.move_to(voice)
        else:
            embed = discord.Embed(title=f'Ошибка! — {await get_nick(ctx.author)}',
            description='Ивента с таким порядковым номером не найдено!', color=discord.Colour(0x36393E))
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/859153448309096458/863041118300274688/icons8----96.png')
            await ctx.send(embed=embed)

    
def setup(Bot):
    Bot.add_cog(Events(Bot))