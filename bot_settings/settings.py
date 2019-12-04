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

SystemSettings = namedtuple('SystemSettings', ['token', 'command_character', 'admins'])
GeneralSettings = namedtuple('GeneralSettings', ['characters_limit'])

class BotSettings:
    """
    Settings object, contatins current state of the bot settings and connected files
    Can update state from files or update files to current state
    """

    def __init__(self, config_path: str, mutable_config_path: str, read_on_init=True):
        """
        config_path contains settings, that can be safely shared between few instances of the bot
        mutable_config_path contains settings, that are unique for each instance of the bot
        if read_on_init is False, then settings will be initiated with default values
        """
        self.config_path = config_path
        self.mutable_config_path = mutable_config_path

        # Init fields with default data on the creation
        self.system_settings = SystemSettings('', '!', ['Desman735#0679', 'KaTaai#9096'])
        self.general_settings = GeneralSettings(2000)
        self.action_settings = dict()
        self.action_settings['CountEmoji'] = {'days_to_count': 7}

        # Try to update settings from file
        if read_on_init:
            try:
                self.read_settings()
            except KeyError:
                print("An error occurred while reading the bot settings\n"
                      "Updating missing settings in files to default values")
                self.fix_settings_file()
                self.read_settings()

    def read_settings(self):
        """retrieves the settings from both files"""

        config = configparser.ConfigParser()
        config.read(self.config_path)

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
        mutable_config.read(self.mutable_config_path)

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

    def write_settings(self):
        """Writes current settings to both files, overriding existing settings"""

        # Update immutable settings
        config = configparser.ConfigParser()

        config['System'] = {'command_character': self.system_settings.command_character,
                            'admins': self.system_settings.admins}
        config['General'] = {'characters_limit': self.general_settings.characters_limit}

        for action in self.action_settings:
            config[action] = self.action_settings[action]

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

        # Update mutable settings
        mutable_config = configparser.ConfigParser()
        mutable_config['System'] = {'bot_token': self.system_settings.token}

        with open(self.mutable_config_path, 'w') as configfile:
            mutable_config.write(configfile)

    def fix_settings_file(self):
        """Adds missing fields to the settings files, not overriding the existing ones"""
        self.fix_general_config()
        self.fix_mutable_config()

    def fix_general_config(self):
        """
        Adds missing fields to the immutable config files
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)

        if 'System' in config:
            system = config['System']
            if 'command_character' not in system:
                system['command_character'] = self.system_settings.command_character
            if 'admins' not in system:
                system['admins'] = self.system_settings.admins
        else:
            config['System'] = {'command_character': self.system_settings.command_character,
                                'admins': self.system_settings.admins}

        if 'General' in config:
            if 'characters_limit' not in config['General']:
                config['General']['characters_limit'] = self.general_settings.characters_limit
        else:
            config['General'] = {'characters_limit': self.general_settings.characters_limit}

        for action in self.action_settings:
            if action in config:
                for setup in action:
                    if setup not in config[action]:
                        config[action][setup] = self.action_settings[action][setup]
            else:
                config[action] = self.action_settings[action]

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

    def fix_mutable_config(self):
        """
        A script to update fields of the mutable config file.
        These settings are unique for each instance of the bot and not tracked by git
        """
        config = configparser.ConfigParser()

        # changing default key transformer to keep the case of keys on file update
        # default key transformer changes key values to lowercase
        # removed due to new settings naming convention
        # mutable_config.optionxform = str

        config.read(self.mutable_config_path)

        if 'System' in config:
            if 'bot_token' not in config['System']:
                config['System']['bot_token'] = self.system_settings.token
        else:
            config['System'] = {'bot_token': self.system_settings.token}

        with open(self.mutable_config_path, 'w') as configfile:
            config.write(configfile)
