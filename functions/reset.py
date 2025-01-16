from discord.ext import commands
from utilities.data import get_user_data
import datetime

# Create a cog class
class Reset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reset(self, ctx):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        for word in user['vocab']:
            user['vocab'][word]['time_to_revise'] = int(datetime.datetime.now().timestamp())
            user['vocab'][word]['times_learned'] = 0
        user_ref.update({'vocab': user['vocab']})
        await ctx.send("Progress has been reset for all words.")

# Set up the cog
def setup(bot):
    bot.add_cog(Reset(bot))
