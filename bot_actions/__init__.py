'''File for functions, that implements bot functions'''

from datetime import datetime
import logging
import discord
from bot_settings import settings
from .functions import get_action_by_command
from . import actions


class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, bot_settings: settings.BotSettings):
        self.bot_settings = bot_settings
        bot_settings.action_dict = {
            "CountEmoji": actions.EmojiCounter,
            "Help": actions.HelpMessage
        }

    def parse_message(self, message: discord.message.Message) -> actions.ActionInterface:
        '''Method that parse command and returns the corresponding action'''
        # ignore empty messages and messages from bots
        if not message.content or message.author.bot:
            return None

        # in case of DM to the bot
        if not message.guild:
            logging.info('(%s) Author: %s, Message ID: %d', datetime.utcnow(),
                         message.author.display_name, message.id)
            logging.warning('Message has no guild. Sending error message back to the author.')
            return actions.SimpleResponse("Sorry, it's not enough food for me in DM!")

        command_character = self.bot_settings.system_settings.command_character

        if not message.content.startswith(command_character):
            # The branch that gets called
            # when there is no command character at the start of a message.
            # Use for tasks that have to check every message.
            return None

        logging.info('(%s) Author: %s, Message ID: %d, Message: %s', datetime.utcnow(),
                     message.author.display_name, message.id, message.content)

        command, arguments = self.extract_command_and_args(message.content)

        # find an action based on keywords from settings
        action, action_settings = get_action_by_command(message.author, command, self.bot_settings)

        if not action:
            return None

        if action not in self.bot_settings.action_dict:
            logging.error("Action '%s' don't have a corresponding action class!", action)
            return None

        action_class = self.bot_settings.action_dict[action]
        return action_class(message, arguments, self.bot_settings, action_settings)

    @staticmethod
    def extract_command_and_args(message: str, separator=' ') -> (str, [str]):
        '''extracts command and argumends from the message based on separator'''
        arguments = message.split(separator)
        # command is the first argument except the first character, which is the command character
        command = arguments[0][1:].lower()
        # remove the command from arguments
        arguments = arguments[1:]
        return command, arguments
