'''
Created on Nov 21, 2018

@author: kataai
The idea is to get info from two sources.
One source is to set up stuff that shouldn't change for example the command string.
The other source contains stuff that benefits from being separate during testing.
-For example the bot token etc.
'''
import configparser

class settingsParser(object):
    """
    Parses both settings files
    """
    
    def __init__(self):
        config=configparser.ConfigParser()
        config.read('settings.ini')
        self.commandCharacter = config['Default']['commandcharacter']
        self.admins = config['Default']['admins']
        
        mutableConfig = configparser.ConfigParser()
        mutableConfig.read('mutableSettings.ini')
        self.botToken = mutableConfig['Default']['Bottoken']
        
def loadNewSettings():
    config=configparser.ConfigParser()
    config['Default'] = {'CommandCharacter':'!',
                         'Admins':['Desman735#0679','KaTaai#9096']}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
     
    mutableConfig=configparser.ConfigParser()
    mutableConfig['Default'] = {'BotToken':''}
    with open('mutableSettings.ini', 'w') as configfile:
        mutableConfig.write(configfile)
