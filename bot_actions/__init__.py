'''File for functions, that implements bot functions'''

from datetime import datetime
import logging
import discord
from bot_settings import settings
from . import actions


# pylint: disable=too-few-public-methods
class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, bot_settings: settings.BotSettings):
        self.bot_settings = bot_settings
        bot_settings.action_dict = {
            "CountEmoji": actions.EmojiCounter,
            "Help": actions.HelpMessage
        }

    def parse_message(self, message: discord.message.Message) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
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
            # self.messageEmojiTester(message)
            return None

        # early return in case when message not starts with command character
        # no need for additional check

        # if message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is a command character at the start of a message

        logging.info('(%s) Author: %s, Message ID: %d, Message: %s', datetime.utcnow(),
                     message.author.display_name, message.id, message.content)

        command = str(message.content.split(command_character, 1)[1].split(" ")[0]).lower()

        # find an action based on keywords from settings
        action, action_settings = self.get_action_by_command(message, command)

        if not action:
            return None

        action_class = self.bot_settings.action_dict[action]
        return action_class(message, self.bot_settings, action_settings)

    def get_action_by_command(self, message: discord.message.Message, command: str) \
        -> (str, settings.ActionSettings):
        '''
        Returns action as a string or None if command is not available.
        If action is not available, logs why.
        '''
        result_action = None

        for action, setup in self.bot_settings.action_settings.items():
            # setup must contains keywords fields based on settings code
            if command in setup.keywords:
                result_action = action
                break

        if not result_action:
            logging.error("Can't find action for command '%s'!", command)
            return None, None

        result_action_settings = self.bot_settings.action_settings[result_action]

        if not result_action_settings.is_active:
            logging.info("Called action '%s' is not active", result_action)
            return None, None

        if not self.is_action_allowed(result_action_settings, message.author):
            logging.info("Called action '%s' is forbidden for user '%s'", result_action,
                         message.author.display_name)
            return None, None

        return result_action, result_action_settings

    def is_action_allowed(self, action_settings: settings.ActionSettings, user: discord.User) \
        -> bool:
        '''
        Checks, if the user is allowed to use an action.
        User will be allowed to use action if they are in the whitelist and not in the blacklist.
        Admins are allowed to use any actions.
        '''

        if user.guild_permissions.administrator:
            return True

        if str(user) in self.bot_settings.system_settings.admins:
            return True

        userspaces = [str(user)]
        for role in user.roles:
            userspaces.append(str(role))

        is_in_whitelist = False
        # Empty whitelist means everyone is in whitelist
        if action_settings.call_whitelist:
            for userspace in userspaces:
                if userspace in action_settings.call_whitelist:
                    is_in_whitelist = True
                    break
        else:
            is_in_whitelist = True

        is_in_blacklist = False
        # Empty blacklist means noone is in blacklist
        for userspace in userspaces:
            if userspace in action_settings.call_blacklist:
                is_in_blacklist = True
                break

        return is_in_whitelist and not is_in_blacklist

# pylint: enable=too-few-public-methods
