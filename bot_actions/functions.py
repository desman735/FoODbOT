'''File, that contains helper functions for bot'''
import logging
from datetime import datetime
from discord import User
from bot_settings.settings import ActionSettings, SystemSettings, BotSettings

async def handle_messages(client, channel, check_time, handler, container):
    '''
    Runs handler on every message from channel between start_time and stop_time
    '''
    start = datetime.utcnow()
    start_time = start
    stop_time = start - check_time
    id_list = []
    while start_time > stop_time:
        is_empty = True  # if there is any messages between start and stop
        # todo: look for a better way to check it

        async for msg in channel.history(limit=None, before=start,
                                         after=stop_time):
            is_empty = False
            start = msg
            start_time = msg.created_at
            if start_time > stop_time and msg.id not in id_list:  # todo: should it be checked?
                id_list.append(msg.id)
                handler(msg, container, client.user.id)  # container =
            else:
                break  # found message after stop_time

        if is_empty:
            break  # no more messages to check between start and stop


def get_action_by_command(author: User, command: str, bot_settings: BotSettings) \
    -> (str, ActionSettings):
    '''
    Returns action as a string or None if command is not available.
    If action is not available, logs why.
    '''
    result_action = None

    for action, setup in bot_settings.action_settings.items():
        # setup must contains keywords fields based on settings code
        if command in setup.keywords:
            result_action = action
            break

    if not result_action:
        logging.error("Can't find action for command '%s'!", command)
        return None, None

    result_action_settings = bot_settings.action_settings[result_action]

    if not result_action_settings.is_active:
        logging.info("Called action '%s' is not active", result_action)
        return None, None

    if not is_action_allowed(author, result_action_settings, bot_settings.system_settings):
        logging.info("Called action '%s' is forbidden for user '%s'", result_action,
                     author.display_name)
        return None, None

    return result_action, result_action_settings

def is_action_allowed(user: User, action_settings: ActionSettings, system_settings: SystemSettings)\
    -> bool:
    '''
    Checks, if the user is allowed to use an action.
    User will be allowed to use action if they are in the whitelist and not in the blacklist.
    Admins are allowed to use any actions.
    '''

    if user.guild_permissions.administrator:
        return True

    if str(user) in system_settings.admins:
        return True

    userspaces = [str(user)]
    for role in user.roles:
        userspaces.append(str(role))

    is_in_whitelist = False
    # Empty whitelist means everyone is in whitelist
    if action_settings.call_whitelist:
        for userspace in userspaces:
            if userspace in action_settings.call_whitelist:
                is_in_whitelist = True
                break
    else:
        is_in_whitelist = True

    is_in_blacklist = False
    # Empty blacklist means noone is in blacklist
    for userspace in userspaces:
        if userspace in action_settings.call_blacklist:
            is_in_blacklist = True
            break

    return is_in_whitelist and not is_in_blacklist
