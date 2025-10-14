import discord
from discord import app_commands
from discord.ui import Select, View

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Commands",
                description="View all general bot commands",
                emoji="<:scroll:1427519497207812168>",
                value="general"
            ),
            discord.SelectOption(
                label="Legal Information",
                description="Privacy, Terms, and License",
                emoji="<:legal:1427781041216557127>",
                value="legal"
            )
        ]
        super().__init__(placeholder="Choose a category...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        
        if category == "general":
            embed = discord.Embed(
                title="<:scroll:1427519497207812168> General Commands",
                description="**All available general commands:**",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="/help",
                value="Shows this help menu",
                inline=False
            )
            embed.add_field(
                name="More Commands",
                value="Additional commands will appear here as they're added",
                inline=False
            )
            
        elif category == "legal":
            embed = discord.Embed(
                title="<:legal:1427781041216557127> Legal Information",
                description="**Important legal documents and policies:**",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="/privacy",
                value="View our privacy policy and data handling",
                inline=False
            )
            embed.add_field(
                name="/terms", 
                value="Read our terms of service",
                inline=False
            )
            embed.add_field(
                name="/license",
                value="View the bot's license information",
                inline=False
            )
        
        embed.set_footer(text="Select another category to explore more commands")
        
        await interaction.response.edit_message(embed=embed, view=HelpView())

class HelpView(View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpSelect())

@app_commands.command(name="help", description="Get help with bot commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:question:1427511257275301959> Amethis Help Center <:question:1427511257275301959>",
        description="**Welcome to the help menu!**\n\nPlease select a category from the dropdown below to explore available commands.",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="<:hashtag:1427516016354660414> Categories",
        value="• **General Commands** - Core bot functionality\n• **Legal Information** - Policies and terms",
        inline=False
    )
    
    embed.set_footer(text="Choose a category to get started")
    
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

def setup(bot):
    bot.tree.add_command(help)
    print("Help command loaded")