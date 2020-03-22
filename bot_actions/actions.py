'''File to describe the interface for action and list of actions'''
from datetime import timedelta, datetime
import re
import logging

from discord import ChannelType, errors, Embed, Message
from bot_settings.settings import BotSettings, ActionSettings
from . import functions, time_utils


class ActionInterface:
    '''Interface for async action to execute'''

    def __init__(self, message: Message, arguments: [str], bot_settings: BotSettings,
                 action_settings: ActionSettings):
        self.action_message = message
        self.action_arguments = arguments
        self.bot_settings = bot_settings
        self.action_settings = action_settings

        # create fields, that will be filled later
        self.response_channel = None
        self.client = None

    async def run_action(self):
        '''Method to run async action'''
        logging.warning('Default run_action method is not overriden!')

# pylint: disable=unused-argument
    @staticmethod
    def get_help_message(action_settings: ActionSettings) -> str:
        '''Returns help message for the action'''
        return 'No help message'

    @staticmethod
    def get_detailed_help_message(action_settings: ActionSettings, arguments: [str]) -> str:
        '''Returns detailed help message for the action'''
        return 'No detailed help message'
#pylint: enable=unused-argument


class EmojiCounter(ActionInterface):
    '''Class, that counts emoji usage for a some period of time'''

    @staticmethod
    def get_help_message(action_settings: ActionSettings) -> str:
        days_to_count = action_settings.settings['days_to_count']
        return f'Counts the server emoji used in the last {days_to_count} days.'

    @staticmethod
    def get_detailed_help_message(action_settings: ActionSettings, arguments: [str]) -> str:
        return "One perfect day you'll be able to pass amount of days as argument, but not now"

    def __init__(self, message: Message, arguments: [str], bot_settings: BotSettings,
                 action_settings: ActionSettings):
        super().__init__(message, arguments, bot_settings, action_settings)

        self.days_to_count = int(self.action_settings.settings['days_to_count'])
        self.channels = []

        guild_channels = self.action_message.guild.channels
        for channel in guild_channels:
            if channel.type == ChannelType.text:  # filter channels by type
                self.channels.append(channel)

    @staticmethod
    def get_server_emoji_dict(server):
        '''returns the dictionary <emoji: 0> with all emojis from the server'''
        result = dict()
        for emoji in server.emojis:
            if not emoji.animated:
                result[emoji] = 0

        return result

    @staticmethod
    def count_emoji_in_messages(message, container, bot_id):
        '''Counts the number of static server emoji in the text of the message and in the reactions.
           Ignores messages sent by the bot.
        '''

        if not message.author.id == bot_id:
            message_emoji_pattern = re.compile("(<:?[a-zA-Z0-9]+:?[0-9]+>)")
            emojis_str = message_emoji_pattern.findall(message.content)
            for emoji_str in emojis_str:
                # split -> ['<', 'name', 'id>']
                emoji_id = emoji_str.split(':')[2][:-1]

                search_container = dict()
                for k in container.keys():
                    search_container[k.id] = k

                if int(emoji_id) in search_container.keys():
                    container[search_container[int(emoji_id)]] += 1

        if message.reactions:
            for reaction in message.reactions:
                if reaction.custom_emoji and \
                        reaction.emoji in container.keys():
                    container[reaction.emoji] += reaction.count

    async def run_action(self):
        '''Should be called once per bot request'''
        if not self.response_channel:# or not self.client:
            logging.error('No response channel to answer')
            return

        result = f'Counting emojis for the last {self.days_to_count} day(s), do not disturb...'
        logging.info(result)
        result_msg = await self.response_channel.send(result)

        check_time = timedelta(days=self.days_to_count)

        emoji_dict = self.get_server_emoji_dict(self.response_channel.guild)
        async with self.response_channel.typing():
            for channel in self.channels:
                logging.info('Working with %s', channel)
                try:
                    await functions.handle_messages(self.client, channel,
                                                    check_time,
                                                    self.count_emoji_in_messages,
                                                    emoji_dict)
                except errors.Forbidden:
                    logging.warning("We have no access to %s", channel)
            logging.info('Finished!')
            output = f"We found the following emojis in the last {self.days_to_count} day(s):\n"
            await result_msg.edit(content=output)

        output = ""
        # To change the sorting order, add reverse=True to the sorted()

        emojis = list(emoji_dict.items())  # [(emoji, amout)]
        # sort by amount, in increasing order
        emojis.sort(key=lambda emoji_tuple: emoji_tuple[1], reverse=False)

        for emoji, amount in emojis:
            line = f"Emoji {emoji} was used {amount} times.\n"

            # Send message, if line will be too long after concat
            if len(output) + len(line) > self.bot_settings.system_settings.characters_limit:
                await self.response_channel.send(output)
                output = ""

            output += line

        # Send what's left after cycle
        if output:
            output += 'The end!'
            await self.response_channel.send(output)


