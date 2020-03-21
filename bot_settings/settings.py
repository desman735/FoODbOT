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
import logging
import json
from collections import namedtuple

SystemSettings = namedtuple('SystemSettings', ['token', 'command_character', 'admins',
                                               'characters_limit', 'log_level'])
ActionSettings = namedtuple('ActionSettings', ['is_active', 'keywords', 'call_whitelist',
                                               'call_blacklist', 'settings'])

class BotSettings:
    """
    Settings object, contains current state of the bot settings and connected files
    Can update state from files or update files to current state
    """

    def __init__(self, config_path: str, mutable_config_path: str, read_on_init=True):
        """
        config_path contains settings, that can be safely shared between few instances of the bot
        mutable_config_path contains settings, that are unique for each instance of the bot
        if read_on_init is False, then settings will be initiated with default values
        """
        # Will be filled later to avoid cyclic import (on init of the message handler)
        self.action_dict = {}

        self.config_path = config_path
        self.mutable_config_path = mutable_config_path

        # Init fields with default data on the creation
        self.system_settings = SystemSettings('', '!', ['Desman735#0679', 'KaTaai#9096'], 2000, 20)
        self.action_settings = dict()
        self.action_settings['CountEmoji'] = ActionSettings(True, ['CountEmoji', 'StatEmoji'],
                                                            [], [], {'days_to_count': 7})
        self.action_settings['Help'] = ActionSettings(True, ['help'], [], [], {})

        # Try to update settings from file
        if read_on_init:
            try:
                self.read_settings()
            except KeyError:
                logging.error("An error occurred while reading the bot settings. "
                              "Updating missing settings in files to default values")
                self.fix_settings_file()
                self.read_settings()

    def read_settings(self):
        """retrieves the settings from both files"""

        config = configparser.ConfigParser()
        config.read(self.config_path)

        # system settings
        admins = self.convert_string_to_array(config['System']['admins'])
        command_character = config['System']['command_character']
        characters_limit = int(config['System']['characters_limit'])
        log_level = int(config['System']['log_level'])
        logging.getLogger().setLevel(log_level)

        ignored_action_sections = ['System', 'DEFAULT']
        self.read_action_settings(config, ignored_action_sections)

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
        self.system_settings = SystemSettings(token, command_character, admins, characters_limit,
                                              log_level)

    def read_action_settings(self, config: configparser.ConfigParser, ignored_sections: [str]):
        """reads from config settings for custom actions"""
        self.action_settings = dict()

        ignored_section_fields = ['is_active', 'keywords', 'call_whitelist', 'call_blacklist']

        # action settings
        for section in config:
            if section in ignored_sections:
                continue

            is_active = True
            if 'is_active' in config[section]:
                is_active = json.loads(config[section]['is_active'].lower())
            else:
                message = f'Action {section} not contains is_active field! '
                message = message + 'Action will be enabled by default'
                logging.warning(message)

            keywords = []
            if 'keywords' in config[section]:
                keywords = BotSettings.convert_string_to_array(config[section]['keywords'])
                # lowercase all keywords, they are case-insensitive
                keywords = list(map(str.lower, keywords))
            else:
                message = f'Action {section} not contains keywords setup! '
                message = message + 'Action name will be used as a keyword'
                logging.warning(message)
                keywords = [section.lower()]

            whitelist = []
            if 'call_whitelist' in config[section]:
                whitelist = BotSettings.convert_string_to_array(config[section]['call_whitelist'])
            else:
                message = f'Action {section} not contains call whitelist! '
                message = message + 'Action is allowed to everyone except the blacklist'
                logging.warning(message)

            blacklist = []
            if 'call_blacklist' in config[section]:
                blacklist = BotSettings.convert_string_to_array(config[section]['call_blacklist'])
            else:
                message = f'Action {section} not contains call blacklist! '
                message = message + 'Nobody is banned from using an action'
                logging.warning(message)

            settings = {}
            for field in config[section]:
                if field in ignored_section_fields:
                    continue
                settings[field] = config[section][field]

            self.action_settings[section] = ActionSettings(is_active, keywords, whitelist,
                                                           blacklist, settings)
            logging.info('Add action %s to possible actions', section)


    def write_settings(self):
        """Writes current settings to both files, overriding existing settings"""

        # Update immutable settings
        config = configparser.ConfigParser()

        config['System'] = {'command_character': self.system_settings.command_character,
                            'admins': self.system_settings.admins,
                            'characters_limit': self.system_settings.characters_limit,
                            'log_level': self.system_settings.log_level}

        for action, action_setup in self.action_settings.items():
            if action_setup.settings:
                config[action] = action_setup.settings
            else:
                config[action] = {}
            config[action]['keywords'] = str(action_setup.keywords)
            config[action]['is_active'] = str(action_setup.is_active)
            config[action]['call_whitelist'] = str(action_setup.call_whitelist)
            config[action]['call_blacklist'] = str(action_setup.call_blacklist)

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

        self.update_system_settings(config)
        self.update_actions_settings(config)

        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

    def update_system_settings(self, config: configparser.ConfigParser):
        """Updates system settings section of the config file"""
        if 'System' in config:
            system = config['System']
            if 'command_character' not in system:
                system['command_character'] = str(self.system_settings.command_character)
            if 'admins' not in system:
                system['admins'] = str(self.system_settings.admins)
            if 'characters_limit' not in system:
                system['characters_limit'] = str(self.system_settings.characters_limit)
            if 'log_level' not in system:
                system['log_level'] = str(self.system_settings.log_level)
        else:
            config['System'] = {'command_character': self.system_settings.command_character,
                                'admins': self.system_settings.admins,
                                'characters_limit': self.system_settings.characters_limit,
                                'log_level': self.system_settings.log_level}

    def update_actions_settings(self, config: configparser.ConfigParser):
        """Updates actions settings sections of the config file"""
        for action, action_setup in self.action_settings.items():
            if action in config:
                if 'keywords' not in config[action]:
                    config[action]['keywords'] = str(action_setup.keywords)
                if 'is_active' not in config[action]:
                    config[action]['is_active'] = str(action_setup.is_active)
                if 'call_whitelist' not in config[action]:
                    config[action]['call_whitelist'] = str(action_setup.call_whitelist)
                if 'call_blacklist' not in config[action]:
                    config[action]['call_blacklist'] = str(action_setup.call_blacklist)
                for setup in action_setup.settings:
                    if setup not in config[action]:
                        config[action][setup] = str(action_setup.settings[setup])
            else:
                if action_setup.settings:
                    config[action] = action_setup.settings
                else:
                    config[action] = {}
                config[action]['keywords'] = str(action_setup.keywords)
                config[action]['is_active'] = str(action_setup.is_active)
                config[action]['call_whitelist'] = str(action_setup.call_whitelist)
                config[action]['call_blacklist'] = str(action_setup.call_blacklist)

    def fix_mutable_config(self):
        """
        A script to update fields of the mutable config file.
        These settings are unique for each instance of the bot and not tracked by git
        """
        config = configparser.ConfigParser()

        # changing default key transformer to save the case of key value on the file update
        # default key transformer changes key to lowercase
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

    @staticmethod
    def convert_string_to_array(array_str: str) -> [str]:
        """Takes an array string read from settings file and converts it to the array"""
        # configparser saves strings with ' at creation, but json requires ", so we replacing them
        array_str = array_str.replace("'", '"')
        return json.loads(array_str)
