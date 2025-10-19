import re
import discord
from discord import app_commands
from utils import is_admin, get_data_category
from typing import Optional, List, Tuple

POSSIBLE_TITLES = {
    "REGISTRATION SYSTEM",
    "📋 REGISTRATION SYSTEM",
    "<:scroll:1427519497207812168> REGISTRATION SYSTEM",
}

# helper to find registration embed message
async def _find_registration_message(guild: discord.Guild) -> Optional[discord.Message]:
    category = await get_data_category(guild)
    reg_channel = discord.utils.get(category.text_channels, name="registration-data")
    if not reg_channel:
        return None

    async for msg in reg_channel.history(limit=500):
        if not msg.embeds:
            continue
        title = (msg.embeds[0].title or "").strip()
        if title in POSSIBLE_TITLES or title.upper() in POSSIBLE_TITLES:
            return msg
    return None

def _parse_questions_field(value: str) -> List[dict]:
    """Parse current Questions field into list of dicts.
       Each dict: {question: str, type: "Text"|"Option", action: "Nick Changer"|"Role Adder", options: [(opt_text, role_id_or_mention), ...] }
    """
    if not value:
        return []
    blocks = [b.strip() for b in value.split("\n\n") if b.strip()]
    result = []
    q_re = re.compile(r"^Q\s*\d+\s*:\s*(.*)$", re.IGNORECASE)
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        m = q_re.match(lines[0])
        if not m:
            continue
        question_text = m.group(1).strip()
        typ = None
        action = None
        options = []
        for ln in lines[1:]:
            if ln.lower().startswith("• type:"):
                typ = ln.split(":",1)[1].strip()
            elif ln.lower().startswith("• action:"):
                action = ln.split(":",1)[1].strip()
            elif ln.lower().startswith("• options:"):
                # options line - the rest will be split by commas previously in the stored format;
                opts_raw = ln.split(":",1)[1].strip()
                # if stored as "Opt -> Role; Opt2 -> Role2" split by ';' or ' , '
                for optpair in re.split(r"\s*;\s*|\s*,\s*", opts_raw):
                    if "->" in optpair:
                        left, right = optpair.split("->",1)
                        options.append((left.strip(), right.strip()))
        result.append({
            "question": question_text,
            "type": typ or "Text",
            "action": action or "",
            "options": options
        })
    return result

