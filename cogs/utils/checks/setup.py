import typing
import asyncpg
import voxelbotutils as vbu
from discord.ext import commands


class CheckFailure(commands.CommandError):
    """
    Generic error for check failure.
    """

async def fetch_guild_settings(ctx:vbu.Context) -> typing.List[asyncpg.Record]:
    """"
    Fetch guild settings.
    """

    if ctx.guild:
        async with ctx.bot.database() as db:
            return await db('''
                SELECT * FROM guild_settings
                WHERE guild_id = $1;
                ''', ctx.guild.id)
    return []

def setup_complete():
    """
    Check if bot setup is complete.
    """

    async def predicate(ctx:vbu.Context):
        if await fetch_guild_settings(ctx):
            return True
        raise CheckFailure(f'Your server hasn\'t yet been set up. Use {ctx.prefix}setup')
    return commands.check(predicate)

def setup_not_complete():
    """
    Check if bot setup is not complete.
    """

    async def predicate(ctx:vbu.Context):
        if await fetch_guild_settings(ctx):
            raise CheckFailure('Your server has already been set up.')
        return True
    return commands.check(predicate)