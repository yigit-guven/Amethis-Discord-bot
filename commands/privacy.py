import discord
from discord import app_commands

@app_commands.command(name="privacy", description="View our privacy policy")
async def privacy(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:shield:1427515556113809479> Privacy Policy",
        description="**Your privacy is important to us**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> Full Privacy Policy", 
        value="[Read Complete Privacy Policy](https://yigitguven.net/amethis/privacy)", 
        inline=False
    )
    
    embed.set_footer(text="We value your privacy and security")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(privacy)
    print("Privacy command loaded")