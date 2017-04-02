"""
A collection of functions called by the bot
These should be either in response to a !command from chat or for using /commands
Includes a simple function for timing-out a user as an example.
Other commands https://help.twitch.tv/customer/portal/articles/659095-chat-moderation-commands
"""


def timeout(username, time):
    """
    Timeout a user for a given number of minutes
    Returns the timeout command and the chat message
    """
    if time[-1] == "m":  # minutes
        time_out = str(int(time[:-1])*60)
    elif time[-1] == "h":  # hours 
        time_out = str(int(time[:-1])*60*60)
    elif time[-1] == "d":  # days
        time_out = str(int(time[:-1])*60*60*24)
    else:
        time_out = time[:-1]  # assumed to be seconds (ex: 4s)
    return [('/timeout ' + username + ' ' + time_out),
            (str(time) + ' ' + str(username) + ' for prohibited phrase')]


def new_command(arguments):
    """forms message into a list containing command information"""
    command, event = arguments.split(' ', 1)
    command_list = ["" for i in range(4)]
    if command.startswith("!"):
        command_list[0] = command
        command_list[1] = event
        if command.startswith("!!"):
            command_list[0] = command[1:]
            command_list[3] = "ADMIN"
        return command_list


def google(arguments):
    """
    a sample function: creates a google link to google a list of search term arguments
    example !google neat thing
    bot: http://google.com/search?q=neat+thing
    """
    arg_list = arguments.split(' ')
    url_base = "http://google.com/search?q="
    for token in arg_list:
        if token != "":
            url_base += token + "+"
    if url_base.endswith("="):
        return ""
    return url_base[:-1]


# add other functions here (and to command list)
