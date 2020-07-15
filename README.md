# registration_desk
Discord bot to help out at registration desk of a conference

Roles will be given to successful registration:

* `speaker` and `attendee` if it's a speaker ticket to the conference
* `attendee` if it's a non-speaker ticket to the conference
* `sprinter` if it's a sprint ticket

## Ticket checking logic

The users' name and ticket will be check against the data in the CSV file. The check will fail if:

1) The user's full name is the same as someone's name in the channel (name has been registered before)

2) There is no match, matching of name is case insensitive.

## Set up environment variables

The bot need certain environment variables for it to work:

* REG_BOT_SECRET - secret fo the bot, provided by Discord
* REG_CHANNEL_ID -  id of the channel that is used for resignation, the channel that you want the bot to listen to. (It only listens to this channel if ONLY_RESPOND_REG is True)
* LOG_CHANNEL_ID -  (OPTIONAL) id of the channel that is used for logging (if it is not set, it will not be sending the log to any channels)
* DATA_PATH - path to the data CSV (see below for the format explanation)
* ONLY_RESPOND_REG - (OPTIONAL) if True bot only response to the registration channel, default is False

If no `SPEAKER_CHANNEL_ID` is set, the welcome message will be display on registration channel. Same apply to `ATTENDEE_CHANNEL_ID`.

## Getting a channel id

1. Go to user setting in Discord App
2. Go to Appearance
3. Scroll down and check the Developer mode in the Advance session
4. Go back to the server and right click on the channel
5. Select Copy ID, now the id is in your clip board

## Data CSV

The format of the CSV needs to satisfy the format of:

`name, email, is_speaker, ticket_class, ticket_id, other cols...`

for each row.

For example:

`Testing, testing@gmail.com, no, conference, 11111, TRSP`

Any change of the data CSV will be reflected live in the bot.

## Log file

Log file is saved at .log/reg.log
