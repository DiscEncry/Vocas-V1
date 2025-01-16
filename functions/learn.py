import datetime, random, textwrap
from discord.ext import commands
from utilities.data import *
from utilities.paginator import *
from discord.ui import View, Modal, TextInput
import google.generativeai as genai

genai.configure(api_key="sec")
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_paragraph(words, config):
    story = model.generate_content(f"Make a {config} containing those words (they should be underlined using __ __ and spread throughout the paragraph, the other words should be easy words): {', '.join(words)}").text
    max_page_length = 1000
    return textwrap.wrap(story, max_page_length)

def pages_from_paragraphs(paragraphs):
    return [
        discord.Embed(title="Learning Session", description=paragraph, color=discord.Color.green())
            .set_footer(text=f"Page {index + 1}/{len(paragraphs)}")  # Add footer with page number
            for index, paragraph in enumerate(paragraphs)
    ]

def user_summary(user_id):
    user_ref, user = get_user_data(user_id)
    vocab = user['vocab']
    now = int(datetime.datetime.now().timestamp())
    total_vocab = len(vocab)
    learned_vocab = sum(1 for word, data in vocab.items() if data['time_to_revise'] > now)
    understand_percentage = (learned_vocab / total_vocab * 100) if total_vocab > 0 else 0

    embed = discord.Embed(title="Learning Profile", color=discord.Color.blue())
    embed.add_field(name="Total Vocabulary", value=total_vocab)
    embed.add_field(name="Learned", value=learned_vocab)
    embed.add_field(name="Progress", value=f"{understand_percentage:.2f}%", inline=False)

    return embed

class LearningSetupView(View):
    def __init__(self, ctx, user_ref, user):
        super().__init__()
        self.ctx = ctx
        self.user_ref = user_ref
        self.user = user

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: Button):
        modal = LearningModal(self.ctx, self.user_ref, self.user)
        await interaction.response.send_modal(modal)

class LearningModal(Modal, title="Learning Preferences"):
    def __init__(self, ctx, user_ref, user):
        super().__init__()
        self.ctx = ctx
        self.user_ref = user_ref
        self.user = user

    num_words = TextInput(label="Number of Words", placeholder="Enter number of words (default 12, must <= 50)", required=False)
    paragraph_config = TextInput(label="Paragraph Config", placeholder="Enter paragraph config (default: medium-length story)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        num_words = int(self.num_words.value) if self.num_words.value else 12
        if num_words > 50: await interaction.message.edit(content = "Please enter number of words smaller or equal to 50")
        paragraph_config = str(self.paragraph_config.value) if self.paragraph_config.value else "medium-length story"
        msg = None

        vocab = self.user['vocab']
        now = int(datetime.datetime.now().timestamp())
        words_to_learn = [word for word, data in vocab.items() if data['time_to_revise'] <= now]
        if len(words_to_learn) < num_words:
            words_to_learn += [word for word, _ in sorted(vocab.items(), key=lambda x: x[1]['time_to_revise'])[:num_words-len(words_to_learn)]]
            msg = "Words that are already learned within deadline will not be progressed."

        await interaction.message.edit(content = "Generating...")
        random_words = random.sample(words_to_learn, min(len(words_to_learn), num_words))
        paragraphs = generate_paragraph(random_words, paragraph_config)
        embed_pages = pages_from_paragraphs(paragraphs)

        view = ParagraphPaginatorView(self.ctx, self.user_ref, self.user, random_words, paragraph_config, embed_pages)
        await interaction.message.edit(content = msg, embed = embed_pages[0], view = view)

class ParagraphPaginatorView(UniversalPaginator):
    def __init__(self, ctx, user_ref, user, words, paragraph_config, embed_pages):
        super().__init__(ctx, embed_pages)
        self.user_ref = user_ref
        self.user = user
        self.words = words
        self.paragraph_config = paragraph_config

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green, row=1)
    async def done(self, interaction: discord.Interaction, button: Button):
        now = int(datetime.datetime.now().timestamp())
        for word in self.words:
            data = self.user['vocab'][word]
            if now >= data['time_to_revise']:
                days_to_add = 2 ** data['times_learned']
                data['times_learned'] += 1
                data['time_to_revise'] = now + days_to_add * 86400

        self.user_ref.update(self.user)
        embed = user_summary(str(self.ctx.author.id))
        await interaction.response.edit_message(content="Session Completed. Progress saved.", embed=embed, view=None)

    @discord.ui.button(label="Remake", style=discord.ButtonStyle.blurple, row=1)
    async def remake(self, interaction: discord.Interaction, button: Button):
        paragraphs = generate_paragraph(self.words, self.paragraph_config)
        self.pages=pages_from_paragraphs(paragraphs)
        self.current_page = 0
        await self.update_buttons(interaction)

class Learn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def learn(self, ctx):
        user_id = str(ctx.author.id)
        embed = user_summary(user_id)
        user_ref, user = get_user_data(user_id)
        view = LearningSetupView(ctx, user_ref, user)

        await ctx.send(embed=embed, view=view)

# Set up the cog
def setup(bot):
    bot.add_cog(Learn(bot))