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
        if message.content:
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
            admin_action_dict = {
                "countEmoji": actions.EmojiCounter(message.channel.guild.channels, settings.days_to_count,
                                                   settings.animated_emoji_dict)#,
#                 "animatedEmojis": actions.AnimatedEmojiLister(message, settings.animated_emoji_dict)
            }
            
            general_action_dict = {"help": actions.HelpMessage(message, client, self.command_character,
                                                               settings.admins, settings.days_to_count)}

            if message.content.split(self.command_character)[1].split(" ")[0] in general_action_dict:
                print(message.content.split(self.command_character)[1].split(" ")[0])
                return general_action_dict[message.content.split(self.command_character)[1].split(" ")[0]]
                    
            elif message.content.split(self.command_character)[1].split(" ")[0] in admin_action_dict.keys():
                if str(message.author) in settings.admins or message.author.guild_permissions.administrator:
                    return admin_action_dict[message.content.split(self.command_character)[1].split(" ")[0]]
#             if message.content[1:].startswith("countEmoji"):
#                 return actions.EmojiCounter(message.server.channels,
#                                             settings.days_to_count)

        return actions.ActionInterface()  # todo: or None?

# pylint: enable=too-few-public-methods
