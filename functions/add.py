from discord.ext import commands
from utilities.data import *

class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, *args):
        user_id = str(ctx.author.id)
        if len(ctx.message.attachments) == 1 and ctx.message.attachments[0].filename.endswith('.txt'):
            attachment = ctx.message.attachments[0]
            content = await attachment.read()
            words_in_file = content.decode('utf-8').splitlines()
            
            results = []
            for word in words_in_file:
                success, message = add_word_to_vocab(user_id, False, word)
                if not success:
                    results.append(f"Failed: {message}")
                else:
                    results.append(message)
                    
            await ctx.send("\n".join(results))
        else:
            results = []
            for word in args:
                success, message = add_word_to_vocab(user_id, False, word)
                results.append(message)
            
            await ctx.send("\n".join(results))

# Set up the cog
async def setup(bot):
    await bot.add_cog(Add(bot))