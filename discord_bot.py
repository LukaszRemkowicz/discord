import datetime
import random
from typing import Optional

import discord
from unidecode import unidecode
from discord.ext.commands import Context
from discord.ext import commands, tasks

from logger import get_module_logger, ColoredLogger
from repos.api_repo import APIRepo
from repos.types import Coords
from settings import BOT_NAME, TOKEN, DISCORD_LOGS, CHANNELS
from use_cases.use_case import DiscordUseCase

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)
logger: ColoredLogger = get_module_logger("DISCORD")


@bot.event
async def on_ready():
    """searching the guild with name of the variable GUILD:"""
    guild = discord.utils.get(bot.guilds)
    members = "\n - ".join(
        [member.name for member in guild.members if member.name != BOT_NAME]
    )

    logger.welcome_msg(
        f"{bot.user} is connected to the following guild:\n\n"
        f"Welcome to {guild.name} guild (id: {guild.id}) \n"
        f"Guild Members:\n\n - {members}\n"
        "\nDebugs prints:  \n"
    )
    message_channel_id = 1065217359247310851
    message_channel = bot.get_channel(message_channel_id)
    await message_channel.send('I\'m back. Did you miss me?')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to our Discord server!")


@bot.command(
    name="um",
    pass_context=True,
    help="Returns UM diagram for given city ",
)
async def um_on_wish(ctx: Context, city_name: str) -> None:
    """Returns UM diagram for given city"""

    city_decoded: str = unidecode(city_name)
    logger.info(f"parsing meteogram for city {city_decoded}")

    scrapper_use_case: DiscordUseCase = DiscordUseCase(
        db_repo="",
        scrapper_repo=APIRepo,
    )
    coords: Optional[Coords] = await scrapper_use_case.get_coords(city_name)

    if coords:
        url_res: str = await scrapper_use_case.icm_database_search(city_name, coords)  # noqa
        await ctx.send(file=discord.File(url_res))
    else:
        await ctx.send(f"Wrong city")


@bot.command(
    name="moon",
    pass_context=True,
    help="Returns moon information ",
)
async def get_moon(ctx: Context, day: str) -> None:
    """Returns moon information"""

    scrapper_use_case: DiscordUseCase = DiscordUseCase()
    coords: Optional[Coords] = await scrapper_use_case.get_moon_img(day)

    if coords:
        url_res: str = await scrapper_use_case.icm_database_search(city_name, coords)  # noqa
        await ctx.send(file=discord.File(url_res))
    else:
        await ctx.send(f"Wrong city")


@bot.event
async def on_error(event, *args):

    date = datetime.datetime.now()

    with open(DISCORD_LOGS.format(date=date.strftime("%d-%m-%Y %H:%M:%S")), "w") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You do not have the correct role for this command.")


@tasks.loop(hours=random.choice([3, 4, 6, 8]))
async def called_once_a_some_hours():
    await bot.wait_until_ready()
    answers = [
        "Hey, you missed me?",
        "Its Friday soon   \\.^.^./",
        "whats uuuuuuuuuup?",
    ]
    message_channel_id = CHANNELS.get('DEFAULT')
    message_channel = bot.get_channel(message_channel_id)
    whats_the_hour_now = datetime.datetime.now().time().strftime("%H")
    if 22 > int(whats_the_hour_now) > 7:
        response = random.choice(answers)
        await message_channel.send(response)


# @called_once_a_some_hours.before_loop
# async def before():
#     await bot.wait_until_ready()
#     print("Finished waiting")
#
#
# called_once_a_some_hours.start()

async def setup_hook():
    called_once_a_some_hours.start()
bot.setup_hook = setup_hook

# @tasks.loop(hours = 1)
# async def remindstudy():
#   await bot.wait_until_ready()
#   channel = bot.get_channel(CHANNELS.get('DEFAULT'))
#   await channel.send("check")

#
# @called_once_a_some_hours.before_loop
# async def before():
#     await bot.wait_until_ready()
#     print("Finished waiting")
#
#
# # called_once_a_some_hours.start()
#

bot.run(TOKEN)
