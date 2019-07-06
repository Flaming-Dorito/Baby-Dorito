import discord
from discord.ext import commands
import datetime


class ListenerCog(commands.Cog):

    def __init__(self, bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self._bot.user in message.mentions:
            emb = discord.Embed(title=f"Hi there!", type="rich", description=f"I'm Baby-Dorito. my prefix is `{self._bot.get_prefix(message)}`. Use the command `{self._bot.get_prefix(message)}help` for more info.", color=0x00ff00, timestamp=datetime.datetime.utcnow())
            emb.set_footer(text=f"Requested by {message.author}")
            await message.channel.send(embed=emb)


def setup(bot):
    bot.add_cog(ListenerCog(bot))
