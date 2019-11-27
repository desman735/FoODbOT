'''File for functions, that implements bot functions'''

from datetime import datetime
import discord
from . import actions


# pylint: disable=too-few-public-methods
class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, system_settings):
        self.command_character = system_settings.command_character
        self.admins = system_settings.admins

    def parse_message(self, message, settings) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        if not message.content:
            return None

        author = message.author
        if str(author) in self.admins or author.guild_permissions.administrator:
            print(f'({datetime.utcnow()})',
                  f'Author: {message.author.display_name},',
                  f'Message: {message.content}')

        if not message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is no command character at the start of a message.
            # Use for tasks that have to check every message.
            # self.messageEmojiTester(message)
            return None

        if message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is a command character at the start of a message

            # todo: return different actions in different cases
            # todo: parse for amount of days. Some other time structure?
            days_to_count = int(settings.action_settings['CountEmoji']['days_to_count'])
            command_name = message.content.split(self.command_character, 1)[1].split(" ")[0]
            admin_action_dict = {
                "countEmoji":
                    actions.EmojiCounter(message.guild.channels, days_to_count, message.channel),
                # "animatedEmojis":
                #     actions.AnimatedEmojiLister(message, settings.animated_emoji_dict)
            }

            general_action_dict = {
                "help": actions.HelpMessage(message, self.command_character,
                                            self.admins, days_to_count)}

            if command_name in general_action_dict.keys():
                return general_action_dict[command_name]

            if command_name in admin_action_dict.keys():
                if str(author) in self.admins or author.guild_permissions.administrator:
                    return admin_action_dict[command_name]

        return None

# pylint: enable=too-few-public-methods
