import datetime
import random
from typing import Optional, Union

import discord
from unidecode import unidecode
from discord.ext.commands import Context
from discord.ext import commands, tasks

from logger import get_module_logger, ColoredLogger
from repos.api_repo import APIRepo
from repos.db_repo import MoonRepo
from repos.models import Coords
from settings import Settings
from use_cases.use_case import DiscordUseCase
from utils.db_utils import DBConnectionHandler
from utils.utils import Validator

settings: Settings = Settings()


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)
logger: ColoredLogger = get_module_logger("DISCORD")


@bot.event
async def on_ready():
    """Discord startup"""
    guild = discord.utils.get(bot.guilds)
    members = "\n - ".join(
        [member.name for member in guild.members if member.name != settings.BOT_NAME]
    )

    logger.welcome_msg(
        f"{bot.user} is connected to the following guild:\n\n"
        f"Welcome to {guild.name} guild (id: {guild.id}) \n"
        f"Guild Members:\n\n - {members}\n"
        "\nDebugs prints:  \n"
    )


@bot.event
async def on_member_join(member):
    """Event for member joining server"""
    await member.create_dm()
    await member.dm_channel.send(f"Hi {member.name}, welcome to our Discord server!")


@bot.command(
    name="um",
    pass_context=True,
    help="Returns UM diagram for given city ",
)
async def um_on_wish(ctx: Context, city_name: Optional[str] = None) -> None:
    """Returns UM diagram for given city"""

    if not city_name:
        await ctx.send("City not given. Command cannot be empty")
    else:
        city_decoded: str = unidecode(city_name)
        logger.info(f"parsing meteogram for city {city_decoded}")
        use_case: DiscordUseCase = DiscordUseCase(
            db_repo=MoonRepo,
            scrapper_repo=APIRepo,
        )
        coords: Optional[Coords] = await use_case.get_coords(city_name)
        url_res: Optional[str] = await use_case.icm_database_search(city_name, coords)

        if url_res:
            await ctx.send(file=discord.File(url_res))
        else:
            await ctx.send(f"Wrong city")


@bot.command(
    name="moon",
    pass_context=True,
    help="Returns moon information. Usage example: !moon '20.01.2023'",
)
async def get_moon(ctx: Context, day: Optional[str] = None) -> None:
    """Returns moon information"""

    use_case: DiscordUseCase = DiscordUseCase(
        db_repo=MoonRepo,
        scrapper_repo=APIRepo,
    )

    if not day:
        await ctx.send("Date is not valid. Should be format like: '20.01.2023'")
    else:
        data_validator: Union[dict, str]
        with Validator(date=day) as res:
            data_validator = res

        async with DBConnectionHandler():
            if isinstance(data_validator, dict) and data_validator.get("error"):
                await ctx.send(res.get("error"))
            else:
                url_res: str = await use_case.get_moon_img(date_str=day)
                if isinstance(url_res, dict) and url_res.get("error"):
                    await ctx.send(url_res.get("error"))
                else:
                    await ctx.send(file=discord.File(url_res))


@bot.event
async def on_error(event, *args):
    date = datetime.datetime.now()

    with open(
        settings.DISCORD_LOGS.format(date=date.strftime("%d-%m-%Y %H:%M:%S")), "w"
    ) as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


@bot.event
async def on_command_error(ctx, error):
    logger.error(error)
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
    message_channel_id = settings.CHANNELS.get("DEFAULT")
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

bot.run(settings.TOKEN)
