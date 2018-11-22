'''File to describe the interface for action'''
from discord import ChannelType


# pylint: disable=too-few-public-methods
class ActionInterface:
    '''Interface for async action to execute'''
    response_channel = None
    client = None

    async def run_action(self):
        '''Method to run async action'''
        pass


class EmojiCounter(ActionInterface):
    '''Class, that counts emoji usage for a some period of time'''
    channels = []  # Should be Discord.py channels
    days = 7

    def __init__(self, channels, days):
        for channel in channels:
            if channel.type == ChannelType.text:  # filter channels by type
                self.channels.append(channel)
        self.days = days

    async def run_action(self):
        '''Method to run async action'''
        if not self.response_channel or not self.client:
            print('No client or responce channel to answer')
            return

        response = "Channels:"
        for channel in self.channels:
            response = response + " " + channel.name

        await self.client.send_message(self.response_channel, response)

# pylint: enable=too-few-public-methods
