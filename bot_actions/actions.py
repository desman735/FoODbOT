'''File to describe the interface for action and list of actions'''
from datetime import timedelta
import re

from discord import ChannelType
from discord import errors
from discord import Embed
from bot_settings import update_animated_emoji_list
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

    def __init__(self, channels, days_to_count, response_channel):
        super().__init__()
        self.channels = []  # Should be Discord.py channels
        self.days_to_count = None
        self.response_channel = response_channel

        for channel in channels:
            if channel.type == ChannelType.text:  # filter channels by type
                self.channels.append(channel)

        self.days_to_count = days_to_count

    @staticmethod
    def get_server_emoji_dict(server):
        '''returns the dictionary <emoji: 0> with all emojis from the server'''
        result = dict()
        for emoji in server.emojis:
            if not emoji.animated:
                result[emoji] = 0

        return result

    @staticmethod
    def count_emoji_in_messages(message, container, bot_id):
        '''Counts the number of static server emoji in the text of the message and in the reactions.
           Ignores messages sent by the bot.
        '''

        if not message.author.id == bot_id:
            message_emoji_pattern = re.compile("(<:?[a-zA-Z0-9]+:?[0-9]+>)")
            emojis_str = message_emoji_pattern.findall(message.content)
            print(message.content)
            for emoji_str in emojis_str:
                # split -> ['<', 'name', 'id>']
                emoji_id = emoji_str.split(':')[2][:-1]

                search_container = dict()
                for k in container.keys():
                    search_container[k.id] = k

                if int(emoji_id) in search_container.keys():
                    container[search_container[int(emoji_id)]] += 1

            if message.reactions:
                for reaction in message.reactions:
                    if reaction.custom_emoji and \
                            reaction.emoji in container.keys():
                        container[reaction.emoji] += reaction.count

    async def run_action(self):
        '''Should be called once per bot request'''
        if not self.response_channel:# or not self.client:
            print('No responce channel to answer')
            return

        result = f'Counting emojis for the last {self.days_to_count} day(s), do not disturb...'
        print(result)
        result_msg = await self.response_channel.send(result)

        check_time = timedelta(days=self.days_to_count)

        emoji_dict = self.get_server_emoji_dict(self.response_channel.guild)
        async with self.response_channel.typing():
            for channel in self.channels:
                print('Working with', channel)
                try:
                    await functions.handle_messages(self.client, channel,
                                                    check_time,
                                                    self.count_emoji_in_messages,
                                                    emoji_dict)
                except errors.Forbidden:
                    print(f"We have no access to {channel}")
            print('Finished!')
            output = f"We found the following emojis in the last {self.days_to_count} day(s):\n"
            await result_msg.edit(content = output)

        output = ""
        # To change the sorting order, add reverse=True to the sorted()

        emojis = list(emoji_dict.items())  # [(emoji, amout)]
        # sort by amount, in increasing order
        emojis.sort(key=lambda emoji_tuple: emoji_tuple[1], reverse=False)

        for emoji, amount in emojis:
            line = f"Emoji {emoji} was used {amount} times.\n"

            # Send message, if line will be too long after concat
            if len(output) + len(line) > self.characters_limit:
                await self.response_channel.send(output)
                output = ""

            output += line

        # Send what's left after cycle
        if output:
            output += 'The end!'
            await self.response_channel.send(output)


# pylint: disable=too-few-public-methods
class AnimatedEmojiLister(ActionInterface):
    '''Class that collects the animated emoji'''

    def __init__(self, message, animated_emoji_dict):
        super().__init__()
        self.message = message
        self.animated_emoji_dict = animated_emoji_dict

    async def run_action(self):
        '''Method to run async action'''
        if self.message.server.name not in self.animated_emoji_dict.keys():
            self.animated_emoji_dict[self.message.server.name] = []

        message_words = self.message.content.split(" ")
        animated_emojis = self.animated_emoji_dict[self.message.server.name]

        if len(message_words) >= 2:
            print(self.message.content+"\n" + message_words[1])
            if message_words[1] == "add":
                for emoji in message_words[2:]:
                    if emoji not in animated_emojis:
                        animated_emojis.append(emoji)
                update_animated_emoji_list(self.message.server.name, animated_emojis)
                await self.client.send_message(self.message.channel, "Added to the list")

            elif message_words[1] == "remove":
                for emoji in message_words[2:]:
                    if emoji in animated_emojis:
                        animated_emojis.remove(emoji)
                update_animated_emoji_list(self.message.server.name, animated_emojis)
                await self.client.send_message(self.message.channel, "Removed from the list")

            elif message_words[1] == "print":
                print("Hi")
                if animated_emojis:
                    result = "The following emoji are marked as animated\n"
                    for emoji in animated_emojis:
                        print(emoji)
                        result += "{}\n".format(emoji)
                    await self.client.send_message(self.message.channel,
                                                   result)
            else:
                print("Animated emojis: No command given")
# pylint: enable=too-few-public-methods

# pylint: disable=too-few-public-methods
class HelpMessage(ActionInterface):
    """Creates and prints the help message"""
    def __init__(self, message, command_character, admins,days_to_count):
        super().__init__()
        self.message = message
        self.command_character = command_character
        self.admins = admins
        self.days_to_count = days_to_count

    async def run_action(self):
        embed = Embed(title = "Help with FooDBoT commands",
                      description = f"{self.client.user.name} commands accessible to {self.message.author.display_name}")
        embed.add_field(name=f"{self.command_character}help", value = "Displays this help message.")
        if str(self.message.author) in self.admins or self.message.author.guild_permissions.administrator:
            embed.add_field(name=f"{self.command_character}countEmoji",
                            value = f"Counts the server emoji used in the last {self.days_to_count} days.")
        await self.message.channel.send(content=None,embed=embed)
# pylint: enable=too-few-public-methods
