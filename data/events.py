from discord.ext import commands

class Events():

    def __init__(self, Bot):
        self.bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')

def setup(Bot):
    Bot.add_cog(Events(Bot))