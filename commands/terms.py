import discord
from discord import app_commands

@app_commands.command(name="terms", description="View terms of service")
async def terms(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:scroll:1427519497207812168> Terms of Service",
        description="**Please read our terms carefully**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> Full Terms of Service", 
        value="[Read Complete Terms](https://yigitguven.net/amethis/terms)", 
        inline=False
    )
    
    embed.set_footer(text="By using this bot, you agree to our terms of service")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(terms)
    print("Terms command loaded")