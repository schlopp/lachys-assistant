import datetime
import voxelbotutils as vbu
from discord.ext import tasks


class Events(vbu.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.unmute.start()

    @tasks.loop(seconds=5)
    async def unmute(self):
        """
        Unmute users at the appropriate time.
        """

        print('yooo!')
        now = datetime.datetime.now()
        async with vbu.DatabaseConnection() as db:
            fetched = await db('''SELECT * FROM muted''')
            for row in fetched:
                if row['time'] is not None and row['time'] < now:
                    await db('''DELETE FROM muted WHERE guild_id = $1 AND user_id = $2''', row['guild_id'], row['user_id'])
                    fetched = await db('''SELECT muted_role_id FROM guild_settings WHERE guild_id = $1''', row['guild_id'])
                    guild = self.bot.get_guild(row['guild_id'])
                    member = guild.get_member(row['user_id'])
                    role = guild.get_role(fetched[0]['muted_role_id'])
                    await member.remove_roles(role)
                    await member.send(f'You\'ve been unmuted from **{guild.name}**')



def setup(bot:vbu.Bot):
    x = Events(bot)
    bot.add_cog(x)