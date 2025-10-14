import os
import importlib
import discord
from discord.ext import commands
from discord import app_commands

class CommandLoader(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_commands_from_folder()
    
    def load_commands_from_folder(self):
        """Automatically load all command files from the commands directory"""
        commands_dir = "commands"
        
        if not os.path.exists(commands_dir):
            print(f"Warning: {commands_dir} directory not found")
            return
        
        # Get all Python files in the commands directory
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]  # Remove .py extension
                self.load_command_module(module_name)
    
    def load_command_module(self, module_name: str):
        """Load a single command module and register its commands"""
        try:
            # Import the module
            module = importlib.import_module(f"commands.{module_name}")
            
            # Look for a setup function or command classes
            if hasattr(module, 'setup'):
                # If the module has a setup function, use it
                module.setup(self.bot)
                print(f"Loaded command module: {module_name} (via setup)")
            else:
                # Otherwise, look for classes that inherit from app_commands.Group or have commands
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # If it's a command group, add it to the tree
                    if isinstance(attr, app_commands.Group):
                        self.bot.tree.add_command(attr)
                        print(f"Loaded command group: {module_name}.{attr_name}")
                    
                    # If it's a command, add it directly
                    elif isinstance(attr, app_commands.Command):
                        self.bot.tree.add_command(attr)
                        print(f"Loaded command: {module_name}.{attr_name}")
                        
        except Exception as e:
            print(f"Failed to load command module {module_name}: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandLoader(bot))