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
    log_channel_id = int(os.environ["LOG_CHANNEL_ID"])
except:
    log_channel_id = None

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
                    if row[0].lower() == name.lower():
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
        name, ticket_number = info.split(",")
        mem_nick = list(map(lambda mem: mem.nick, ctx.guild.members))
        if name in mem_nick:
            await ctx.send(
                f"{ctx.author.mention} Sorry, your name has already been register. The reason could be:\n1) your ticket has not be assgined to you property or;\n2) although it seems quite rare, someone has the same name as you.\n\nYou may ask the person who bought you the ticket to check if they have assgin the ticket to you with your full name. In anycase, if you need a team member to help, contact '@registration'"
            )
            roles = []
            log_msg = f"FAIL: Request form user {ctx.author} with name={name}, ticket_no={ticket_number} has duplicated name"
        else:
            roles = roles_given(name, ticket_number)

        if roles is None:
            log_msg = f"FAIL: Cannot find request form user {ctx.author} with name={name}, ticket_no={ticket_number}"
            await ctx.send(
                f"{ctx.author.mention} Sorry, cannot find the ticket #{ticket_number} with name: {name}.\n\nPlease check and make sure you put down your full name same as the one you used in registering your ticket then try again.\n\nIf you want a team member to help you, please reply to this message with '@registration'"
            )
        elif len(roles) > 0:
            log_msg = f"SUCCESS: Register user {ctx.author} name={name}, ticket_no={ticket_number} with roles={roles}"

            await ctx.message.add_reaction("🎟️")
            await ctx.message.add_reaction("🤖")
            await ctx.author.edit(nick=name)
            attendee_role = get(ctx.author.guild.roles, name="attendee")
            await ctx.author.add_roles(attendee_role)

            for role in roles:
                role_id = get(ctx.author.guild.roles, name=role)
                await ctx.author.add_roles(role_id)

            await ctx.author.send(welcome_msg(ctx.author.mention, roles))

        if log_msg is not None:
            logging.info(log_msg)
            if log_channel_id is not None:
                await bot.get_channel(log_channel_id).send(log_msg)


@bot.command()
async def help(ctx):
    if not only_respond_reg or ctx.channel.id == reg_channel_id:
        await ctx.send(instruction)


bot.run(os.environ["REG_BOT_SECRET"])
