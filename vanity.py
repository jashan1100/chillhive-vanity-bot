import discord
import traceback
from discord.ext import commands
import random

# Function to send embed for role assignments/removals
async def send_role_assigned_embed(user, role, action, description, log_channel_id, bot):
    try:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title=f"Role {action}",
                description=description,
                color=discord.Color.green() if action == "Assigned" else discord.Color.red()
            )
            embed.set_author(name=user.name, icon_url=user.avatar.url)
            embed.add_field(name="Role", value=role.name if role else "None", inline=False)
            embed.add_field(name="User", value=user.mention, inline=False)
            embed.set_footer(text=f"Action performed at")
            embed.timestamp = discord.utils.utcnow()

            await log_channel.send(embed=embed)
        else:
            print("Log channel not found. Please check your channel ID in the config.")
    except Exception as e:
        print(f"Error in send_role_assigned_embed: {e}")
        traceback.print_exc()


# Function to handle custom logic when the bot is ready
async def handle_ready(bot, log_channel_id):
    """
    This function is called to handle the custom actions that should happen when the bot is ready.
    It accepts `bot` and `log_channel_id` as arguments.
    """
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="discord.gg/chillhive")
    )
    print(f"Bot connected as {bot.user}")
    await send_role_assigned_embed(bot.user, None, "Bot online", "Initial bot presence", log_channel_id, bot)


# Helper function to manage presence-based role assignments/removals
async def handle_presence_update(before, after, vanities, role_id, log_channel_id, bot):
    """
    This function contains the logic to assign/remove roles based on vanity URLs in the user's activity.
    It is called inside the on_presence_update event.
    """
    # Ignore if the user goes offline or comes online
    if before.status == discord.Status.offline or after.status == discord.Status.offline:
        return

    try:
        # Fetch the role directly from the guild
        role = await after.guild.fetch_role(role_id)

        # Log the activities for debugging purposes
        print(f"Before activity: {before.activity}, After activity: {after.activity}")

        for vanity_url in vanities:
            # If before activity is None and after activity is set, check if it contains the vanity URL
            if before.activity is None and after.activity is not None:
                if vanity_url in after.activity.name:
                    await after.add_roles(role)
                    await send_role_assigned_embed(after, role, "Assigned",
                                                   f"{after.mention} has been assigned the role **{role.name}** for activity: {after.activity.name}",
                                                   log_channel_id, bot)

            # If both before and after activities are set, check if the vanity URL is in the activities
            elif before.activity is not None and after.activity is not None:
                if vanity_url in before.activity.name and vanity_url not in after.activity.name:
                    await after.remove_roles(role)
                    await send_role_assigned_embed(after, role, "Removed",
                                                   f"{after.mention} has been removed from the role **{role.name}** for activity: {before.activity.name}",
                                                   log_channel_id, bot)
                elif vanity_url not in before.activity.name and vanity_url in after.activity.name:
                    await after.add_roles(role)
                    await send_role_assigned_embed(after, role, "Assigned",
                                                   f"{after.mention} has been assigned the role **{role.name}** for activity: {after.activity.name}",
                                                   log_channel_id, bot)

            # If before activity is set and after activity is None, remove role if it had the vanity URL
            elif before.activity is not None and after.activity is None:
                if vanity_url in before.activity.name:
                    await after.remove_roles(role)
                    await send_role_assigned_embed(after, role, "Removed",
                                                   f"{after.mention} has been removed from the role **{role.name}** for activity: {before.activity.name}",
                                                   log_channel_id, bot)

    except Exception as e:
        print(f"Error in handle_presence_update: {e}")
        traceback.print_exc()


# Ping Command - Responds with bot's latency
async def ping_command(ctx):
    latency = round(ctx.bot.latency * 1000)  # Convert from seconds to milliseconds
    embed = discord.Embed(
        title="Pong!",
        description=f"Latency: `{latency}ms`",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


# Info Command - Sends bot information in an embed
async def info_command(ctx):
    embed = discord.Embed(
        title="Bot Information",
        description="Here is some information about this bot.",
        color=discord.Color.blue()
    )

    # Bot profile picture
    embed.set_thumbnail(url=ctx.bot.user.avatar.url)  # Bot's PFP

    # Developer info
    embed.add_field(
        name="Developer",
        value="Sukhoi Su-57 (<@1055478146981429396>)",
        inline=False
    )

    # Owner Info
    embed.add_field(
        name="Chill Hive Oxnz",
        value="!! Dev.. ?🥀 (<@1086299728318308382>)",
        inline=False
    )
    # Bot's purpose
    embed.add_field(
        name="Made For",
        value="discord.gg/chillhive",
        inline=False
    )

    # Send the embed
    await ctx.send(embed=embed)


# Server Info Command - Sends information about the server
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"Server Info: {guild.name}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Total Members", value=guild.member_count, inline=False)

    # If you want to show the preferred locale instead of region
    embed.add_field(name="Locale", value=guild.preferred_locale, inline=False)

    await ctx.send(embed=embed)


# Coin Flip Command
async def flip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f"The coin landed on: **{result}**")


# Dice Roll Command
async def roll(ctx):
    roll = random.randint(1, 6)
    await ctx.send(f"You rolled a **{roll}**!")


# Magic 8-Ball Command
async def eight_ball(ctx, question: str):
    responses = ["Yes", "No", "Maybe", "Ask again later", "Definitely not", "Absolutely!"]
    response = random.choice(responses)
    await ctx.send(f"Question: {question}\nAnswer: {response}")


from discord.ext import commands

@commands.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message: str):
    """
    Makes the bot repeat the user's message.
    Only users with Administrator permissions can use this command.
    """
    await ctx.message.delete()  # Delete the command message so it doesn't clutter the chat
    await ctx.send(message)  # Bot sends the message

# Error handling for missing permissions
@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the required permissions to use this command.")
