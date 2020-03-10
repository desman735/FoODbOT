'''
Created on Nov 30, 2018

@author: kataai

The idea is that these scripts can be called on a new build and \
can be used to update the setup
'''
from . import settings

def update_settings_files():
    """
    Creates instance of settings with default values and adds missing ones
    """
    default_settings = settings.BotSettings('settings.ini', 'mutableSettings.ini', False)
    default_settings.fix_settings_file()

if __name__ == '__main__':
    update_settings_files()
