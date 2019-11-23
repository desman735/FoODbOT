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
            print("An error occurred while loading the animated_emoji_dict\n"+
                  "Updating animated_emoji_dict file")
            settings_creator.load_new_settings_files()
            self.get_settings()

    def get_settings(self):
        """retrieves the settings from both files"""

        config = configparser.ConfigParser()
        config.read('settings.ini')

        # system settings
        # todo: parse admins
        admins = config['System']['admins']
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
        # todo: check, what is this for and update a comment
        mutable_config.optionxform = str
        mutable_config.read('mutableSettings.ini')

        # system settings
        token = mutable_config['System']['bottoken']

        # action settings
        for section in mutable_config:
            if section not in ignored_action_sections:
                if section in self.action_settings:
                    self.action_settings[section].update(mutable_config[section])
                else:
                    self.action_settings[section] = config[section]

        # init settings structures
        self.system_settings = SystemSettings(token, command_character, admins)
        self.general_settings = GeneralSettings(characters_limit)


# pylint: enable=too-few-public-methods
