import discord
from discord import app_commands

@app_commands.command(name="about", description="Learn more about Amethis")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:heart:1427788237832847441> Hello! I'm Amethis",
        description="**Your transparent, open-source Discord companion**",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:hand:1427789603863007416> Who Am I?", 
        value="I'm Amethis, a multi-purpose Discord bot designed to make your server management enjoyable and transparent! I believe everyone deserves a feature-rich bot without compromising privacy.", 
        inline=False
    )
    
    embed.add_field(
        name="<:question:1427511257275301959> What I Can Do",
        value="• **Moderation**: Keep your server safe and organized\n• **Economy**: Fun currency systems and games\n• **Automation**: Smart tools to simplify management\n• **Entertainment**: Games and fun commands for everyone\n• **Utilities**: Helpful features for daily server use",
        inline=False
    )
    
    embed.add_field(
        name="<:star:1427517629244903434> What Makes Me Special",
        value="• **Completely Free**: No paywalls, no premium tiers\n• **Open Source**: [View my code anytime](https://github.com/yigit-guven/Amethis-Discord-bot)\n• **Privacy-First**: Your data belongs to you\n• **Transparent**: No hidden features or data collection\n• **Community-Driven**: Built with user feedback in mind",
        inline=False
    )
    
    embed.add_field(
        name="<:amethyst:1427510624048382134> My Philosophy",
        value="I believe that powerful tools should be accessible to everyone. That's why I'm free, open-source, and committed to protecting your privacy while providing amazing features!",
        inline=False
    )
    
    embed.add_field(
        name="<:link:1427518497012846612> Quick Links",
        value="[Website](https://yigitguven.net/amethis) • [Terms](https://yigitguven.net/amethis/terms) • [Privacy](https://yigitguven.net/amethis/privacy)",
        inline=False
    )
    
    embed.set_footer(text="Made with ♥️ by yigit-guven • Use /help to explore my commands!")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(about)
    print("About command loaded")