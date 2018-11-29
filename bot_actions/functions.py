'''File, that contains helper functions for bot'''
from datetime import datetime

async def handle_messages(client, channel, check_time, handler, container):
    '''
    Runs handler on every message from channel between start_time and stop_time
    '''
    start = datetime.utcnow()
    start_time = start
    stop_time = start - check_time

    while start_time > stop_time:
        is_empty = True  # if there is any messages between start and stop
        # todo: look for a better way to check it

        async for msg in client.logs_from(channel, before=start,
                                          after=stop_time):
            is_empty = False
            start = msg
            start_time = msg.timestamp
            if start_time > stop_time:  # todo: should it be checked?
                handler(msg, container)  # container =
            else:
                break  # found message after stop_time

        if is_empty:
            break  # no more messages to check between start and stop
