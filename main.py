import os
import discord
from dotenv import load_dotenv
from bot import Bot

def main():
    # Load environment variables
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    app_id = os.getenv('APP_ID')
    
    if not token or not app_id:
        print("Error: DISCORD_TOKEN and APP_ID must be set in .env file")
        return
    
    # Create bot instance
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = Bot(intents=intents)
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    main()