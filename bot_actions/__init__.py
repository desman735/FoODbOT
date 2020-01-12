'''File for functions, that implements bot functions'''

from datetime import datetime
import logging
import discord
from bot_settings import settings
from . import actions


# pylint: disable=too-few-public-methods
class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, system_settings: settings.SystemSettings):
        self.system_settings = system_settings
        self.action_dict = {
            "CountEmoji": actions.EmojiCounter,
            "Help": actions.HelpMessage
        }

    def parse_message(self, message: discord.message.Message,
                      bot_settings: settings.BotSettings) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        # ignore empty messages and messages from bots
        if not message.content or message.author.bot:
            return None

        if not message.guild:
            print(f'Message with id {message.id} has no guild (probably, DM to the bot).',
                  'Sending error message back to the author.')
            return actions.SimpleResponse("Sorry, it's not enough food for me in DM!")

        command_character = self.system_settings.command_character

        if not message.content.startswith(command_character):
            # The branch that gets called
            # when there is no command character at the start of a message.
            # Use for tasks that have to check every message.
            # self.messageEmojiTester(message)
            return None

        # early return in case when message not starts with command character
        # no need for additional check

        # if message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is a command character at the start of a message

        print(f'({datetime.utcnow()})',
              f'Author: {message.author.display_name},',
              f'Message ID: {message.id}',
              f'Message: {message.content}')

        command = str(message.content.split(command_character, 1)[1].split(" ")[0]).lower()

        # find an action based on keywords from settings
        result_action = None
        for action, setup in bot_settings.action_settings.items():
            # setup must contains keywords fields based on settings code
            if command in setup.keywords:
                result_action = action
                break

        if not result_action:
            logging.error("Can't find action for command %s!", command)
            return None

        action_class = self.action_dict[result_action]
        return action_class(message, bot_settings, bot_settings.action_settings[result_action])

# pylint: enable=too-few-public-methods
