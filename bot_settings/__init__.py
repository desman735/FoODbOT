'''Contains set of functions to work with settings'''
import configparser
from . import settings_creator


def update_animated_emoji_list(server_name, emoji_list):
    '''Updates list of animated emojis of the server in config file'''
    mutable_config = configparser.ConfigParser()
    mutable_config.optionxform = str
    mutable_config.read('mutableSettings.ini')
    mutable_config['animated_emojis'][server_name] = str(emoji_list)
    with open('mutableSettings.ini', 'w') as configfile:
        mutable_config.write(configfile)


if __name__ == '__main__':
    settings_creator.load_new_settings_files()
