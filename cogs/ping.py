import voxelbotutils as vbu


class MiscCommands(vbu.Cog):

    @vbu.command()
    async def ping(self, ctx:vbu.Context):
        """
        Pong!
        """

        await ctx.trigger_typing()
        await ctx.send("Pong!")


def setup(bot:vbu.Bot):
    x = MiscCommands(bot)
    bot.add_cog(x)