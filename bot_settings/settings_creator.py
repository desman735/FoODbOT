'''
Created on Nov 30, 2018

@author: kataai

The idea is that these scripts can be called on a new build and \
can be used to update the setup
'''
import configparser


def update_settings_files():
    """A script to set up both settings files"""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    
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

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    mutable_config = configparser.ConfigParser()
    # changing default key transformer to keep the case of keys on file update
    # default key transformer changes key values to lowercase
    # removed due to new settings naming convention
    # mutable_config.optionxform = str
    mutable_config.read('mutableSettings.ini')

    if 'System' in mutable_config:
        if 'bot_token' not in mutable_config['System']:
            mutable_config['Default']['bot_token'] = ''
    else:
        mutable_config['System'] = {'bot_token': ''}

    with open('mutableSettings.ini', 'w') as configfile:
        mutable_config.write(configfile)

if __name__ == '__main__':
    update_settings_files()
