maestrobot
==========
A Twitch bot written in Python 3

To install and use, simply clone the git repository and run the `run.py` file (in the `/src` directory) using Python 3.x. Each bot object requires a name, oauth key, and a list of channels to connect to. Additionally, you may wish to add a list of administrators to the bot, i.e., Twitch users who can use admin-only commands and are immune to time restrictions. Also, you can associate a bot with a list of channels whose chat logs you wish to record.

The `run.py` is, by default, configured to create and run a single bot, but you can create and run as many bots as you like (but note that they will all use the same command list and prohibited word list. To make bots with different lists, clone the repository multiple times).

## Commands:

Commands can be added to the bot by bot administrators in two ways: writing new commands in the command.json file, or using the `!addcommand` command in chat (bot admins only). Note that the latter can only add commands where we expect to return new chat messages, and any commands which require logic or preprocessing will have to be manually coded in, along with the functions. maestrobot comes with a few examples. Use `!delcommand` to delete a given command. Note that all command-related functions should be in `utilities.py`!

Example usage of `!addcommand`:

    !addcommand !dance SourPls
    # Now, when a user in chat types !dance, the bot will respond with SourPls

To create commands only the bot admins can use, use two exclamation points, like so:

    !addcommand !!dance SourPls
    # Now, when a bot admin types !dance, the bot will respond with SourPls

Commands in the `commands.json` file are kept in the following way:

      # {"!commandname": ["RETURN", "FUNC", "ADMIN"]}
      # RETURN: What the bot should respond with. If a function needs to be called, put the function name here
      # FUNC: put "FUNC" here if the command uses a function. Otherwise, leave blank
      # ADMIN: put "ADMIN" here if the command is admin-only. Otherwise, leave blank


## Logs

__maestrobot__ can keep local logs of the chat messages, stored in the `/local_logs` folder as `.txt` files. In order to record a chat, add the channel name to both `bot.channels` and `bot.record`. The name of the `.txt` file will be the channel name and the date.

## Moderator functions

If your bot is a moderator to the chat, set `bot.is_moderator = True`. Now, you can create functions for managing the chat, including the built-in timeout function, which timesout a user for using a prohibited chat phrase. The prohibited phrase are kept in `prohibited.json` as a dictionary `{"banned_word": "timeout length"}`. Timeouts can be days (d), hours (h), minutes (m) or seconds (s), for example "7d" = timeout for 7 days. You can add and delete prohibited phrases by using `!add` and `!del` (ex: `!add 7d website.com`), or by editing the file directly.

## Notes

From here, the bot should be pretty straight forward. My hope is that it's at least somewhat scalable, such that additional commands and functions can be added without too much hassle. There isn't much to the bot out of the box.

