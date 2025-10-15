import discord
from discord import app_commands

@app_commands.command(name="invite", description="Invite Amethis to your server")
async def invite(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:amethyst:1427510624048382134> Invite Amethis",
        description="**Want to add me to your server?**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> Invite Link", 
        value=f"[Click here to invite me!](https://discord.com/oauth2/authorize?client_id=1426595196208021554)", 
        inline=False
    )

    embed.add_field(
        name="<:question:1427511257275301959> Need Help?",
        value="Join our [support server](https://discord.gg/dmjPtN44Fv) if you need assistance with setup!",
        inline=False
    )
    
    embed.set_footer(text="Thank you for choosing Amethis! 💜")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(invite)