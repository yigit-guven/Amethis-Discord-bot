import re
import discord
from discord import app_commands
from utils import is_admin, get_data_category
from typing import Optional, List

POSSIBLE_TITLES = {
    "REGISTRATION SYSTEM",
    "📋 REGISTRATION SYSTEM",
    "<:scroll:1427519497207812168> REGISTRATION SYSTEM",
}

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
    if not value:
        return []
    blocks = [b.strip() for b in value.split("\n\n") if b.strip()]
    questions = []
    q_re = re.compile(r"^Q\s*(\d+)\s*:\s*(.*)$", re.IGNORECASE)
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        m = q_re.match(lines[0])
        if not m:
            continue
        number = int(m.group(1))
        question_text = m.group(2).strip()
        typ = None
        action = None
        options = []
        for ln in lines[1:]:
            if ln.lower().startswith("• type:"):
                typ = ln.split(":",1)[1].strip()
            elif ln.lower().startswith("• action:"):
                action = ln.split(":",1)[1].strip()
            elif ln.lower().startswith("• options:"):
                opts_raw = ln.split(":",1)[1].strip()
                for optpair in re.split(r'\s*;\s*|\s*,\s*', opts_raw):
                    if "->" in optpair:
                        left, right = optpair.split("->",1)
                        options.append((left.strip(), right.strip()))
        questions.append({
            "number": number,
            "question": question_text,
            "type": typ or "Text",
            "action": action or "",
            "options": options
        })
    # sort by number
    questions.sort(key=lambda x: x["number"])
    return questions

def _format_questions_field_from_parsed(parsed: List[dict]) -> str:
    blocks = []
    for idx, q in enumerate(parsed, start=1):
        lines = []
        lines.append(f"Q{idx}: {q['question']}")
        lines.append(f"• Type: {q['type']}")
        lines.append(f"• Action: {q['action']}")
        if q['type'].lower().startswith("option") and q.get("options"):
            opts = ", ".join(f"{opt} -> {role}" for opt, role in q["options"])
            lines.append(f"• Options: {opts}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) if blocks else "(No questions set)"

@app_commands.command(
    name="removeregistrationquestion",
    description="Remove a registration question by its number."
)
@app_commands.describe(number="Question number to remove (e.g. 1)")
@app_commands.guild_only()
async def removeregistrationquestion(interaction: discord.Interaction, number: int):
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

    embed = reg_msg.embeds[0]
    # find questions field
    questions_field_value = ""
    for f in embed.fields:
        if f.name.lower().startswith("questions"):
            questions_field_value = f.value or ""
            break

    parsed = _parse_questions_field(questions_field_value)
    if not parsed:
        await interaction.response.send_message("ℹ️ There are currently no questions to remove.", ephemeral=True)
        return

    if number < 1 or number > len(parsed):
        await interaction.response.send_message(f"❌ Invalid question number. There are currently {len(parsed)} questions.", ephemeral=True)
        return

    # remove and reindex
    parsed.pop(number - 1)

    new_value = _format_questions_field_from_parsed(parsed)
    new_embed = discord.Embed.from_dict(embed.to_dict())

    replaced = False
    for i, field in enumerate(new_embed.fields):
        if field.name.lower().startswith("questions"):
            new_embed.set_field_at(i, name=field.name, value=new_value, inline=field.inline)
            replaced = True
            break
    if not replaced:
        new_embed.add_field(name="Questions", value=new_value, inline=False)

    await reg_msg.edit(embed=new_embed)
    await interaction.response.send_message(f"✅ Removed question #{number} and reindexed remaining questions.", ephemeral=True)

def setup(bot):
    bot.tree.add_command(removeregistrationquestion)
    print("RemoveRegistrationQuestion command loaded")