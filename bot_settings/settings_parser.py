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
import json
from collections import namedtuple
from . import settings_creator

SystemSettings = namedtuple('SystemSettings', ['token', 'command_character', 'admins'])
GeneralSettings = namedtuple('GeneralSettings', ['characters_limit'])

# pylint: disable=too-few-public-methods
class SettingsParser:
    """
    Parses both settings files
    """

    def __init__(self):

        try:
            self.get_settings()
        except KeyError:
            print("An error occurred while loading the bot settings\n"+
                  "Updating settings file")
            settings_creator.update_settings_files()
            self.get_settings()

    def get_settings(self):
        """retrieves the settings from both files"""

        config = configparser.ConfigParser()
        config.read('settings.ini')

        # system settings
        admins = config['System']['admins']
        # configparser saves strings with ' at creation, but json requires ", so we replacing them
        admins = admins.replace("'", '"')
        admins = json.loads(admins)
        command_character = config['System']['command_character']

        # general settings
        characters_limit = int(config['General']['characters_limit'])

        self.action_settings = dict()
        ignored_action_sections = ['System', 'General', 'DEFAULT']

        # action settings
        for section in config:
            if section not in ignored_action_sections:
                self.action_settings[section] = dict(config[section])


        mutable_config = configparser.ConfigParser()
        # changing default key transformer to keep the case of keys on file read
        # default key transformer changes key values to lowercase
        # removed due to new settings naming convention
        # mutable_config.optionxform = str
        mutable_config.read('mutableSettings.ini')

        # system settings
        token = mutable_config['System']['bot_token']

        # action settings
        for section in mutable_config:
            if section not in ignored_action_sections:
                if section in self.action_settings:
                    self.action_settings[section].update(mutable_config[section])
                else:
                    self.action_settings[section] = dict(mutable_config[section])

        # init settings structures
        self.system_settings = SystemSettings(token, command_character, admins)
        self.general_settings = GeneralSettings(characters_limit)


# pylint: enable=too-few-public-methods
