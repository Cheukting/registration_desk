import csv
import logging
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get

logging.basicConfig(
    filename=".log/reg.log",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
    datefmt="%d-%b-%y %H:%M:%S",
)

data_file = ".data/data.csv"

reg_channel_id = int(os.environ["REG_CHANNEL_ID"])
event_name = "EuroPython"
instruction = f"Welcome to {event_name}! Please use `!register <Full Name>, <Ticket Number>` to register.\nE.g. `!register James Brown, 99999`\nNOTE: please ONLY register for YOURSELF."

bot = commands.Bot(
    command_prefix="!",
    description=f"Registration Desk for {event_name}",
    help_command=None,
)


def is_speaker(name, ticket_no):
    with open(data_file, newline="") as csvfile:
        datareader = csv.reader(csvfile, delimiter=",")
        for row in datareader:
            if int(row[3]) == int(ticket_no):
                if row[0] == name:
                    if row[2] == "yes":
                        return True
                    else:
                        return False


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.listening, name="!help"),
    )
    await bot.get_channel(reg_channel_id).send(instruction)
    print("Bot is ready")
    logging.info("Bot logged in")


@bot.command()
async def register(ctx, *, info):
    info = info.split(",")
    speaker = is_speaker(info[0], info[1])
    if speaker is None:
        logging.info(
            f"FAIL: Cannot find request form user {ctx.author} with name={info[0]}, ticket_no={info[1]}"
        )
        await ctx.send(
            f"{ctx.author.mention} Sorry cannot find the ticket #{info[1]} with name: {info[0]}.\nPlease check and make sure you put down your full name same as the one you used in registering your ticket then try again."
        )
    else:
        logging.info(
            f"SUCCESS: Register user {ctx.author} with name={info[0]}, ticket_no={info[1]}"
        )
        await ctx.message.add_reaction("🎟️")
        await ctx.message.add_reaction("🤖")
        await ctx.author.edit(nick=info[0])
        attendee_role = get(ctx.author.guild.roles, name="attendee")
        await ctx.author.add_roles(attendee_role)
        if speaker:
            speaker_role = get(ctx.author.guild.roles, name="speaker")
            await ctx.author.add_roles(speaker_role)
            await ctx.send(
                f"Welcome {ctx.author.mention}, you now have the speaker and attendee role."
            )
        else:
            await ctx.send(
                f"Welcome {ctx.author.mention}, you now have the attendee role."
            )


@bot.command()
async def help(ctx):
    await ctx.send(instruction)


bot.run(os.environ["REG_BOT_SECRET"])
