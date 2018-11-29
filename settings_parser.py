'''
Created on Nov 21, 2018

@author: kataai
The idea is to get info from two sources.
One source is to set up stuff that shouldn't change
(for example the command character)
The other source contains stuff that benefits from being separate
(for example the bot token etc.)
'''
import configparser


# pylint: disable=too-few-public-methods
class SettingsParser:
    """
    Parses both settings files
    """

    def __init__(self):
        self.days_to_count = 7
        self.characters_limit = 2000

        config = configparser.ConfigParser()
        config.read('settings.ini')

        # required settings
        self.command_character = config['Default']['commandcharacter']
        self.admins = config['Default']['admins']

        # optional settings
        if 'days_to_count' in config['Default']:
            self.days_to_count = int(config['Default']['days_to_count'])
        if 'charaters_limit' in config['Default']:
            self.characters_limit = int(config['Default']['charaters_limit'])

        mutable_config = configparser.ConfigParser()
        mutable_config.read('mutableSettings.ini')
        self.bot_token = mutable_config['Default']['Bottoken']
# pylint: enable=too-few-public-methods


def load_new_settings():
    """A script to set up both settings files"""
    config = configparser.ConfigParser()
    config['Default'] = {'CommandCharacter': '!',
                         'Admins': ['Desman735#0679', 'KaTaai#9096'],
                         'days_to_count': '7'}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    mutable_config = configparser.ConfigParser()
    mutable_config['Default'] = {'BotToken': ''}
    with open('mutableSettings.ini', 'w') as configfile:
        mutable_config.write(configfile)
