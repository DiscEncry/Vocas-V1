from discord.ext import commands
from utilities.data import get_user_data

# Create a cog class
class Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def delete(self, ctx, word):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        if word in user['vocab']:
            del user['vocab'][word]
            user_ref.update({'vocab': user['vocab']})
            await ctx.send(f"Deleted word: {word}")
        else:
            await ctx.send(f"Word not found: {word}")

# Set up the cog
async def setup(bot):
    await bot.add_cog(Delete(bot))