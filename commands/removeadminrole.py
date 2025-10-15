import discord
from discord import app_commands
from utils import is_admin, get_admin_roles, save_admin_roles

@app_commands.command(name="removeadminrole", description="Remove a role from Amethis admin roles")
@app_commands.guild_only()
@app_commands.describe(role="The role to remove from administrator")
async def removeadminrole(interaction: discord.Interaction, role: discord.Role):
    if not await is_admin(interaction):
        embed = discord.Embed(
            title="<:cross:1427515205654544486> Access Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    admin_role_ids = await get_admin_roles(interaction.guild)
    
    if role.id not in admin_role_ids:
        embed = discord.Embed(
            title="<:exclamation:1427511606387937360> Role Not Found",
            description=f"{role.mention} is not an administrator role.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    admin_role_ids.remove(role.id)
    await save_admin_roles(interaction.guild, admin_role_ids)
    
    embed = discord.Embed(
        title="<:tick:1427514481650565251> Role Removed",
        description=f"Successfully removed {role.mention} from administrator roles.",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="What this means:",
        value=f"Users with {role.mention} can no longer use Amethis admin commands.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(removeadminrole)