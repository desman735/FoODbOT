'''
Created on Nov 30, 2018

@author: kataai

The idea is that these scripts can be called on a new build and \
can be used to update the setup
'''
import configparser


def update_settings_files():
    """A script to set up both settings files"""
    update_config('settings.ini')
    update_mutable_config('mutableSettings.ini')


def update_config(config_file_path: str):
    """
    A script to update fields of the general config file.
    These settings can be safely shared between a few instances of the bot
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)

    if 'System' in config:
        system = config['System']
        if 'command_character' not in system:
            system['command_character'] = '!'
        if 'admins' not in system:
            system['admins'] = ['Desman735#0679', 'KaTaai#9096']
    else:
        config['System'] = {'command_character': '!',
                            'admins': ['Desman735#0679', 'KaTaai#9096']}

    if 'General' in config:
        if 'characters_limit' not in config['General']:
            config['General']['characters_limit'] = 2000
    else:
        config['General'] = {'characters_limit': 2000}

    if 'CountEmoji' in config:
        if 'days_to_count' not in config['CountEmoji']:
            config['CountEmoji']['days_to_count'] = 7
    else:
        config['CountEmoji'] = {'days_to_count': 7}

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

def update_mutable_config(config_file_path: str):
    """
    A script to update fields of the mutable config file.
    These settings are unique for each instance of the bot and not tracked by git
    """
    config = configparser.ConfigParser()

    # changing default key transformer to keep the case of keys on file update
    # default key transformer changes key values to lowercase
    # removed due to new settings naming convention
    # mutable_config.optionxform = str

    config.read(config_file_path)

    if 'System' in config:
        if 'bot_token' not in config['System']:
            config['Default']['bot_token'] = ''
    else:
        config['System'] = {'bot_token': ''}

    with open(config, 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    update_settings_files()
