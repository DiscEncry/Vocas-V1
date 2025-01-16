from bs4 import BeautifulSoup
from utilities.data import *
from utilities.paginator import UniversalPaginator
from discord.ui import Button, TextInput, Modal
import discord, sqlite3

conn = sqlite3.connect("dict_hh.db")
cursor = conn.cursor()

def parse_html_to_discord_format(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    title = soup.find('h1').text.strip()
    pronunciation = soup.find('h3').text.strip()
    discord_message = f"**{title}** {pronunciation}\n\n"

    # Process each section (h2 and corresponding ul/ol)
    for section in soup.find_all('h2'):
        section_title = section.text.strip()
        discord_message += f"__{section_title}__\n"

        # Find the next <ul> or <ol> after the current <h2>
        list_tag = section.find_next_sibling(['ul', 'ol'])
        if list_tag:
            for li in list_tag.find_all('li', recursive=False):
                main_meaning = li.contents[0].strip() if li.contents else ""
                discord_message += f"- {main_meaning}\n"

                # Process examples in nested <ul>
                nested_list = li.find(['ul', 'ol'])
                if nested_list:
                    for example in nested_list.find_all('li'):
                        example_text = example.contents[0].strip() if example.contents else ""
                        example_meaning = example.find('i').text.strip() if example.find('i') else ""
                        discord_message += f"  - {example_text} (*{example_meaning}*)\n"

        discord_message += "\n"

    return discord_message

def split_into_pages(text, max_length=1000):
    lines = text.splitlines()
    pages = []
    current_page = ""
    
    for line in lines:
        if len(current_page) + len(line) + 1 <= max_length:
            if current_page:
                current_page += "\n" + line
            else:
                current_page = line
        else:
            pages.append(current_page)
            current_page = line
    
    if current_page:
        pages.append(current_page)
    
    return pages

class EmbedPaginator(UniversalPaginator):
    def __init__(self, ctx, embeds):
        super().__init__(ctx, embeds)
        self.search_button = Button(label="Search", style=discord.ButtonStyle.secondary)
        self.search_button.callback = self.search_modal
        self.add_item(self.search_button)

    async def search_modal(self, interaction):
        class SearchModal(Modal):
            def __init__(self, paginator):
                super().__init__(title="Search for a Word")
                self.paginator = paginator
                self.word_input = TextInput(
                    label="Enter word:",
                    placeholder="Type a word to search",
                    required=True
                )
                self.add_item(self.word_input)

            async def on_submit(self, interaction: discord.Interaction):
                word = self.word_input.value.lower()
                pages = search_command(word)

                if not pages:
                    no_result_embed = discord.Embed(
                        title="No Results",
                        description=f"No matches found for **{word}**.",
                        color=discord.Color.red()
                    )
                    self.paginator.pages = [no_result_embed]
                else:
                    self.paginator.pages = pages

                self.paginator.current_page = 0
                await self.paginator.update_buttons(interaction)

        await interaction.response.send_modal(SearchModal(self))

def search_command(word):
    cursor.execute("SELECT html FROM av WHERE word = ?", (word,))
    html = cursor.fetchone()

    if not html:
        return

    html_content = html[0]
    formatted_text = parse_html_to_discord_format(html_content)

    chunks = split_into_pages(formatted_text)
    embeds = [discord.Embed(description=chunk, color=discord.Color.blue()).
              set_footer(text=f"Page {i + 1} of {len(chunks)}") for i, chunk in enumerate(chunks)]

    return embeds

from discord.ext import commands

# Create a cog class
class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def search(self, ctx, *, word):
        embeds = search_command(word)
        if not embeds: await ctx.send(content = "No result found.")
        await ctx.send(embed=embeds[0], view=EmbedPaginator(ctx, embeds))

# Set up the cog
def setup(bot):
    bot.add_cog(Search(bot))