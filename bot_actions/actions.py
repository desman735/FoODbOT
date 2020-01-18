'''File to describe the interface for action and list of actions'''
from datetime import timedelta
import re
import logging

from discord import ChannelType
from discord import errors
from discord import Embed
from discord import Message
from bot_settings import settings
from . import functions


class ActionInterface:
    '''Interface for async action to execute'''

    def __init__(self, message: Message, bot_settings: settings.BotSettings,
                 action_settings: settings.ActionSettings):
        self.action_message = message
        self.bot_settings = bot_settings
        self.action_settings = action_settings

        # create fields, that will be filled later
        self.response_channel = None
        self.client = None

    async def run_action(self):
        '''Method to run async action'''

    def is_called_by_admin(self) -> bool:
        '''Checks, if the running action was initiated by administrator'''
        if self.action_message.author.guild_permissions.administrator:
            return True

        if str(self.action_message.author) in self.bot_settings.system_settings.admins:
            return True

        return False

# pylint: disable=unused-argument
    @staticmethod
    def get_help_message(action_settings: settings.ActionSettings) -> str:
        '''Returns help message for the action'''
        return ''
#pylint: enable=unused-argument


class EmojiCounter(ActionInterface):
    '''Class, that counts emoji usage for a some period of time'''

    @staticmethod
    def get_help_message(action_settings: settings.ActionSettings) -> str:
        days_to_count = action_settings.settings['days_to_count']
        return f'Counts the server emoji used in the last {days_to_count} days.'

    def __init__(self, message: Message, bot_settings: settings.BotSettings,
                 action_settings: settings.ActionSettings):
        super().__init__(message, bot_settings, action_settings)

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
            logging.error('No responce channel to answer')
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


class HelpMessage(ActionInterface):
    """Creates and prints the help message"""

    @staticmethod
    def get_help_message(action_settings: settings.ActionSettings) -> str:
        return "Displays this help message."

    async def run_action(self):
        bot = self.client.user
        message_author = self.action_message.author

        description = (f"{bot.display_name} commands accessible to {message_author.display_name}\n"
                       "All commands are case insensetive")
        embed = Embed(title="Help with FooDBoT commands", description=description)

        for action, action_class in self.bot_settings.action_dict.items():
            action_setup = self.bot_settings.action_settings[action]
            if not action_setup.is_active:
                continue

            keywords = self.get_action_keywords_string(action)
            help_mesage = action_class.get_help_message(action_setup)

            embed.add_field(name=keywords, value=help_mesage)

        await self.response_channel.send(content=None, embed=embed)

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

# pylint: disable=too-few-public-methods, super-init-not-called
class SimpleResponse(ActionInterface):
    """Sending a simple response message back to response channel"""
    def __init__(self, response_message: str):
        self.response = response_message

    async def run_action(self):
        await self.response_channel.send(self.response)
# pylint: enable=too-few-public-methods, super-init-not-called
