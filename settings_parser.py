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
import SettingsCreator


# pylint: disable=too-few-public-methods
class SettingsParser:
    """
    Parses both settings files
    """

    def __init__(self):

        try:
            self.get_settings()
        except KeyError:
            print("An error occurred while loading the settings\n"+
                  "Updating settings file")
            SettingsCreator.load_new_settings_files()
            self.get_settings()

    def get_settings(self):
        """retrieves the settings from both files"""
        config = configparser.ConfigParser()
        config.read('settings.ini')

        # required settings
        self.command_character = config['Default']['commandcharacter']
        self.admins = config['Default']['admins']

        self.days_to_count = int(config['Default']['days_to_count'])
        self.characters_limit = int(config['Default']['characters_limit'])

        mutable_config = configparser.ConfigParser()
        mutable_config.read('mutableSettings.ini')
        self.bot_token = mutable_config['Default']['Bottoken']

# pylint: enable=too-few-public-methods
