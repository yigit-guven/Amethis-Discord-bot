import os
import discord
from discord.ext import commands
import asyncio

class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=os.getenv('APP_ID')
        )
    
    async def setup_hook(self):
        
        await self.load_extension('cogs.commands')
        
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        self.loop.create_task(self.rotate_status())
    
    async def rotate_status(self):
        await self.wait_until_ready()
        
        while not self.is_closed():
            statuses = [
                discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"),
                discord.Activity(type=discord.ActivityType.playing, name="Use /help for commands"),
                discord.Activity(type=discord.ActivityType.watching, name="your commands"),
                discord.Activity(type=discord.ActivityType.listening, name="slash commands")
            ]
            
            for activity in statuses:
                await self.change_presence(activity=activity)
                await asyncio.sleep(30)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Connected to {len(self.guilds)} servers')
        print('------')