def _format_questions_field(questions: List[dict]) -> str:
    """Format questions list into embed field value using the requested style."""
    blocks = []
    for idx, q in enumerate(questions, start=1):
        lines = []
        lines.append(f"Q{idx}: {q['question']}")
        lines.append(f"• Type: {q['type']}")
        lines.append(f"• Action: {q['action']}")
        if q['type'].lower().startswith("option") and q.get("options"):
            # Format options as "• Options: Opt -> @Role, Opt2 -> @Role2"
            opts = ", ".join(f"{opt} -> {role}" for opt, role in q["options"])
            lines.append(f"• Options: {opts}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) if blocks else "(No questions set)"

def _extract_role_from_text(guild: discord.Guild, role_text: str) -> Optional[discord.Role]:
    """Try to parse a role mention or role name and return discord.Role or None."""
    role_text = role_text.strip()
    # role mention pattern: <@&id>
    m = re.match(r"<@&(\d+)>", role_text)
    if m:
        rid = int(m.group(1))
        return guild.get_role(rid)
    # try numeric id
    if role_text.isdigit():
        return guild.get_role(int(role_text))
    # try by name (case-sensitive)
    role = discord.utils.get(guild.roles, name=role_text)
    if role:
        return role
    # try case-insensitive match
    for r in guild.roles:
        if r.name.lower() == role_text.lower():
            return r
    return None

@app_commands.command(
    name="addregistrationquestion",
    description="Add a registration question to the registration system."
)
@app_commands.guild_only()
async def addregistrationquestion(interaction: discord.Interaction):
    # admin check
    if not await is_admin(interaction):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    guild = interaction.guild
    reg_msg = await _find_registration_message(guild)
    if reg_msg is None:
        await interaction.response.send_message(
            "⚠️ Could not find the registration embed in `registration-data`. Run /setupregistration first.",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Please enter the question text (single message):", ephemeral=True)
    try:
        q_msg = await interaction.client.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id and m.channel.type == discord.ChannelType.private or (m.author.id == interaction.user.id and m.channel == interaction.channel),
            timeout=120
        )
    except Exception:
        await interaction.followup.send("⏱️ Timed out waiting for question text. Please run the command again.", ephemeral=True)
        return

    question_text = q_msg.content.strip()
    if not question_text:
        await interaction.followup.send("❌ Empty question. Aborting.", ephemeral=True)
        return

    # Ask for question mode
    await interaction.followup.send(
        "Choose question mode by typing `1` or `2`:\n`1` - Open Text\n`2` - With Options",
        ephemeral=True
    )
    try:
        mode_msg = await interaction.client.wait_for(
            "message",
            check=lambda m: m.author.id == interaction.user.id and (m.channel.type == discord.ChannelType.private or m.channel == interaction.channel),
            timeout=60
        )
    except Exception:
        await interaction.followup.send("⏱️ Timed out waiting for mode selection. Please run the command again.", ephemeral=True)
        return

    mode_choice = mode_msg.content.strip()
    if mode_choice not in ("1", "2"):
        await interaction.followup.send("❌ Invalid choice. Please run the command again and enter `1` or `2`.", ephemeral=True)
        return

    # Load existing questions
    embed = reg_msg.embeds[0]
    questions_field_value = ""
    for f in embed.fields:
        if f.name.lower().startswith("questions"):
            questions_field_value = f.value or ""
            break
    questions = _parse_questions_field(questions_field_value)

    if mode_choice == "1":
        # Open text
        await interaction.followup.send("Is this question a user nickname value? Type `yes` or `no`:", ephemeral=True)
        try:
            nick_msg = await interaction.client.wait_for(
                "message",
                check=lambda m: m.author.id == interaction.user.id and (m.channel.type == discord.ChannelType.private or m.channel == interaction.channel),
                timeout=60
            )
        except Exception:
            await interaction.followup.send("⏱️ Timed out waiting for nickname choice. Please run the command again.", ephemeral=True)
            return

        nick_choice = nick_msg.content.strip().lower()
        if nick_choice in ("yes", "y", "true"):
            action = "Nick Changer"
        else:
            action = "None"

        new_q = {
            "question": question_text,
            "type": "Text",
            "action": action,
            "options": []
        }
        questions.append(new_q)

    else:
        # With Options - one-shot input
        await interaction.followup.send(
            "Provide options in ONE message using this format:\n"
            "`Option1 : @Role1 , Option2 : @Role2 , Option3 : @Role3`\n\n"
            "Rules:\n- Separate pairs with commas. \n- Use role mention (`@Role`) or role name.\n- Option text may contain spaces and punctuation.\n\n"
            "Example:\n`Red : @RedRole , Blue : 123456789012345678 , Green : GreenRole`",
            ephemeral=True
        )
        try:
            opts_msg = await interaction.client.wait_for(
                "message",
                check=lambda m: m.author.id == interaction.user.id and (m.channel.type == discord.ChannelType.private or m.channel == interaction.channel),
                timeout=180
            )
        except Exception:
            await interaction.followup.send("⏱️ Timed out waiting for options. Please run the command again.", ephemeral=True)
            return

        raw = opts_msg.content.strip()
        if not raw:
            await interaction.followup.send("❌ Empty options. Aborting.", ephemeral=True)
            return

        # parse pairs split by commas (but ignore commas inside quotes? we keep it simple)
        pairs = [p.strip() for p in re.split(r'\s*,\s*', raw) if p.strip()]
        parsed_options: List[Tuple[str, str]] = []
        failed_pairs = []
        for pair in pairs:
            if ":" not in pair:
                failed_pairs.append(pair)
                continue
            left, right = pair.split(":", 1)
            opt_text = left.strip()
            role_text = right.strip()
            role_obj = _extract_role_from_text(guild, role_text)
            role_repr = role_text
            if role_obj:
                role_repr = f"<@&{role_obj.id}>"
            else:
                # keep the raw text if role not resolved; still allow it
                role_repr = role_text
            parsed_options.append((opt_text, role_repr))

        if failed_pairs:
            await interaction.followup.send(f"❌ Could not parse pairs: {failed_pairs}. Aborting. Use format `Option : @Role, ...`", ephemeral=True)
            return

        # With options, action is Role Adder
        new_q = {
            "question": question_text,
            "type": "Option",
            "action": "Role Adder",
            "options": parsed_options
        }
        questions.append(new_q)

    # Format and update embed
    new_embed = discord.Embed.from_dict(embed.to_dict())
    new_value = _format_questions_field(questions)

    # replace or add Questions field
    replaced = False
    for i, field in enumerate(new_embed.fields):
        if field.name.lower().startswith("questions"):
            new_embed.set_field_at(i, name=field.name, value=new_value, inline=field.inline)
            replaced = True
            break
    if not replaced:
        new_embed.add_field(name="Questions", value=new_value, inline=False)

    await reg_msg.edit(embed=new_embed)
    await interaction.followup.send("✅ Question added to the registration embed.", ephemeral=True)

def setup(bot):
    bot.tree.add_command(addregistrationquestion)
    print("AddRegistrationQuestion command loaded")