import discord
from discord import app_commands

@app_commands.command(name="ping", description="Check bot's latency and status")
async def ping(interaction: discord.Interaction):
    bot_latency = round(interaction.client.latency * 1000)  # Convert to ms
    websocket_latency = round(interaction.client.latency * 1000)
    
    if bot_latency < 100:
        status_emoji = "🟢"
        status_text = "Excellent"
        color = discord.Color.green()
    elif bot_latency < 200:
        status_emoji = "🟡"
        status_text = "Good"
        color = discord.Color.orange()
    else:
        status_emoji = "🔴"
        status_text = "Slow"
        color = discord.Color.red()
    
    embed = discord.Embed(
        title="<:pingpong:1427537352447754262> Pong!",
        description=f"{status_emoji} **Connection Status: {status_text}**",
        color=color
    )
    
    embed.add_field(
        name="<:snow:1427793833604681779> Bot Latency",
        value=f"`{bot_latency}ms`",
        inline=True
    )
    
    embed.add_field(
        name="<:wifi:1427793462291464273> WebSocket",
        value=f"`{websocket_latency}ms`",
        inline=True
    )
    
    embed.add_field(
        name="<:globe:1427520126055350335> Amethis Status",
        value="Online and responsive",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.tree.add_command(ping)