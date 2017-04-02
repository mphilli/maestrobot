from bot import Bot

if __name__ == "__main__":
    """run the bot"""
    print("Maestro Bot 1.0")
    print("run.py")
    # must specify the bot's name, oauth key, and list of channels to connect to
    name, oauth, channels = "", "", []
    admins, record = [], []    # OPTIONAL: add bot administrators or list of channels to log
    if name == "":
        name = input("bot name: ")
    if oauth == "":
        oauth = input("oauth key: ")
    if not channels:
        # use whitespace as delimiter
        channels = input("channels: ").split(' ')

    # create bot object
    twitch_bot = Bot((name, oauth), channels, admins, record)

    # twitch_bot.is_moderator = True  # if bot is a moderator to the channel(s)
    # call run() to run the bot
    twitch_bot.run()

    """
    # For a list of bots
    bots = []  # list of bots - FORMAT: ([name,  oauth], [channels], [admins], [record_chat])
    # note: admins and record_chat can be 'None', but must be passed
    for bot in bots:
        # create and run each bot in the bots list
        Bot([bot[0], bot[1], bot[2], bot[3]).run()
    """
