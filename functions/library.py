from utilities.paginator import UniversalPaginator
from utilities.data import *
import discord
from discord.ext import commands
from discord.ui import Button, Select

class WordPaginatorView(UniversalPaginator):
    def __init__(self, ctx, vocab):
        self.vocab = vocab
        self.sort_method = "alphabet"
        self.reverse_order = False
        self.generate_embeds()
        super().__init__(ctx, self.pages)

    def generate_embeds(self):
        sorted_vocab = self.sort_vocab()
        self.pages = []
        self.current_page = 0
        words_per_page = 20

        for i in range(0, len(sorted_vocab), words_per_page):
            chunk = sorted_vocab[i:i + words_per_page]
            embed = discord.Embed(title="Your Saved Words", color=discord.Color.green())

            # Divide words into two rows
            row1 = chunk[:words_per_page//2]
            row2 = chunk[words_per_page//2:]

            if row1:
                value = "\n".join(
                    f"**{word}** - <t:{int(data['time_to_revise'])}:R>"
                    for word, data in row1
                )
                embed.add_field(name="Row 1", value=value, inline=True)

            if row2:
                value = "\n".join(
                    f"**{word}** - <t:{int(data['time_to_revise'])}:R>"
                    for word, data in row2
                )
                embed.add_field(name="Row 2", value=value, inline=True)

            embed.set_footer(
                text=f"Page {len(self.pages) + 1}/{(len(sorted_vocab) + words_per_page - 1) // words_per_page}"
            )
            self.pages.append(embed)

    def sort_vocab(self):
        if self.sort_method == "alphabet":
            return sorted(self.vocab.items(), key=lambda x: x[0], reverse=self.reverse_order)
        elif self.sort_method == "time_to_revise":
            return sorted(self.vocab.items(), key=lambda x: x[1]['time_to_revise'], reverse=self.reverse_order)
   

    @discord.ui.button(label="Reverse", style=discord.ButtonStyle.gray, row=0)
    async def reverse(self, interaction: discord.Interaction, button: Button):
        self.reverse_order = not self.reverse_order
        self.generate_embeds()
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.select(
        placeholder="Select sorting method",
        options=[
            discord.SelectOption(label="Alphabetical", value="alphabet"),
            discord.SelectOption(label="Lowest Time to Revise", value="time_to_revise"),
        ],
        row=1,
    )
    async def sort_dropdown(self, interaction: discord.Interaction, select: Select):
        self.sort_method = select.values[0]
        self.generate_embeds()
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

# Create a cog class
class Library(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def library(self, ctx):
        user_id = str(ctx.author.id)
        user_ref, user = get_user_data(user_id)
        vocab = user['vocab']

        if not vocab:
            await ctx.send("You have no saved words.")
            return

        view = WordPaginatorView(ctx, vocab)
        await ctx.send(embed=view.pages[0], view=view)

# Set up the cog
def setup(bot):
    bot.add_cog(Library(bot))