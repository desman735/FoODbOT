'''
Created on Nov 30, 2018

@author: kataai

The idea is that these scripts can be called on a new build and \
can be used to update the setup
'''
import configparser


def load_new_settings_files():
    """A script to set up both settings files"""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if 'Default' in config:
        if 'commandcharacter' not in config['Default']:
            config['Default']['CommandCharacter'] = '!'
        if 'admins' not in config['Default']:
            config['Default']['Admins'] = ['Desman735#0679', 'KaTaai#9096']
        if 'days_to_count' not in config['Default']:
            config['Default']['days_to_count'] = '7'
        if 'characters_limit' not in config['Default']:
            config['Default']['characters_limit'] = '2000'
    else:
        config['Default'] = {'CommandCharacter': '!',
                             'Admins': ['Desman735#0679', 'KaTaai#9096'],
                             'days_to_count': '7',
                             'characters_limit': '2000'}

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    mutable_config = configparser.ConfigParser()
    if 'Default' in mutable_config:
        if 'bottoken' not in mutable_config['Default']:
            mutable_config['Default']['BotToken'] = ''
    else:
        mutable_config['Default'] = {'BotToken': ''}

    mutable_config.optionxform = str
    if 'animated_emoji' in mutable_config:
        pass
    else:
        mutable_config['animated-emoji'] = {"Stand Still Stay Silent":
                                            [":tuuriahhumm:", ":sooffended:"],
                                            "SSSSDev": [':465993384570650634:']
                                            }
    with open('mutableSettings.ini', 'w') as configfile:
        mutable_config.write(configfile)

    if 'animated_emoji_list' not in mutable_config:
        mutable_config['animated_emoji_list'] = dict()

if __name__ == '__main__':
    load_new_settings_files()
