import discord
from discord import app_commands

@app_commands.command(name="license", description="View the bot's license")
async def license(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📄 License Information",
        description="**Amethis Discord Bot License**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> License File", 
        value="[View Full License on GitHub](https://github.com/yigit-guven/Amethis-Discord-bot/blob/main/LICENSE)", 
        inline=False
    )
    embed.add_field(
        name="<:forbidden:1427516790593949786> License Type", 
        value="READ-ONLY License", 
        inline=True
    )
    
    embed.set_footer(text="Please review the full license terms before use")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(license)
    print("License command loaded")