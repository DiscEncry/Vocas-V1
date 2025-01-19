from discord.ext import commands
from utilities.data import get_user_data
import discord
import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx, word: str):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        
        # Check if word exists in user's vocabulary
        if word not in user['vocab']:
            await ctx.send(f"'{word}' is not in your vocabulary.")
            return
            
        # Get word data
        word_data = user['vocab'][word]
        
        # Calculate time until next revision
        now = int(datetime.datetime.now().timestamp())
        time_to_revise = word_data['time_to_revise']
        time_remaining = time_to_revise - now
        
        # Calculate learning progress
        learning_level = word_data['times_learned']
        next_interval = 1.3 ** learning_level if learning_level > 0 else 0  # Days until next revision
        
        # Create embed
        embed = discord.Embed(
            title=f"Word Information: {word}",
            color=discord.Color.blue()
        )
        
        # Add fields
        embed.add_field(
            name="Learning Level",
            value=f"Level {learning_level}",
            inline=True
        )
        
        embed.add_field(
            name="Next Review Interval",
            value=f"{next_interval} days",
            inline=True
        )
        
        # Status field - whether it needs review or not
        status = "Needs Review" if time_remaining <= 0 else "Up to Date"
        embed.add_field(
            name="Status",
            value=status,
            inline=True
        )
        
        # Next review timestamp
        embed.add_field(
            name="Next Review",
            value=f"<t:{time_to_revise}:R>",
            inline=True
        )
        
        # Progress visualization
        if learning_level > 0:
            progress_bar = "🟦" * learning_level + "⬜" * (10 - learning_level)
            embed.add_field(
                name="Learning Progress",
                value=progress_bar,
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))