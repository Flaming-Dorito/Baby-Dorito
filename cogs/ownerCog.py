import discord
from discord.ext import commands
import datetime


class NotAuthorised(commands.CheckFailure):
    pass


class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self._bot = bot

    def is_owner():
        async def predicate(ctx):
            if ctx.author.id != 205333110731046913:
                raise NotAuthorised('Not Authorised')
            return True
        return commands.check(predicate)

    @commands.command()
    @is_owner()
    async def stop(self, ctx):
        emb = discord.Embed(title="Stopping Baby-Dorito", type="rich", description="Baby-Dorito is stopping.", color=0x00ff00, timestamp=datetime.datetime.utcnow())
        emb.set_thumbnail(url="https://res.cloudinary.com/teepublic/image/private/s--b4YQ-RHz--/t_Preview/b_rgb:6e2229,c_limit,f_jpg,h_630,q_90,w_630/v1516782493/production/designs/2304606_0.jpg")
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)
        await self._bot.logout()

    @commands.command()
    @is_owner()
    async def listext(self, ctx):
        await ctx.send(f"Extensions: {list(self._bot.extensions.keys())}")

    @commands.command()
    @is_owner()
    async def unload(self, ctx, cog):
        try:
            self._bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command()
    @is_owner()
    async def reload(self, ctx, cog):
        try:
            self._bot.unload_extension(cog)
        except Exception as e:
            if type(e).__name__ != "ExtensionNotLoaded":
                await ctx.send(f'**`ERROR unloading:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS unloading`**')
        try:
            self._bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR loading:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS loading`**')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, NotAuthorised):
            emb = discord.Embed(title=f"Error: {error}", type="rich", description="You are not authorised to use this command.", color=0xff0000, timestamp=datetime.datetime.utcnow())
            emb.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(OwnerCog(bot))
