'''File for functions, that implements bot functions'''

from datetime import datetime
import discord
from . import actions


# pylint: disable=too-few-public-methods
class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, command_character):
        '''
        command_character is a string
        '''
        self.command_character = command_character

    def parse_message(self, message, settings,client) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        if message.content and not message.author == client.user.name:
            print(f'({datetime.utcnow()}) Author: {message.author.display_name}, Message: {message.content}')
        if not message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is no command character at the start of a message.
            # Use for tasks that have to check every message.
            # self.messageEmojiTester(message)
            pass

        if message.content.startswith(self.command_character):
            # The branch that gets called
            # when there is a command character at the start of a message

            # todo: return different actions in different cases
            # todo: parse for amount of days. Some other time structure?
            command_name = message.content.split(self.command_character,1)[1].split(" ")[0]
            admin_action_dict = {
                "countEmoji": actions.EmojiCounter(message.guild.channels, settings.days_to_count, message.channel)
#                 "animatedEmojis": actions.AnimatedEmojiLister(message, settings.animated_emoji_dict)
            }

            general_action_dict = {"help": actions.HelpMessage(message, self.command_character,
                                                               settings.admins, settings.days_to_count)}

            if command_name in general_action_dict:
                return general_action_dict[command_name]

            elif command_name in admin_action_dict.keys():
                if str(message.author) in settings.admins or message.author.guild_permissions.administrator:
                    return admin_action_dict[command_name]

        return actions.ActionInterface()

# pylint: enable=too-few-public-methods
