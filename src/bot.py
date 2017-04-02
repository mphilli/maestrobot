import datetime
import os
import re
import select
import socket
import json
import time
import utilities as util


class Bot:
    """A Twitch bot written in Python 3"""
    def __init__(self, bot_info, in_channels, in_admins=None, record_chat=None):
        """
        :param bot_info: a tuple that consists of the bot's username and oauth key
        :param in_channels: the list of channels the bot should connect to
        :param in_admins: an optional list of bot administrators (needed for certain bot-related tasks)
        :param record_chat: an optional list of channels the bot should record chat logs for
        """
        self.terminate = False
        self.record = record_chat
        self.admins = in_admins
        self.name = bot_info[0]
        self.oauth = bot_info[1]
        self.channels = in_channels
        self.s = socket.socket()             # the connection socket object
        self.is_moderator = False            # set to True if bot has administrative privileges in the channel
        self.commands = self.get_commands()  # list of bot-familiar commands from bot_files/command_list.txt
        self.prohibited = self.get_prohibited()  # list of prohibited phrases and their associated timeout times
        self.time_restrict = 0    # number of seconds before another bot message can be sent (doesn't apply to admins)
        self.local_commands = ['!delcommand', '!add', '!del']
        self.last = 0             # the last time a message was sent (used for time-restricting commands)

    def establish_connection(self):
        """establish the connection to Twitch chat channels"""
        self.s.connect(('irc.chat.twitch.tv', 6667))
        self.s.send(('PASS ' + self.oauth + '\n').encode('utf-8'))
        self.s.send(('NICK '+self.name+'\n').encode('utf-8'))
        for channel in self.channels:
            self.s.send(('JOIN #'+channel+'\n').encode('utf-8'))
        self.s.send('CAP REQ :twitch.tv/commands\n'.encode())

    def run(self):
        """Establishes a connection and constantly reads incoming data from the server"""
        print('establishing connection...')
        self.establish_connection()
        time.clock()
        server_messages = ['USERSTATE', 'NOTICE', 'CLEARCHAT', 'USERNOTICE']
        while not self.terminate:
            readable, writable, exceptional = select.select([self.s], [self.s], [], 120)
            for read in readable:
                raw_recv = read.recv(2048).decode().strip("\r\n")
                if re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)', raw_recv):
                    message = self.format_message(raw_recv)
                    print('#' + message)
                    self.handle_message(message)
                elif re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)', raw_recv):
                    whisper = self.format_whisper(raw_recv)
                    print('(whisper to ' + self.name + "): " + ' '.join(whisper.split(' ')[1:]))
                    self.handle_whisper(whisper)
                elif raw_recv.find('PING :') != -1:
                    print(raw_recv)
                    self.ping()
                elif raw_recv.find(':tmi.twitch.tv NOTICE * :Login authentication failed') != -1:
                    print(raw_recv)
                    exit()
                elif len(raw_recv.split(' ')) > 1 and raw_recv.split(' ')[1] in server_messages:
                    pass  # Exclude from terminal output
                else:
                    # print all else
                    print(raw_recv)
        print("bot terminated")

    def ping(self):
        """Respond to the server ping and stay connected"""
        self.s.send('PONG :pingis\n'.encode())
        print("PONG :client")

    def handle_message(self, fmessage):
        """Handles various operations based on the latest received chat message (logging, commands, etc)"""
        channel, timestamp, username, message = fmessage.split(' ', 3)
        username = username[:-1]
        if not self.admins:  # testing should always be done be approved users
            self.admins = []

        # check if we should log the message(s):
        if self.record and channel in self.record:
                self.log_message(fmessage)

        # check if the message is a bot-familiar command:
        in_list = False
        if self.time_restricted(username) or username in self.admins:
            for command in self.commands:
                if message.lower().startswith(command):
                    self.handle_command(channel, command, message, username)
                    in_list = True
                    break
            if not in_list:
                for command in self.local_commands:
                    if message.lower().startswith(command):
                        self.handle_local_commands(channel, command, message, username)
                        break

        # check if a non-mod user has typed a prohibited phrase. timeout accordingly (if bot is an admin)
        if self.is_moderator:
            for phrase in self.prohibited:
                if phrase in message and (username not in self.admins or username != channel):
                    timeout_messages = util.timeout(username, self.prohibited[phrase])
                    for message in timeout_messages:
                        self.send_message(channel, message)

    def handle_whisper(self, fwhisper):
        """Handles various operations based on the latest received whisper"""
        name, timestamp, sender, message = fwhisper.split(' ', 3)
        sender = sender[:-1]

        # test sending whispers
        if self.admins:  # testing should always be done be approved users
            if message == "!psst" and sender in self.admins:
                self.send_whisper(sender, "Hey! I'm whispering!")
            elif message == "!terminate" and sender in self.admins:  # terminate the bot!
                self.terminate = True

    def time_restricted(self, username):
        """Checks if enough time has passed since the last bot message to satisfy the set time restriction"""
        if self.time_restrict > 0 and username not in self.admins:
            timeout = int(time.clock()) - self.time_restrict < self.last
            return not timeout or self.last == 0
        else:
            return True

    def handle_command(self, channel, command, message, username):
        """parses the command"""
        permission = True
        arguments = re.sub("^" + command, "", message).lstrip()  # the message minus the command
        if command in self.local_commands:
            self.handle_local_commands(channel, command, arguments, username)
        event = self.commands[command.lower()]
        if self.commands[command][2] == "ADMIN":
            permission = False
        if permission or username in self.admins:
            if self.commands[command][1] == "FUNC":
                func_name = self.commands[command][0]
                event = getattr(util, func_name)(arguments)
                # add new commands
                if func_name == "new_command" and len(event) == 4:
                    chat_message = "command already exists; command updated"
                    if event[0] not in self.commands:
                        chat_message = "command added"
                    self.add_command(event)
                    self.send_message(channel, chat_message)
                else:
                    self.send_message(channel, event)
            elif event != "":
                self.send_message(channel, event[0])

    def handle_local_commands(self, channel, command, message, username):
        arguments = re.sub("^" + command, "", message).lstrip()
        if command == "!delcommand" and username in self.admins:
            # delete a command
            delete = arguments.split(" ")[0].lower()
            if delete != "!addcommand" and delete != "!delcommand":
                delete_message = "command not found"
                if delete in self.commands:
                    self.del_command(delete)
                    delete_message = "command deleted"
                self.send_message(channel, delete_message)
        elif command == "!add" and username in self.admins:
            if len(arguments.split(" ")) > 1:
                timeout_length = arguments.split(" ")[0].lower()
                phrase = " ".join(arguments.split(" ")[1:])
                self.add_prohib(timeout_length, phrase)
                self.send_message(channel, "phrase added")
        elif command == "!del" and username in self.admins:
            phrase = arguments.split(" ")[0].lower()
            self.del_prohib(phrase)
            self.send_message(channel, "phrase deleted")

    def send_message(self, channel, message):
        """sends a chat message to the target channel"""
        self.s.send(('PRIVMSG ' + '#' + channel + ' :' + str(message) + '\r\n').encode("utf-8"))
        self.last = int(time.clock())
        timestamp = LogDate().timestamp
        formatted_message = channel + ' ' + timestamp + ' ' + self.name + ': ' + message
        if not message.startswith("/") or message.startswith("/me"):
            # don't record commands like /timeout
            print('#' + formatted_message)
            if channel in self.record:
                self.log_message(formatted_message)

    def send_whisper(self, receiver, message):
        """sends a whisper to the target user"""
        self.s.send(('PRIVMSG #jtv :/w ' + receiver + " " + message + '\r\n').encode("utf-8"))
        timestamp = LogDate().timestamp
        print("(whisper to " + receiver + ") " + timestamp + ' ' + self.name + ': ' + message)

    def format_whisper(self, whisper_raw):
        """Converts the incoming whisper to a readable format (receiver + timestamp + username + message)"""
        timestamp = LogDate().timestamp
        whisper = whisper_raw.split(':', 2)
        sender = whisper_raw.split(':', 2)[1].split('!')[0]
        message = whisper[2]
        whisper = self.name + ' ' + timestamp + ' ' + sender + ": " + message
        return whisper

    @staticmethod
    def format_message(message_raw):
        """Converts the incoming chat messages to a readable format (channel + timestamp + username + message)"""
        message_raw = message_raw.split(':', 2)
        if len(message_raw) > 2:
            try:
                username = message_raw[1].split("!", 1)[0]  # the Twitch username of the person who sent this message
                message = message_raw[2]  # the message that the user sent
                channel = re.findall('PRIVMSG (.*)', message_raw[1])[0].strip()[1:]  # message source channel
                timestamp = LogDate().timestamp
                formatted_message = channel + ' ' + timestamp + ' ' + username + ': ' + message
                return formatted_message
            except IndexError:
                print("INDEX ERROR ON : " + message_raw)

    def add_command(self, command):
        """add a command to the commands list"""
        self.commands[command[0]] = command[1:]
        with open('bot_files/commands.json', 'w') as f:
            json.dump(self.commands, f)
        self.commands = self.get_commands()

    def del_command(self, command):
        """delete a command"""
        if command in self.commands:
            del self.commands[command]
        with open('bot_files/commands.json', 'w') as f:
            json.dump(self.commands, f)
        self.commands = self.get_commands()

    def add_prohib(self, length, phrase):
        """adds a new prohibited phrase to prohibited.json"""
        if re.match('[0-9]+(d|s|m|h)', length):
            self.prohibited[phrase] = length
            with open('bot_files/prohibited.json', 'w') as f:
                json.dump(self.prohibited, f)
            self.prohibited = self.get_prohibited()

    def del_prohib(self, phrase):
        """adds a new prohibited phrase to prohibited.json"""
        if phrase in self.prohibited:
            del self.prohibited[phrase]
            with open('bot_files/prohibited.json', 'w') as f:
                json.dump(self.prohibited, f)
            self.prohibited = self.get_prohibited()

    @staticmethod
    def get_commands():
        """Retrieve a dictionary of command names and functions from command_list.txt"""
        with open('bot_files/commands.json') as f:
            command_dict = json.load(f)
        return command_dict

    @staticmethod
    def get_prohibited():
        """Returns a list of prohibited phrases and their associated timeout times (in minutes)"""
        with open('bot_files/prohibited.json') as f:
            prohibited = json.load(f)
        return prohibited

    @staticmethod
    def log_message(in_message):
        """records the chat message to the appropriate log file"""
        channel = in_message.split(' ')[0]
        message = ' '.join(in_message.split(' ')[1:])
        date = LogDate()
        if not os.path.exists('./local_logs/' + channel):
            os.makedirs('./local_logs/' + channel)
        base = "local_logs/" + channel + "/" + channel + "_"
        file_name = base + date.month + "_" + date.day + "_" + date.year + ".txt"
        with open(file_name, "a", encoding="utf-8") as current_file:
            current_file.write(message + '\n')


class LogDate:

    def __init__(self):
        """Used to create file titles for logs (each chat log file corresponds to a channel and a day),
        Also used to create timestamps for messages and whispers."""
        self.months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                       '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November',
                       '12': 'December'}
        self.date_log = datetime.datetime.now()
        self.date = str(self.date_log).split(" ")[0]
        self.month_num = self.date.split("-")[1]
        self.month = self.months[self.month_num]
        self.day = str(self.date.split("-")[2])
        self.year = str(self.date.split("-")[0])
        self.hour = str(self.date_log.hour)
        self.minute = str(self.date_log.minute)
        self.second = str(self.date_log.second)
        if len(self.second) == 1:
            self.second = "0" + self.second
        self.timestamp = '[' + self.hour + ':' + self.minute + ':' + self.second + ']'
