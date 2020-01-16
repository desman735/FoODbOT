"""Script to start the FoODbOT"""
from datetime import datetime
import logging
from discord import Client
from bot_settings import settings
from bot_actions import MessageHandler


SETTINGS = settings.BotSettings('settings.ini', 'mutableSettings.ini')
CLIENT = Client()
HANDLER = MessageHandler(SETTINGS.system_settings)

# todo: check emoji group before counting
# todo: admins by roles


@CLIENT.event
async def on_ready():
    '''Runs on the bot start'''
    logging.info('FoODbOT started as a %s, at %s', CLIENT.user.name, datetime.utcnow())
    logging.info('Bot ID is %d', CLIENT.user.id)
    print('------')


@CLIENT.event
async def on_message(message):
    '''Runs at receiving the message'''
    if not HANDLER:
        logging.error('Error! No message handler found!')
        return

#     if str(message.author) in SETTINGS.admins or \
#             message.author.guild_permissions.administrator:
#         await message.channel.send("Hi")
    action = HANDLER.parse_message(message, SETTINGS)
    if not action:
        return

    action.client = CLIENT
    action.response_channel = message.channel
    logging.info('Running action %s', action)
    await action.run_action()
    logging.info('Action %s finished', action)
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
CLIENT.run(SETTINGS.system_settings.token)
