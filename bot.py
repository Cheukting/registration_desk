import csv
import logging
import os
import discord
from discord.ext import commands, tasks
from discord.utils import get

# logging config
logging.basicConfig(
    filename=".log/reg.log",
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
    datefmt="%d-%b-%y %H:%M:%S",
)

# set up channel ids and enviroment variables
reg_channel_id = int(os.environ["REG_CHANNEL_ID"])

try:
    speaker_channel_id = int(os.environ["SPEAKER_CHANNEL_ID"])
except:
    speaker_channel_id = reg_channel_id

try:
    attendee_channel_id = int(os.environ["ATTENDEE_CHANNEL_ID"])
except:
    attendee_channel_id = reg_channel_id

try:
    sprinter_channel_id = int(os.environ["SPRINTER_CHANNEL_ID"])
except:
    sprinter_channel_id = reg_channel_id

try:
    only_respond_reg = int(os.environ["ONLY_RESPOND_REG"])
except:
    only_respond_reg = False

# TODO: seperate customization in conf file
event_name = "EuroPython"

instruction = f"Welcome to {event_name}! Please use `!register <Full Name>, <Ticket Number>` to register.\nE.g. `!register James Brown, 99999`\nNOTE: please ONLY register for YOURSELF."


def welcome_msg(mention, roles):
    if len(roles) == 2:
        return f"Welcome {mention}, you now have the {roles[0]} and {roles[1]} roles."
    elif len(roles) == 1:
        return f"Welcome {mention}, you now have the {roles[0]} role."
    else:
        text = roles[1:-1].join(", ")
        return f"Welcome {mention}, you now have the {roles[0]}, {text} and {roles[-1]} roles."


bot = commands.Bot(
    command_prefix="!",
    description=f"Registration Desk for {event_name}",
    help_command=None,
)


def roles_given(name, ticket_no):
    # check the roles that need to be given to the user
    # return list of roles that need to be given
    with open(os.environ["DATA_PATH"], newline="") as csvfile:
        datareader = csv.reader(csvfile, delimiter=",")
        for row in datareader:
            try:  # skip if it's header
                if int(row[4]) == int(ticket_no):
                    if row[0] == name:
                        if row[3] == "sprint":
                            return ["sprinter"]
                        if row[2] == "yes":
                            return ["speaker", "attendee"]
                        else:
                            return ["attendee"]
            except:
                continue


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
    if not only_respond_reg or ctx.channel.id == reg_channel_id:
        info = info.split(",")
        roles = roles_given(info[0], info[1])
        if roles is None:
            logging.info(
                f"FAIL: Cannot find request form user {ctx.author} with name={info[0]}, ticket_no={info[1]}"
            )
            await ctx.send(
                f"{ctx.author.mention} Sorry cannot find the ticket #{info[1]} with name: {info[0]}.\nPlease check and make sure you put down your full name same as the one you used in registering your ticket then try again.\nIf you want a team member to help you, please reply to this message with '@registration'"
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

            for role in roles:
                role_id = get(ctx.author.guild.roles, name=role)

                await ctx.author.add_roles(role_id)

            if "speaker" in roles:
                await bot.get_channel(speaker_channel_id).send(
                    welcome_msg(ctx.author.mention, roles)
                )
            elif "attendee" in roles:
                await bot.get_channel(attendee_channel_id).send(
                    welcome_msg(ctx.author.mention, roles)
                )
            elif "sprinter" in roles:
                await bot.get_channel(sprinter_channel_id).send(
                    welcome_msg(ctx.author.mention, roles)
                )


@bot.command()
async def help(ctx):
    if not only_respond_reg or ctx.channel.id == reg_channel_id:
        await ctx.send(instruction)


bot.run(os.environ["REG_BOT_SECRET"])
