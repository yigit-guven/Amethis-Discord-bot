import re
import discord
from discord import app_commands
from discord.ui import View
from utils import get_data_category

# Helper to find registration embed message
async def _find_registration_message(guild: discord.Guild) -> discord.Message | None:
    category = await get_data_category(guild)
    reg_channel = discord.utils.get(category.text_channels, name="registration-data")
    if not reg_channel:
        return None

    async for msg in reg_channel.history(limit=500):
        if not msg.embeds:
            continue
        title = (msg.embeds[0].title or "").strip()
        if "REGISTRATION SYSTEM" in title.upper():
            return msg
    return None

def _parse_questions_field(value: str) -> list:
    if not value:
        return []
    blocks = [b.strip() for b in value.split("\n\n") if b.strip()]
    questions = []
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
                opts_raw = ln.split(":",1)[1].strip()
                for optpair in re.split(r'\s*;\s*|\s*,\s*', opts_raw):
                    if "->" in optpair:
                        left, right = optpair.split("->",1)
                        options.append((left.strip(), right.strip()))
        questions.append({
            "question": question_text,
            "type": typ or "Text",
            "action": action or "",
            "options": options
        })
    return questions

class AcceptDenyView(View):
    def __init__(self, user: discord.Member, answers: dict, questions: list, mode: str, thread: discord.Thread | None):
        super().__init__(timeout=None)
        self.user = user
        self.answers = answers
        self.questions = questions
        self.mode = mode
        self.thread = thread

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        for q, ans in zip(self.questions, self.answers.values()):
            if q['type'].lower() == "text" and q['action'] == "Nick Changer":
                try:
                    await self.user.edit(nick=ans)
                except discord.Forbidden:
                    await self.user.send("⚠️ Cannot change your nickname (owner or permission issue).")
            elif q['type'].lower() == "option" and q['action'] == "Role Adder":
                for opt_text, role_repr in q['options']:
                    if opt_text.lower() == ans.lower():
                        m = re.match(r"<@&(\d+)>", role_repr)
                        if m:
                            role_id = int(m.group(1))
                            role = interaction.guild.get_role(role_id)
                            if role:
                                await self.user.add_roles(role)
        await interaction.message.edit(content=f"✅ Registration accepted by {interaction.user.mention}", view=None)
        try:
            await self.user.send(f"✅ Your registration for **{interaction.guild.name}** has been accepted! You are now registered.")
        except:
            pass
        # Delete the thread if it exists
        if self.thread:
            try: await self.thread.delete()
            except: pass

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(content=f"❌ Registration denied by {interaction.user.mention}\nThis message will be deleted in 30 seconds.", view=None)
        try:
            await self.user.send(f"❌ Your registration for **{interaction.guild.name}** has been denied by the Administration. You may try again.")
        except:
            pass
        # Schedule deletion of the denied message after 30 seconds
        await interaction.message.delete(delay=30)
        # Delete the thread if it exists
        if self.thread:
            try: await self.thread.delete()
            except: pass

