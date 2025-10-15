import discord
from discord import app_commands
from utils import is_admin, get_admin_roles, save_admin_roles

@app_commands.command(name="addadminrole", description="Add a role as admin for Amethis")
@app_commands.guild_only()
@app_commands.describe(role="The role to add as Amethis administrator")
async def addadminrole(interaction: discord.Interaction, role: discord.Role):
    if not await is_admin(interaction):
        embed = discord.Embed(
            title="<:cross:1427515205654544486> Access Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    admin_role_ids = await get_admin_roles(interaction.guild)
    
    if role.id in admin_role_ids:
        embed = discord.Embed(
            title="<:circle:1427512638769725542> Role Already Admin",
            description=f"{role.mention} is already an administrator role.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    admin_role_ids.append(role.id)
    await save_admin_roles(interaction.guild, admin_role_ids)
    
    embed = discord.Embed(
        title="<:tick:1427514481650565251> Role Added",
        description=f"Successfully added {role.mention} as an administrator role.",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="What this means:",
        value=f"Users with {role.mention} can now use Amethis admin commands.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(addadminrole)