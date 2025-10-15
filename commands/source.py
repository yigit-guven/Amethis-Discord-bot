import discord
from discord import app_commands

@app_commands.command(name="source", description="View the bot's source code")
async def source(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:scroll:1427519497207812168> Source Code",
        description="**Amethis Discord Bot - Open Source**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> GitHub Repository", 
        value="[View Source Code on GitHub](https://github.com/yigit-guven/Amethis-Discord-bot)", 
        inline=False
    )
    embed.add_field(
        name="<:star:1427517629244903434> Star the Repo", 
        value="If you like this bot, consider giving it a star on GitHub!", 
        inline=False
    )
    embed.add_field(
        name="<:bug:1427786269005451424> Issues & Contributions", 
        value="Found a bug? Feel free to open an issue!", 
        inline=False
    )
    
    embed.set_footer(text="Open source and free to use")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(source)