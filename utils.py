import discord
from discord import app_commands

async def is_admin(interaction: discord.Interaction) -> bool:
    """Check if user has administrator permissions or is in admin roles"""
    # If this is a DM context, always return True
    if interaction.guild is None:
        return True
    
    # Check if user is a Member (should always be true in guild context, but safe check)
    if not isinstance(interaction.user, discord.Member):
        return False
    
    # Check if user has administrator permissions
    if interaction.user.guild_permissions.administrator:
        return True
    
    # Check if user has any admin roles
    admin_roles = await get_admin_roles(interaction.guild)
    user_roles = [role.id for role in interaction.user.roles]
    
    return any(role_id in user_roles for role_id in admin_roles)

async def get_data_category(guild: discord.Guild) -> discord.CategoryChannel:
    """Get or create the Amethis data category"""
    category_name = "Amethis' Data"
    
    for category in guild.categories:
        if category.name == category_name:
            return category
    
    category = await guild.create_category_channel(
        name=category_name,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }
    )
    return category

async def get_admin_roles_channel(guild: discord.Guild) -> discord.TextChannel:
    """Get or create the admin-roles data channel"""
    category = await get_data_category(guild)
    channel_name = "admin-roles"
    
    # Look for existing channel
    for channel in category.channels:
        if channel.name == channel_name:
            return channel
    
    # Create new channel if not found
    channel = await category.create_text_channel(
        name=channel_name,
        overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, read_messages=True, send_messages=True)
        }
    )
    return channel

async def get_admin_roles(guild: discord.Guild) -> list:
    """Get admin roles from data channel"""
    channel = await get_admin_roles_channel(guild)
    
    admin_roles = []
    async for message in channel.history(limit=10):
        if message.content.startswith("ADMIN_ROLE:"):
            try:
                role_id = int(message.content.split(":")[1].strip())
                admin_roles.append(role_id)
            except (ValueError, IndexError):
                continue
    
    return admin_roles

async def save_admin_roles(guild: discord.Guild, admin_roles: list):
    """Save admin roles to data channel"""
    channel = await get_admin_roles_channel(guild)
    
    async for message in channel.history(limit=50):
        if message.content.startswith("ADMIN_ROLE:"):
            await message.delete()
    
    for role_id in admin_roles:
        await channel.send(f"ADMIN_ROLE:{role_id}")
    
    display_message = await get_or_create_display_message(channel)
    role_mentions = [f"<@&{role_id}>" for role_id in admin_roles]
    role_list = "\n".join(role_mentions) if role_mentions else "No admin roles set"
    
    embed = discord.Embed(
        title="<:shield:1427515556113809479> Amethis Admin Roles",
        description="**Administrator roles for this server:**",
        color=discord.Color.purple()
    )
    embed.add_field(name="Admin Roles", value=role_list, inline=False)
    embed.set_footer(text="Use /addadminrole to add more roles")
    
    await display_message.edit(embed=embed)

async def get_or_create_display_message(channel: discord.TextChannel) -> discord.Message:
    """Get or create the display message in the admin roles channel"""
    async for message in channel.history(limit=10):
        if message.embeds and message.embeds[0].title == "<:shield:1427515556113809479> Amethis Admin Roles":
            return message
    embed = discord.Embed(
        title="<:shield:1427515556113809479> Amethis Admin Roles",
        description="**Administrator roles for this server:**",
        color=discord.Color.purple()
    )
    embed.add_field(name="Admin Roles", value="No admin roles set", inline=False)
    embed.set_footer(text="Use /addadminrole to add more roles")
    
    return await channel.send(embed=embed)