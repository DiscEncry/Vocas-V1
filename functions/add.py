import datetime
from discord.ext import commands
from utilities.data import get_user_data, is_valid_word

class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, *args):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        invalid_words = []
        if len(ctx.message.attachments) == 1 and ctx.message.attachments[0].filename.endswith('.txt'):
            attachment = ctx.message.attachments[0]
            content = await attachment.read()
            words_in_file = content.decode('utf-8').splitlines()
            new_words = 0
            for word in words_in_file:
                if is_valid_word(word):
                    if word not in user['vocab']:
                        user['vocab'][word] = {
                            'time_to_revise': int(datetime.datetime.now().timestamp()),
                            'times_learned': 0
                        }
                        new_words += 1
                else:
                    invalid_words.append(word)
            user_ref.update({'vocab': user['vocab']})
            await ctx.send(f"Added {new_words} valid words from {attachment.filename}. Invalid words: {', '.join(invalid_words)}")
        else:
            new_words = []
            for word in args:
                if is_valid_word(word):
                    if word not in user['vocab']:
                        user['vocab'][word] = {
                            'time_to_revise': int(datetime.datetime.now().timestamp()),
                            'times_learned': 0
                        }
                        new_words.append(word)
                else:
                    invalid_words.append(word)
            user_ref.update({'vocab': user['vocab']})
            await ctx.send(f"Added valid words: {new_words}. Invalid words: {', '.join(invalid_words)}")

# Set up the cog
def setup(bot):
    bot.add_cog(Add(bot))