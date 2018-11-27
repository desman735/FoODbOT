'''File for functions, that implements bot functions'''

from discord import Server
from . import actions


class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, command_character, server=None):
        '''
        server is discord server
        command_character is a string
        '''
        self.server = server
        self.command_character = command_character

    def parse_message(self, message, settings) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        print('Message:', message.content)
        if self.server:
            """The branch that gets called when there is no command character at the start of a message.
               Use for tasks that have to check every message."""
            #self.messageEmojiTester(message)

        if self.server and message.content.startswith(self.command_character):
            """The branche that gets called when there is a command character at the start."""
            # todo: return different actions in different cases
            # todo: parse for amount of days. Some other time structure?
            return actions.EmojiCounter(self.server.channels, 
                                        settings.days_to_count)

        return actions.ActionInterface()  # todo: or None?

#     def messageEmojiTester(self, message):
#         """Looks for custom emoji, and prints some info about it to the command line"""
#         messageEmojiPattern = re.compile("(<:?[a-zA-Z]+:?[0-9]+>)")
#         result=messageEmojiPattern.findall(message.content)
#         if result:
#             for r in result:
#                 print("emoji found: {}, sent in server: {}, in channel: {}, by: {}".format(r,message.server, message.channel,message.author))
