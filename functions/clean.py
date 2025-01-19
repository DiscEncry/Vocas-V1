from discord.ext import commands
from utilities.data import get_user_data, is_valid_word

class Clean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clean(self, ctx):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        
        # Track changes for reporting
        changes_made = []
        words_to_delete = []
        
        # Scan through vocabulary
        for word in user['vocab'].copy():
            if not word.islower():  # Check if word contains uppercase
                lowercase_word = word.lower()
                
                # If lowercase version doesn't exist, add it
                if lowercase_word not in user['vocab']:
                    user['vocab'][lowercase_word] = user['vocab'][word].copy()
                    changes_made.append(f"{word} → {lowercase_word}")
                else:
                    changes_made.append(f"{word} (removed - {lowercase_word} already exists)")
                
                # Mark original uppercase word for deletion
                words_to_delete.append(word)
        
        # Delete uppercase words
        for word in words_to_delete:
            del user['vocab'][word]
            
        # Update database if changes were made
        if changes_made:
            user_ref.update({'vocab': user['vocab']})
            
            # Create report message
            report = "Vocabulary cleaned:\n"
            report += "\n".join(changes_made)
            await ctx.send(report)
        else:
            await ctx.send("No uppercase words found in your vocabulary.")

async def setup(bot):
    await bot.add_cog(Clean(bot))