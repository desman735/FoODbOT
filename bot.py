"""Script to start the FoODbOT"""
from datetime import datetime
from discord import Client
from bot_settings import settings_parser
from bot_actions import MessageHandler


SETTINGS = settings_parser.SettingsParser()
CLIENT = Client()
HANDLER = MessageHandler(SETTINGS.command_character)

# todo: check emoji group before counting
# todo: admins by roles


@CLIENT.event
async def on_ready():
    '''Runs on the bot start'''
    print('FoODbOT started as a', CLIENT.user.name, 'at', datetime.utcnow())
    print('Bot ID is', CLIENT.user.id)
    print('------')


@CLIENT.event
async def on_message(message):
    '''Runs at receiving the message'''
    if not HANDLER:
        print('Error! No message handler found!')
        return

#     if str(message.author) in SETTINGS.admins or \
#             message.author.guild_permissions.administrator:
#         await message.channel.send("Hi")
    action = HANDLER.parse_message(message, SETTINGS, CLIENT)
    action.client = CLIENT
    action.response_channel = message.channel
    action.characters_limit = SETTINGS.characters_limit
    await action.run_action()
#
#
# @CLIENT.event
# async def on_reaction_add(reaction, user):
#     '''Runs on adding a reaction to any message'''
#     if reaction.custom_emoji:
#         print("name: {}, id: {}, user: {}, server: {}, channel: {}, \
#         adding: True".format(reaction.emoji.name, reaction.emoji.id,
#                              user, reaction.message.server,
#                              reaction.message.channel))
#     else:
#         print("emoji: {}".format(reaction.emoji))
#
#
# @CLIENT.event
# async def on_reaction_remove(reaction, user):
#     '''Runs on removing a reaction from any message'''
#     if reaction.custom_emoji:
#         print("name: {}, id: {}, user: {}, server: {}, channel: {}, \
#         adding: False".format(reaction.emoji.name, reaction.emoji.id,
#                               user, reaction.message.server,
#                               reaction.message.channel))
#     else:
#         print("emoji: {}".format(reaction.emoji))
#
CLIENT.run(SETTINGS.bot_token)
