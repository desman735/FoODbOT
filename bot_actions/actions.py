'''File to describe the interface for action and list of actions'''
from datetime import timedelta
import re

from discord import ChannelType
from discord import errors
from . import functions


# pylint: disable=too-few-public-methods
class ActionInterface:
    '''Interface for async action to execute'''

    def __init__(self):
        self.response_channel = None
        self.client = None
        self.characters_limit = 1000  # just in case

    async def run_action(self):
        '''Method to run async action'''
        pass
# pylint: enable=too-few-public-methods


class EmojiCounter(ActionInterface):
    '''Class, that counts emoji usage for a some period of time'''

    def __init__(self, channels, days_to_count):
        super().__init__()
        self.channels = []  # Should be Discord.py channels
        self.days_to_count = None

        for channel in channels:
            if channel.type == ChannelType.text:  # filter channels by type
                self.channels.append(channel)

        self.days_to_count = days_to_count

    @staticmethod
    def get_server_emoji_dict(server):
        '''returns the dictionary <emoji: 0> with all emojis from the server'''
        result = dict()
        for emoji in server.emojis:
            result[emoji] = 0

        return result

    @staticmethod
    def count_emoji_in_messages(message, container):
        '''Called once per message in the range'''
        # print("Message text: \"{}\", \
        #       timestamp: \"{}\"".format(message.content, message.timestamp))
        message_emoji_pattern = re.compile("(<:?[a-zA-Z0-9]+:?[0-9]+>)")
        emojis_str = message_emoji_pattern.findall(message.content)

        for emoji_str in emojis_str:
            # split -> ['<', 'name', 'id>']
            emoji_id = emoji_str.split(':')[2][:-1]

            # Try to find emoji in server emojis by id
            # Get array of all emojis with parsed id and get first element
            # None (default value) in case nothing is found
            emoji = next((e for e in
                          message.server.emojis if e.id == emoji_id),
                         None)

            # todo: maybe, it's better to:
            # 1) cache all server emoji on action start
            # 2) use something like if emoji_str in str(message.server.emojis)

            if emoji:
                if emoji in container.keys():
                    container[emoji] += 1
                else:
                    container[emoji] = 1
                # add to the container

        if message.reactions:
            for reaction in message.reactions:
                if reaction.custom_emoji:
                    if reaction.emoji in container.keys():
                        container[reaction.emoji] += reaction.count
                    else:
                        container[reaction.emoji] = reaction.count

    async def run_action(self):
        '''Should be called once per bot request'''
        if not self.response_channel or not self.client:
            print('No client or responce channel to answer')
            return

        result = 'Counting emojis, do not disturb...'
        print(result)
        result_msg = await self.client.send_message(self.response_channel,
                                                    result)

        check_time = timedelta(days=self.days_to_count)

        emoji_dict = self.get_server_emoji_dict(self.response_channel.server)

        for channel in self.channels:
            print('Working with', channel)
            try:
                await functions.handle_messages(self.client, channel, check_time,
                                                self.count_emoji_in_messages,
                                                emoji_dict)
            except errors.Forbidden:
                print("We have no access to {}".format(channel))
        print('Finished!')
        output = "We found the following emojis:\n"
        await self.client.edit_message(result_msg, output)

        output = ""
        # To change the sorting order, add reverse=True to the sorted()

        emojis = list(emoji_dict.items())  # [(emoji, amout)]
        # sort by amount, in increasing order
        emojis.sort(key=lambda emoji_tuple: emoji_tuple[1], reverse=False)

        for emoji, amount in emojis:
            line = "Emoji {} was used {} times.\n".format(emoji, amount)

            # Send message, if line will be too long after concat
            if len(output) + len(line) > self.characters_limit:
                output += "Whew..."
                await self.client.send_message(self.response_channel,
                                               output)
                output = ""

            output += line

        # Send what's left after cycle
        if output:
            output += 'The end!'
            await self.client.send_message(self.response_channel,
                                           output)
