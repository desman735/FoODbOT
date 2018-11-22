'''File for functions, that implements bot functions'''
from discord import Server
from . import actions


class MessageHandler:
    '''Class to handle commands to the bot'''
    command_character = '!'
    server = None  # should be discord sesrver

    def __init__(self, command_character, server=None):
        '''
        server is discord server
        command_character is a string
        '''
        if isinstance(server, Server):
            self.server = server
            self.command_character = command_character

    def parse_message(self, message) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        print('Message:', message)
        if self.server and message.startswith(self.command_character):
            # todo: return different actions in different cases
            # todo: parse for amount of days. Some other time structure?
            return actions.EmojiCounter(self.server.channels, 7)

        return actions.ActionInterface()  # todo: or None?
