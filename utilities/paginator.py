import discord
from discord.ui import View, Button

class UniversalPaginator(View):
    def __init__(self, ctx, pages):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0

        # Navigation Buttons
        self.previous_button = Button(label="Previous", style=discord.ButtonStyle.blurple, disabled=True)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.blurple, disabled=len(pages) <= 1)

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    async def update_buttons(self, interaction):
        """Update button states and refresh the message."""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
        content = self.pages[self.current_page]
        if isinstance(content, discord.Embed):
            await interaction.response.edit_message(embed=content, view=self)
        else:
            await interaction.response.edit_message(content=content, view=self)

    async def previous_page(self, interaction):
        """Navigate to the previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons(interaction)

    async def next_page(self, interaction):
        """Navigate to the next page."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_buttons(interaction)
