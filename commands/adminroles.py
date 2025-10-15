import discord
from discord import app_commands
from utils import is_admin, get_admin_roles

@app_commands.command(name="adminroles", description="View all admin roles for Amethis")
@app_commands.guild_only()
async def adminroles(interaction: discord.Interaction):
    if not await is_admin(interaction):
        embed = discord.Embed(
            title="<:cross:1427515205654544486> Access Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    admin_role_ids = await get_admin_roles(interaction.guild)
    
    embed = discord.Embed(
        title="<:shield:1427515556113809479> Admin Roles",
        description="**Current administrator roles for Amethis:**",
        color=discord.Color.purple()
    )
    
    if admin_role_ids:
        role_mentions = [f"<@&{role_id}>" for role_id in admin_role_ids]
        role_list = "\n".join(role_mentions)
        embed.add_field(name="Roles with Admin Access", value=role_list, inline=False)
    else:
        embed.add_field(
            name="No Admin Roles Set", 
            value="Use `/addadminrole` to add administrator roles.", 
            inline=False
        )
    
    embed.add_field(
        name="<:pin:1427805351083905127> Note", 
        value="Users with these roles can use admin commands even without the Administrator permission.", 
        inline=False
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(adminroles)