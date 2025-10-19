import discord
from discord import app_commands
from typing import Literal
from utils import is_admin, get_data_category

@app_commands.command(
    name="setupregistration",
    description="Setup the registration system for your server."
)
@app_commands.describe(
    registration_channel="Channel where users will register.",
    management_channel="Channel for registration management.",
    mode="Choose the registration mode: Manual or Automatic."
)
@app_commands.guild_only()
async def setupregistration(
    interaction: discord.Interaction,
    registration_channel: discord.TextChannel,
    management_channel: discord.TextChannel,
    mode: Literal["Manual", "Automatic"]
):
    # Check for admin permission
    if not await is_admin(interaction):
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    guild = interaction.guild

    # Get or create the "Amethis' Data" category using your utils.py
    category = await get_data_category(guild)

    # Look for or create "registration-data" channel inside the category
    channel_name = "registration-data"
    reg_data_channel = discord.utils.get(category.text_channels, name=channel_name)

    if not reg_data_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        reg_data_channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason="For storing registration system configuration"
        )

    # Create embed with setup info
    embed = discord.Embed(
        title="<:scroll:1427519497207812168> REGISTRATION SYSTEM",
        color=discord.Color.purple()
    )
    embed.add_field(name="Registration Channel", value=registration_channel.mention, inline=False)
    embed.add_field(name="Management Channel", value=management_channel.mention, inline=False)
    embed.add_field(name="Mode", value=mode, inline=False)
    embed.add_field(name="Manager Role(s)", value="(Empty for now)", inline=False)
    embed.set_footer(
        text=f"Made by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    # Send embed into registration-data channel
    await reg_data_channel.send(embed=embed)

    # Respond to admin who ran the command
    await interaction.response.send_message(
        f"✅ Registration system setup complete!\nConfiguration saved in {reg_data_channel.mention}",
        ephemeral=True
    )

def setup(bot):
    bot.tree.add_command(setupregistration)
    print("SetupRegistration command loaded")