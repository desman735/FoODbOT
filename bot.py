"""Script to start the FoODbOT"""
from discord import Client
from Settingsparser import settingsParser
from bot_actions import MessageHandler

PARSER = settingsParser()
CLIENT = Client()
HANDLER = MessageHandler(PARSER.commandCharacter)


@CLIENT.event
async def on_ready():
    '''Runs on the bot start'''
    print('FoODbOT started as a', CLIENT.user.name)
    print('Bot ID is', CLIENT.user.id)
    print('------')
    if CLIENT.servers:
        HANDLER.server = list(CLIENT.servers)[0]
    else:
        print('Error! Not found any servers!')


@CLIENT.event
async def on_message(message):
    '''Runs at receiving the message'''
    if not HANDLER:
        print('Error! No message handler found!')
        return
    full_name = message.author.name + '#' + message.author.discriminator
    if full_name in PARSER.admins:
        action = HANDLER.parse_message(message.content)
        action.client = CLIENT
        action.response_channel = message.channel
        await action.run_action()

CLIENT.run(PARSER.botToken)
