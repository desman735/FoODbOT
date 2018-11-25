'''File to describe the interface for action'''
from datetime import timedelta
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

    def handle_message(self, message):
        '''Updates object according to the passed message'''
        #todo: make it
        pass

    async def run_action(self):
        '''Method to run async action'''
        if not self.response_channel or not self.client:
            print('No client or responce channel to answer')
            return

        result = 'Counting emojis, do not disturb...'
        print(result)
        result_msg = await self.client.send_message(self.response_channel,
                                                    result)

        check_time = timedelta(days=self.days_to_count)

        for channel in self.channels:
            print('Working with', channel)
            await functions.handle_messages(self.client, channel, check_time,
                                            self.handle_message)

        result = 'Finished!'
        print(result)
        await self.client.edit_message(result_msg, result)
