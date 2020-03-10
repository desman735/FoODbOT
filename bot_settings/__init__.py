'''Inits settings files if run as main'''
from . import settings_creator

if __name__ == '__main__':
    settings_creator.update_settings_files()