class ConvertTime(ActionInterface):
    '''Action to convert time between timezones'''

    @staticmethod
    def get_help_message(action_settings: ActionSettings) -> str:
        return "Converts time between timezones.\n"
            # "Use as '!convert time timezone_from timezone_to' " # +\
            # "(for example '!convert 9:15 AM CST GMT+3')\n" +\
            # "Time supports both 12h and 24h formats\n" +\
            # "Use abbreviation or UTC offset to specify timezones.\n" +\
            # "Take into account that some timezones are sharing one abbreviation. " +\
            # "It's better to use UTC offset, if you know it"

    async def run_action(self):
        respond = self.response_channel.send
        if len(self.action_arguments) < 3:
            await respond('Not enough arguments.\n'
                          'Command is used as "!convert time timezone_from timezone_to"')
            return

        timezone_to = self.action_arguments[-1]
        timezone_from = self.action_arguments[-2]
        time = ' '.join(self.action_arguments[0:-2])

        try:
            time = time_utils.get_datetime_from_strtime(time)
        except ValueError:
            await respond(f"Can't parse '{time}' time. Is it valid?")
            return

        # using current day to avoid problems with dates less than starting one
        time = datetime.utcnow().replace(hour=time.hour, minute=time.minute)

        try:
            timezone_from = time_utils.get_timezone_from_abbr(timezone_from)
        except KeyError as error:
            await respond(f"Can't find timezone {error}")
            return

        except ValueError as error:
            await respond(f"Can't parse '{timezone_from}' timezone. Is it valid?")
            return

        try:
            timezone_to = time_utils.get_timezone_from_abbr(timezone_to)
        except KeyError as error:
            await respond(f"Can't find timezone {error}")
            return
        except ValueError:
            await respond(f"Can't parse '{timezone_to}' timezone. Is it valid?")
            return

        time_utc = time - timezone_from.utcoffset(None)
        result_time = time_utc + timezone_to.utcoffset(None)

        await respond(f'{result_time:%H:%M} (from {timezone_from} to {timezone_to})')



class HelpMessage(ActionInterface):
    """Creates and prints the help message"""

    @staticmethod
    def get_help_message(action_settings: ActionSettings) -> str:
        return "Displays this help message."

    @staticmethod
    def get_detailed_help_message(action_settings: ActionSettings, arguments: [str]) -> str:
        return "Displays detailed help message for the command. You're on the right way!"

    async def run_action(self):
        if self.action_arguments:
            command = self.action_arguments[0]
            arguments = self.action_arguments[1:]
            embed = self.make_command_help_message(command, arguments)
            if embed:
                await self.response_channel.send(content=None, embed=embed)
            else:
                await self.response_channel.send(f"Can't find help for '{command}'")
        else:
            embed = self.make_general_help_message()
            await self.response_channel.send(content=None, embed=embed)

    def make_general_help_message(self) -> Embed:
        '''Creates embeded help message with short help for each command'''
        bot = self.client.user
        message_author = self.action_message.author

        description = (f"{bot.display_name} commands accessible to {message_author.display_name}\n"
                       "All commands are case insensetive")
        embed = Embed(title="Help with FooDBoT commands", description=description)

        for action, action_class in self.bot_settings.action_dict.items():
            action_setup = self.bot_settings.action_settings[action]
            if not action_setup.is_active:
                continue

            action_allowed = functions.is_action_allowed(message_author, action_setup,
                                                         self.bot_settings.system_settings)
            if not action_allowed:
                continue

            keywords = self.get_action_keywords_string(action)
            help_mesage = action_class.get_help_message(action_setup)

            embed.add_field(name=keywords, value=help_mesage)

        return embed

    def make_command_help_message(self, command: str, arguments: [str]) -> Embed:
        '''Creates embeded help message with detailed help for exact command'''
        message_author = self.action_message.author
        
        # if command is disabled or not available for this user, action will be None
        action, action_settings = functions.get_action_by_command(message_author, command,
                                                                  self.bot_settings)

        if action is None:
            return None
        if action not in self.bot_settings.action_dict:
            logging.warning("Action %s don't have a corresponding action class!", action)
            return None

        action_class = self.bot_settings.action_dict[action]

        title = f"Help with '{command}'"
        description = f"{action_class.get_help_message(action_settings)}\n\n" +\
                      f"{action_class.get_detailed_help_message(action_settings, arguments)}"

        return Embed(title=title, description=description)

    def get_action_keywords_string(self, action_name: str) -> str:
        '''
        Returns human-readable string of all keywords for the action
        Output format is '!keyword1 or !keyword2 or ...'
        '''
        command_character = self.bot_settings.system_settings.command_character
        keywords = self.bot_settings.action_settings[action_name].keywords
        result = ''

        for keyword in keywords:
            if result:
                result = result + ' or '
            result = result + command_character + keyword

        return result

# pylint: disable=too-few-public-methods
class SimpleResponse(ActionInterface):
    """Sending a simple response message back to response channel"""
    def __init__(self, response_message: str):
        super().__init__(None, None, None, None)
        self.response = response_message

    async def run_action(self):
        await self.response_channel.send(self.response)
# pylint: enable=too-few-public-methods
