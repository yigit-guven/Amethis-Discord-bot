import discord
from discord import app_commands
from discord.ui import Select, View
from utils import is_admin

class HelpSelect(Select):
    def __init__(self, is_user_admin: bool = False):
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
        if is_user_admin:
            options.append(
                discord.SelectOption(
                    label="Administration",
                    description="Server administration commands",
                    emoji="<:shield:1427515556113809479>",
                    value="administration"
                )
            )
        
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
                name="/about",
                value="Learn more about Amethis and her features",
                inline=False
            )
            embed.add_field(
                name="/ping",
                value="Check bot's latency and connection status",
                inline=False
            )
            embed.add_field(
                name="/invite",
                value="Invite Amethis to your server",
                inline=False
            )
            embed.add_field(
                name="/poll",
                value="Create customizable polls with advanced options",
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
            embed.add_field(
                name="/source",
                value="View the bot's source code on GitHub",
                inline=False
            )
        
        elif category == "administration":
            embed = discord.Embed(
                title="<:shield:1427515556113809479> Administration Commands",
                description="**Server administration commands:**",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="/adminroles",
                value="View all admin roles for Amethis",
                inline=False
            )
            embed.add_field(
                name="/addadminrole",
                value="Add a role as admin for Amethis",
                inline=False
            )
            embed.add_field(
                name="/removeadminrole",
                value="Remove a role from Amethis admin roles",
                inline=False
            )
            embed.add_field(
                name="<:pin:1427805351083905127> Note",
                value="These commands are only available for server administrators and custom admin roles.",
                inline=False
            )
        
        embed.set_footer(text="Select another category to explore more commands")
        
        await interaction.response.edit_message(embed=embed, view=HelpView(is_user_admin=await is_admin(interaction)))

class HelpView(View):
    def __init__(self, is_user_admin: bool = False):
        super().__init__()
        self.add_item(HelpSelect(is_user_admin=is_user_admin))

@app_commands.command(name="help", description="Get help with bot commands")
async def help(interaction: discord.Interaction):
    is_user_admin = await is_admin(interaction)
    
    embed = discord.Embed(
        title="<:question:1427511257275301959> Amethis Help Center <:question:1427511257275301959>",
        description="**Welcome to the help menu!**\n\nPlease select a category from the dropdown below to explore available commands.",
        color=discord.Color.purple()
    )
    
    categories_text = "• **General Commands** - Core bot functionality\n• **Legal Information** - Policies and terms"
    if is_user_admin:
        categories_text += "\n• **Administration** - Server administration commands"
    
    embed.add_field(
        name="<:hashtag:1427516016354660414> Categories",
        value=categories_text,
        inline=False
    )
    
    embed.set_footer(text="Choose a category to get started")
    
    await interaction.response.send_message(embed=embed, view=HelpView(is_user_admin=is_user_admin), ephemeral=True)

def setup(bot):
    bot.tree.add_command(help)
    print("Help command loaded")