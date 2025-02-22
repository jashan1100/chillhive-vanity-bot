import discord
import json
from discord.ext import commands
from vanity import handle_ready, handle_presence_update, ping_command, info_command, say, server_info, flip, roll, eight_ball  # Import necessary functions

# Load configuration from config.json
with open('config.json') as f:
    config = json.load(f)

token = config.get('token')
prefix = config.get("prefix")
vanities = config.get("vanities")  # List of vanity URLs
role_id = int(config.get("role_id"))  # Ensure this is an integer
log_channel_id = int(config.get("log_channel_id"))  # Ensure this is an integer

intents = discord.Intents().all()  # Make sure to enable all necessary intents
bot = commands.Bot(command_prefix=f'{prefix}', intents=intents)

bot.remove_command('help')  # Remove default help command

# Event when the bot is ready
@bot.event
async def on_ready():
    """
    Call the handle_ready function from vanity.py.
    This ensures we are calling the logic with the correct arguments.
    """
    await handle_ready(bot, log_channel_id)

# Event when user presence changes
@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    """
    Call the handle_presence_update function from vanity.py.
    This will handle presence-based role assignments/removals.
    """
    await handle_presence_update(before, after, vanities, role_id, log_channel_id, bot)

# Ping Command (Latency Check)
@bot.command(name='ping')
async def ping(ctx):
    await ping_command(ctx)

# Info Command (Bot Information)
@bot.command(name='info')
async def info(ctx):
    await info_command(ctx)

# Say Command (Bot repeats user's message)
@bot.command(name='say')
@commands.has_permissions(administrator=True)
async def say_command(ctx, *, message: str):
    await say(ctx, message=message)

# Server Info Command
@bot.command(name='serverinfo')
async def server_info_command(ctx):
    await server_info(ctx)

# Flip Command (Coin Flip)
@bot.command(name='flip')
async def flip_command(ctx):
    await flip(ctx)

# Roll Command (Dice Roll)
@bot.command(name='roll')
async def roll_command(ctx):
    await roll(ctx)

# 8 Ball Command (Random Answer Generator)
@bot.command(name='8ball')
async def eight_ball_command(ctx, *, question: str):
    await eight_ball(ctx, question=question)

# Start the bot
if __name__ == "__main__":
    try:
        bot.run(token)
    except Exception as e:
        print(f"Failed to start bot: {e}")
        traceback.print_exc()  # Log the error if bot fails to start
