'''File for functions, that implements bot functions'''

from discord import Server
from . import actions


# pylint: disable=too-few-public-methods
class MessageHandler:
    '''Class to handle commands to the bot'''

    def __init__(self, command_character):
        '''
        command_character is a string
        '''
        self.command_character = command_character

    def parse_message(self, message, settings) -> actions.ActionInterface:
        '''Method that parse command and returns corresponding method'''
        print('Message:', message.content)
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
            print(settings.days_to_count)
            action_dict={"countEmoji":actions.EmojiCounter(message.server.channels,
                                            settings.days_to_count,settings.animated_emoji_dict)
            }
            if message.content[1:].split(" ")[0] in action_dict.keys():
                return action_dict[message.content[1:].split(" ")[0]]
#             if message.content[1:].startswith("countEmoji"):
#                 return actions.EmojiCounter(message.server.channels,
#                                             settings.days_to_count)

        return actions.ActionInterface()  # todo: or None?

    # def message_emoji_tester(self, message):
    #     """
    #     Looks for custom emoji, and prints some info about it
    #     to the command line
    #     """
    #     message_emoji_pattern = re.compile("(<:?[a-zA-Z]+:?[0-9]+>)")
    #     result = message_emoji_pattern.findall(message.content)
    #     if result:
    #         for res in result:
    #             print("emoji found: {}, sent in server: {}, in channel: {}, \
    #                 by: {}".format(res, message.server,
    #                                message.channel, message.author))

# pylint: enable=too-few-public-methods
