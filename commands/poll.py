import discord
from discord import app_commands
from discord.ui import Button, View
import asyncio
from typing import Optional
from datetime import datetime, timedelta

class SimplePollView(View):
    def __init__(self, question: str, options: list, duration_minutes: int, creator: discord.User):
        super().__init__(timeout=None)  # Persistent view, we'll handle timeout manually
        self.question = question
        self.options = options
        self.votes = [0] * len(options)
        self.voters = set()  # Track who voted to prevent multiple votes
        self.duration_minutes = duration_minutes
        self.end_time = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.creator = creator
        self.message = None
        
        # Create buttons for each option
        for i, option in enumerate(options):
            button = Button(
                label=f"{i+1}. {option}",
                style=discord.ButtonStyle.primary,
                custom_id=f"poll_{i}_{datetime.utcnow().timestamp()}"  # Unique ID to avoid conflicts
            )
            button.callback = self.create_callback(i, option)
            self.add_item(button)
    
    def create_callback(self, index: int, option: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.voters:
                await interaction.response.send_message("You've already voted in this poll!", ephemeral=True)
                return
            
            # Record vote
            self.votes[index] += 1
            self.voters.add(interaction.user.id)
            
            # Update embed with new results
            embed = self.create_results_embed()
            await interaction.response.edit_message(embed=embed)
            
            await interaction.followup.send(f"✅ You voted for: **{option}**", ephemeral=True)
        
        return callback
    
    def create_results_embed(self):
        total_votes = sum(self.votes)
        
        embed = discord.Embed(
            title=f"📊 {self.question}",
            color=discord.Color.purple()  # Purple color as requested
        )
        
        for i, (option, votes) in enumerate(zip(self.options, self.votes)):
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = self.create_progress_bar(percentage)
            
            embed.add_field(
                name=f"{i+1}. {option}",
                value=f"{bar} {votes} votes ({percentage:.1f}%)",
                inline=False
            )
        
        # Calculate remaining time
        remaining = self.end_time - datetime.utcnow()
        total_seconds = max(0, int(remaining.total_seconds()))
        
        # Format remaining time dynamically
        if total_seconds >= 3600:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if minutes > 0:
                time_text = f"{hours}h {minutes}m"
            else:
                time_text = f"{hours}h"
        elif total_seconds >= 60:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if seconds > 0:
                time_text = f"{minutes}m {seconds}s"
            else:
                time_text = f"{minutes}m"
        else:
            time_text = f"{total_seconds}s"
        
        embed.set_footer(
            text=f"Time remaining: {time_text} • Total votes: {total_votes} • Created by {self.creator.display_name}", 
            icon_url=self.creator.display_avatar.url
        )
        
        return embed
    
    def create_progress_bar(self, percentage: float) -> str:
        filled = int(percentage / 10)  # 10 characters max
        bar = "█" * filled + "░" * (10 - filled)
        return f"`{bar}`"
    
    async def update_time_remaining(self):
        """Update the poll embed every minute with remaining time"""
        while True:
            try:
                # Check if poll has ended
                remaining = self.end_time - datetime.utcnow()
                if remaining.total_seconds() <= 0:
                    await self.end_poll()
                    break
                
                # Update the embed with current time
                embed = self.create_results_embed()
                await self.message.edit(embed=embed)
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Error updating poll time: {e}")
                break
    
    async def end_poll(self):
        """End the poll and show final results"""
        # Disable all buttons
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        
        # Create final results embed
        final_embed = self.create_final_embed()
        
        try:
            await self.message.edit(embed=final_embed, view=self)
            await self.message.reply("🗳️ **This poll has ended!**")
        except discord.NotFound:
            pass  # Message was deleted
    
    def create_final_embed(self):
        total_votes = sum(self.votes)
        
        embed = discord.Embed(
            title=f"📊 POLL ENDED: {self.question}",
            color=discord.Color.gold()
        )
        
        if total_votes > 0:
            winner_index = self.votes.index(max(self.votes))
            winner_text = f"**Winner: {self.options[winner_index]}** 🏆"
            embed.add_field(name="Results", value=winner_text, inline=False)
        
        for i, (option, votes) in enumerate(zip(self.options, self.votes)):
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar = self.create_progress_bar(percentage)
            
            winner_emoji = "🏆" if i == winner_index else ""
            
            embed.add_field(
                name=f"{winner_emoji} {i+1}. {option}",
                value=f"{bar} {votes} votes ({percentage:.1f}%)",
                inline=False
            )
        
        embed.set_footer(
            text=f"Final results • Total votes: {total_votes} • Created by {self.creator.display_name}", 
            icon_url=self.creator.display_avatar.url
        )
        return embed

@app_commands.command(name="poll", description="Create a simple poll with up to 5 options")
@app_commands.describe(
    question="The poll question",
    option1="First option",
    option2="Second option",
    option3="Third option (optional)",
    option4="Fourth option (optional)",
    option5="Fifth option (optional)",
    duration="Poll duration in minutes (1-1440, default: 30)"
)
async def poll(
    interaction: discord.Interaction,
    question: str,
    option1: str,
    option2: str,
    option3: Optional[str] = None,
    option4: Optional[str] = None,
    option5: Optional[str] = None,
    duration: Optional[int] = 30
):
    """Simple poll command with duration input and dynamic time display"""
    
    # Validate duration
    if duration < 1 or duration > 1440:  # Max 24 hours
        await interaction.response.send_message("❌ Duration must be between 1 and 1440 minutes (24 hours)!", ephemeral=True)
        return
    
    # Collect options
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    if option5: options.append(option5)
    
    # Validate options
    if len(options) < 2:
        await interaction.response.send_message("❌ You need at least 2 options for a poll!", ephemeral=True)
        return
    
    if len(options) > 5:
        await interaction.response.send_message("❌ Maximum 5 options allowed!", ephemeral=True)
        return
    
    # Create initial embed
    initial_embed = discord.Embed(
        title=f"📊 {question}",
        description="Click the buttons below to vote!",
        color=discord.Color.purple()  # Purple color
    )
    
    initial_embed.add_field(
        name="Options", 
        value="\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)]), 
        inline=False
    )
    
    # Calculate initial time remaining
    end_time = datetime.utcnow() + timedelta(minutes=duration)
    remaining = end_time - datetime.utcnow()
    total_seconds = int(remaining.total_seconds())
    
    if total_seconds >= 3600:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        time_text = f"{hours}h {minutes}m"
    elif total_seconds >= 60:
        minutes = total_seconds // 60
        time_text = f"{minutes}m"
    else:
        time_text = f"{total_seconds}s"
    
    initial_embed.set_footer(
        text=f"Time remaining: {time_text} • Total votes: 0 • Created by {interaction.user.display_name}", 
        icon_url=interaction.user.display_avatar.url
    )
    
    # Create and send poll
    view = SimplePollView(question, options, duration, interaction.user)
    
    await interaction.response.send_message(embed=initial_embed, view=view)
    
    # Store reference to the message in the view
    message = await interaction.original_response()
    view.message = message
    
    # Start the time update task
    asyncio.create_task(view.update_time_remaining())
    
    # Start the auto-end task
    async def auto_end_poll():
        await asyncio.sleep(duration * 60)  # Wait for the duration
        await view.end_poll()
    
    asyncio.create_task(auto_end_poll())

def setup(bot):
    bot.tree.add_command(poll)