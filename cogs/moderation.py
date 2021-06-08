import typing
import discord
import datetime
import cogs.utils as utils
import voxelbotutils as vbu
from discord.ext import commands


class Moderation(vbu.Cog):

    def __init__(self, bot):
        self.bot = bot

    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @utils.checks.setup_complete()
    async def kick(self, ctx:vbu.Context, member:discord.Member, *, reason:typing.Optional[str]='None.'):
        """
        Kick a user.
        """

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You can only ban members below you.")

        await ctx.trigger_typing()
        await member.send(f"You've been **kicked** from **{ctx.guild}**\nReason: {reason}")
        await member.kick(reason=f"Kicked by {ctx.author}. Reason: {reason}")
        await ctx.send(f"{member} `({member.id})` has been **kicked** by {ctx.author.mention}\nReason: {reason}")

    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @utils.checks.setup_complete()
    async def ban(self, ctx:vbu.Context, member:discord.Member, *, reason:typing.Optional[str]='None.'):
        """
        Ban a user.
        """

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You can only ban members below you.")

        await ctx.trigger_typing()
        await member.send(f"You've been **banned** from **{ctx.guild}**\nReason: {reason}")
        await member.ban(reason=f"Banned by {ctx.author}. Reason: {reason}")
        await ctx.send(f"{member} `({member.id})` has been **banned** by {ctx.author.mention}\nReason: {reason}")
    
    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @utils.checks.setup_complete()
    async def unban(self, ctx:vbu.Context, user_id:int, *, reason:typing.Optional[str]='None.'):
        """"
        Unban a user with their user ID.
        """

        await ctx.trigger_typing()
        try:
            user = [ban_entry.user for ban_entry in await ctx.guild.bans() if ban_entry.user.id == user_id][0]
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"{user} `({user.id})` has been **unbanned** by {ctx.author.mention}\nReason: {reason}")
        except IndexError:
            await ctx.send(f"No banned user with the ID of `{user_id}` found.")

    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.checks.setup_complete()
    async def mute(self, ctx:vbu.Context, member:discord.Member, *, duration:typing.Optional[typing.Union[str, int]]=None):
        """
        Mute a user for a set duration.
        """

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You can only mute members below you.")

        if isinstance(duration, str):
            multiply = {
                's':1,          # seconds
                'm':60,         # minutes
                'h':3600,      # hours
                'd':86400,   # days
                }
            
            seconds = 0
            for i in duration.split():
                seconds += int(i[:-1])*multiply[i[-1]]
            if seconds < 0 or seconds > 31556926: # ? 31556926 is a year in seconds.
                return await ctx.send('Something wen\'t wrong. `(INVALID_TIME)`')
            time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

        elif isinstance(duration, int):
            if duration < 0 or duration > 31556926: # ? 31556926 is a year in seconds.
                return await ctx.send('Something wen\'t wrong. `(INVALID_TIME)`')
            time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        
        else:
            time = None
        
        async with vbu.DatabaseConnection() as db:
            await db('''
                INSERT INTO muted (guild_id, user_id, time)
                VALUES ($1, $2, $3)
                ON CONFLICT ON CONSTRAINT muted_pkey DO
                    UPDATE SET time = $3;
                ''', ctx.guild.id, member.id, time)
            fetched = await db('''SELECT muted_role_id FROM guild_settings WHERE guild_id = $1''', ctx.guild.id)
        
        muted_role = ctx.guild.get_role(fetched[0]['muted_role_id'])
        await member.add_roles(muted_role)
        
        if time is None:
            time = 'indefinitely'
        else:
            time = f'untill {time.strftime("%b %d %Y %H:%M:%S")}'
        await ctx.send(f'{member} `({member.id})` has been **muted** by {ctx.author.mention} {time}')
    
    @vbu.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @utils.checks.setup_complete()
    async def unmute(self, ctx:vbu.Context, member:discord.Member):
        async with vbu.DatabaseConnection() as db:
            await db('''DELETE FROM muted WHERE guild_id = $1 AND user_id = $2''', ctx.guild.id, member.id)
            fetched = await db('''SELECT muted_role_id FROM guild_settings WHERE guild_id = $1''', ctx.guild.id)
        
        muted_role = ctx.guild.get_role(fetched[0]['muted_role_id'])
        await member.remove_roles(muted_role)
        await ctx.send(f'{member} `({member.id})` has been **unmuted**  by {ctx.author.mention}')



def setup(bot:vbu.Bot):
    x = Moderation(bot)
    bot.add_cog(x)