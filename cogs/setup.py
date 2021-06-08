import typing
import discord
import cogs.utils as utils
import voxelbotutils as vbu
from discord.ext import commands


class Setup(vbu.Cog):

    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    @utils.checks.setup_not_complete()
    async def setup(self, ctx:vbu.Context):
        """
        Setup bot.
        """

        await ctx.trigger_typing()
        message:discord.Message = await ctx.send('`Creating muted role...`')
        setup_info = f'This is a part of the {ctx.bot.user} setup run by {ctx.author}'

        await ctx.trigger_typing()
        muted_role = await ctx.guild.create_role(
            name='muted',
            permissions=discord.Permissions(send_messages=False),
            colour=discord.Colour(0x202020),
            reason=setup_info)
        
        for channel in await ctx.guild.fetch_channels():
            await channel.set_permissions(muted_role, send_messages=False)

        async with vbu.DatabaseConnection() as db:
            await db('''
                INSERT INTO guild_settings (guild_id, muted_role_id) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO
                    UPDATE SET muted_role_id = $2;
                ''', ctx.guild.id, muted_role.id)

        await ctx.send('`Created muted role!`')
        await ctx.send('`Setup complete.`')



def setup(bot:vbu.Bot):
    x = Setup(bot)
    bot.add_cog(x)