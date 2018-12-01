'''
Created on Nov 30, 2018

@author: kataai

The idea is that these scripts can be called on a new build and can be used to update the setup
'''
import configparser

def load_new_settings_files():
    """A script to set up both settings files"""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if 'Default' in config:
        if not 'commandcharacter' in config['Default']:
            config['Default']['CommandCharacter'] ='!'
        if not 'admins' in config['Default']:
            config['Default']['Admins'] =['Desman735#0679', 'KaTaai#9096']
        if not 'days_to_count' in config['Default']:
            config['Default']['days_to_count'] ='7'
        if not 'characters_limit' in config['Default']:
            config['Default']['characters_limit'] = '2000'
    else:
        config['Default'] = {'CommandCharacter':'!',
                             'Admins': ['Desman735#0679', 'KaTaai#9096'],
                             'days_to_count': '7',
                             'characters_limit':'2000'}

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    mutable_config = configparser.ConfigParser()
    if 'Default' in mutable_config:
        if not 'bottoken' in mutable_config['Default']:
            mutable_config['Default']['BotToken'] = ''
    else:
        mutable_config['Default'] = {'BotToken': ''}
    with open('mutableSettings.ini', 'w') as configfile:
        mutable_config.write(configfile)

if __name__ == '__main__':
    load_new_settings_files()
