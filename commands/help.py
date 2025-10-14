import discord
from discord import app_commands

@app_commands.command(name="help", description="Show help information")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Help",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )
    
    # Get all registered commands
    commands_list = []
    for command in interaction.client.tree.get_commands():
        if isinstance(command, app_commands.Command):
            commands_list.append((f"/{command.name}", command.description or "No description"))
    
    for name, description in commands_list:
        embed.add_field(name=name, value=description, inline=False)
    
    embed.set_footer(text="Use / before each command to see available options")
    
    await interaction.response.send_message(embed=embed)

# Setup function for auto-loading
def setup(bot):
    bot.tree.add_command(help)
    print("Help command loaded")