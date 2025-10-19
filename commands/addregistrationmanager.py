import discord
from discord import app_commands
from utils import is_admin, get_data_category
from typing import Optional

POSSIBLE_TITLES = {
    "REGISTRATION SYSTEM",
    "📋 REGISTRATION SYSTEM",
    "<:scroll:1427519497207812168> REGISTRATION SYSTEM",
    "<:scroll:1427519497207812168> REGISTRATION SYSTEM".upper()
}


async def _find_registration_message(guild: discord.Guild) -> Optional[discord.Message]:
    """Return the registration-data embed message or None."""
    category = await get_data_category(guild)

    # Find the registration-data channel in the category
    reg_channel = None
    for ch in category.text_channels:
        if ch.name == "registration-data":
            reg_channel = ch
            break
    if not reg_channel:
        return None

    # Search recent history (increase limit for reliability)
    async for msg in reg_channel.history(limit=500):
        if not msg.embeds:
            continue
        embed = msg.embeds[0]
        title = (embed.title or "").strip()
        if title in POSSIBLE_TITLES or title.upper() in POSSIBLE_TITLES:
            return msg
    return None


@app_commands.command(
    name="addregistrationmanager",
    description="Add a manager role to the registration system."
)
@app_commands.describe(role="The role to add as registration manager")
@app_commands.guild_only()
async def addregistrationmanager(interaction: discord.Interaction, role: discord.Role):
    if not await is_admin(interaction):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    guild = interaction.guild

    reg_msg = await _find_registration_message(guild)
    if reg_msg is None:
        await interaction.response.send_message(
            "⚠️ Could not find the `registration-data` message. Make sure /setupregistration was run and the registration-data channel exists.",
            ephemeral=True
        )
        return

    embed = reg_msg.embeds[0]
    new_embed = discord.Embed.from_dict(embed.to_dict())

    # Find Manager Role(s) field (case-insensitive startswith)
    found = False
    for i, field in enumerate(new_embed.fields):
        if field.name.lower().startswith("manager role"):
            found = True
            current_value = (field.value or "").strip()
            if current_value == "" or "(Empty" in current_value:
                updated_value = role.mention
            else:
                # Prevent duplicates
                # Compare mentions to avoid role ID parsing
                lines = [line.strip() for line in current_value.splitlines() if line.strip()]
                if role.mention in lines:
                    await interaction.response.send_message(f"ℹ️ {role.mention} is already listed.", ephemeral=True)
                    return
                lines.append(role.mention)
                updated_value = "\n".join(lines)

            new_embed.set_field_at(i, name=field.name, value=updated_value, inline=field.inline)
            break

    # If field not found, append it
    if not found:
        new_embed.add_field(name="Manager Role(s)", value=role.mention, inline=False)

    await reg_msg.edit(embed=new_embed)
    await interaction.response.send_message(f"✅ Added {role.mention} to Manager Role(s).", ephemeral=True)


def setup(bot):
    bot.tree.add_command(addregistrationmanager)
    print("AddRegistrationManager command loaded")