import os
import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=os.getenv('APP_ID')
        )
    
    async def setup_hook(self):
        # Load the commands cog that will handle auto-loading
        await self.load_extension('cogs.commands')
        
        # Sync slash commands globally
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')