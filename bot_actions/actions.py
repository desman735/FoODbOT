'''File to describe the interface for action'''
from datetime import timedelta
import re

from discord import ChannelType
from . import functions


# pylint: disable=too-few-public-methods
class ActionInterface:
    '''Interface for async action to execute'''

    def __init__(self):
        self.response_channel = None
        self.client = None

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

    def count_emoji_in_messages(self, message, container):
        '''Called once per message in the range'''
        # print("Message text: \"{}\", timestamp: \"{}\"".format(message.content,message.timestamp))
        message_emoji_pattern = re.compile("(<:?[a-zA-Z]+:?[0-9]+>)")
        emojis_str = message_emoji_pattern.findall(message.content)

        for emoji_str in emojis_str:
            # split -> ['<', 'name', 'id>']
            emoji_id = emoji_str.split(':')[2][:-1]

            # Try to find emoji in server emojis by id
            # Get array of all emojis with parsed id and get first element
            # None (default value) in case nothing is found
            emoji = next((e for e in message.server.emojis if e.id == emoji_id), None)

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

        emoji_dict = dict()
        for channel in self.channels:
            print('Working with', channel)
            await functions.handle_messages(self.client, channel, check_time,
                                            self.count_emoji_in_messages,emoji_dict)

        result = 'Finished!'
        print(result)
        await self.client.edit_message(result_msg, result)
        output = "We found the following emoji:\n"
        #print(self.emoji_dict)
        for k,v in emoji_dict.items():
            output += "emoji: {} {} times.\n".format(k,v)

        await self.client.send_message(self.response_channel,
                                                    output)

    