@app_commands.command(name="register", description="Register yourself via the Registration System")
@app_commands.choices(mode=[
    app_commands.Choice(name="Via Direct Message", value="dm"),
    app_commands.Choice(name="Via Text Channel", value="channel")
])
@app_commands.guild_only()
async def register(interaction: discord.Interaction, mode: app_commands.Choice[str]):
    guild = interaction.guild
    reg_msg = await _find_registration_message(guild)
    if not reg_msg:
        await interaction.response.send_message(
            "⚠️ Registration system not set up yet. Please contact admins.",
            ephemeral=True
        )
        return

    embed = reg_msg.embeds[0]
    reg_channel_mention = None
    man_channel_mention = None
    reg_mode = None
    questions_field = None
    for f in embed.fields:
        if f.name.lower().startswith("registration channel"):
            reg_channel_mention = f.value.strip()
        elif f.name.lower().startswith("management channel"):
            man_channel_mention = f.value.strip()
        elif f.name.lower().startswith("mode"):
            reg_mode = f.value.strip()
        elif f.name.lower().startswith("questions"):
            questions_field = f.value

    # Extract IDs
    try:
        reg_channel_id = int(re.match(r"<#(\d+)>", reg_channel_mention).group(1))
        man_channel_id = int(re.match(r"<#(\d+)>", man_channel_mention).group(1))
    except:
        await interaction.response.send_message(
            "⚠️ Registration or Management channel in embed is invalid. Contact admins.",
            ephemeral=True
        )
        return

    if interaction.channel.id != reg_channel_id and mode.value != "dm":
        await interaction.response.send_message(
            f"❌ You can only use this command in the registration channel: {reg_channel_mention}",
            ephemeral=True
        )
        return

    questions = _parse_questions_field(questions_field)
    if not questions:
        await interaction.response.send_message("ℹ️ No questions set up yet. Contact server admins.", ephemeral=True)
        return

    # Determine target channel / thread
    if mode.value == "dm":
        try:
            target_channel = await interaction.user.create_dm()
        except:
            await interaction.response.send_message(
                "❌ I cannot send you DMs. Please use /register Via Text Channel.",
                ephemeral=True
            )
            return
    else:
        # Create a private thread in registration channel
        reg_channel = guild.get_channel(reg_channel_id)
        thread = await reg_channel.create_thread(
            name=f"registration-{interaction.user.name}",
            type=discord.ChannelType.private_thread,
            auto_archive_duration=60,
            invitable=False
        )
        target_channel = thread
        # Auto-tag the user at the start
        await thread.send(f"{interaction.user.mention}, your registration thread has been created. Please answer the questions below.")
    
    await interaction.response.send_message(
        "✅ Starting registration... Use 'back' to go to previous question if needed.",
        ephemeral=True
    )

    answers = {}
    current_index = 0

    while current_index < len(questions):
        q = questions[current_index]
        content_lines = [f"**Question {current_index+1}/{len(questions)}**: {q['question']}"]
        if q['type'].lower() == "option" and q['options']:
            options_text = "\n".join(f"- {opt}" for opt,_ in q['options'])
            content_lines.append(f"Options:\n{options_text}")
        content_lines.append("\nType your answer below. To go back, type `back`.")

        msg_question = await target_channel.send("\n".join(content_lines))

        try:
            msg = await interaction.client.wait_for(
                "message",
                check=lambda m: m.author.id == interaction.user.id and m.channel == target_channel,
                timeout=300
            )
        except:
            await target_channel.send("⏱️ Registration timed out. Please run /register again.", delete_after=30)
            if mode.value == "channel":
                try: await target_channel.delete()
                except: pass
            return

        # Delete user answer & question to keep thread clean
        try: await msg.delete()
        except: pass
        try: await msg_question.delete()
        except: pass

        if msg.content.lower() == "back":
            if current_index > 0:
                current_index -= 1
            else:
                await target_channel.send("⚠️ Already at the first question.", delete_after=10)
            continue

        # Validate option input
        if q['type'].lower() == "option" and q['options']:
            valid_options = [opt.lower() for opt,_ in q['options']]
            if msg.content.strip().lower() not in valid_options:
                await target_channel.send(
                    f"❌ Invalid option. Choose one of:\n" + "\n".join(valid_options),
                    delete_after=10
                )
                continue

        answers[current_index] = msg.content.strip()
        current_index += 1

    # Apply registration
    if reg_mode.lower() == "automatic":
        for idx, q in enumerate(questions):
            ans = answers.get(idx)
            if q['type'].lower() == "text" and q['action'] == "Nick Changer":
                try:
                    await interaction.user.edit(nick=ans)
                except discord.Forbidden:
                    await interaction.user.send("⚠️ Cannot change your nickname (owner or permission issue).")
            elif q['type'].lower() == "option" and q['action'] == "Role Adder":
                for opt_text, role_repr in q['options']:
                    if opt_text.lower() == ans.lower():
                        m = re.match(r"<@&(\d+)>", role_repr)
                        if m:
                            role_id = int(m.group(1))
                            role = guild.get_role(role_id)
                            if role:
                                await interaction.user.add_roles(role)
        await target_channel.send(f"✅ You are now registered for **{guild.name}**! Welcome aboard.")
    else:  # Manual mode
        man_channel = guild.get_channel(man_channel_id)
        if not man_channel:
            await target_channel.send("⚠️ Management channel not found. Contact admins.", delete_after=30)
            if mode.value == "channel":
                try: await target_channel.delete()
                except: pass
            return

        desc_lines = []
        for idx, q in enumerate(questions):
            desc_lines.append(f"**Q{idx+1}: {q['question']}**\n> {answers[idx]}")
        man_embed = discord.Embed(
            title=f"Registration Request: {interaction.user}",
            description="\n".join(desc_lines),
            color=discord.Color.purple()
        )
        man_embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        man_embed.set_footer(text=f"User ID: {interaction.user.id} | Accept or Deny below")

        view = AcceptDenyView(user=interaction.user, answers=answers, questions=questions, mode=reg_mode, thread=(target_channel if mode.value == "channel" else None))
        await man_channel.send(embed=man_embed, view=view)

def setup(bot):
    bot.tree.add_command(register)
    print("Register command loaded")