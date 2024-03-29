from lib.telegram import Telegram
import sys
from telebot.apihelper import ApiTelegramException
from time import sleep

import config
from __version__ import __version__
from lib.db_sqlite import del_all_user_searches

from init import log


def telebot_exception_handler(user_id: str, e: ApiTelegramException):
    if e.description == config.BOT_ERRORS['BLOCKED_BY_USER']: 
        del_all_user_searches(user_id, log)
        log.info('***** DEL_ALL_USER_SEARCHES')
        exit(1) # выходим для перезагрузки пользовательских растроек после удаления
    elif config.BOT_ERRORS['USER_BLOCKED'] in e.description:
        del_all_user_searches(user_id, log)
        log.info('***** DEL_ALL_USER_SEARCHES')
        exit(1) # выходим для перезагрузки пользовательских растроек после удаления

    elif e.description.startswith(config.BOT_ERRORS['FLOOD_CONTROL']):
        delay = e.description.replace(config.BOT_ERRORS['FLOOD_CONTROL'], '')
        log.info(f'FLOOD CONTROL. sleep {delay}')
        sleep(int(delay))


    else:
        log.error(f'{user_id = }\n{e.description}')


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    if exctype != SystemExit:
        error_text = '\nКритическая ошибка.\n\nERROR : ' + str(value) + '\n' + str(traceback.tb_frame) + '\nline no : ' + str(traceback.tb_lineno)
        error_text_caption = f'{config.log_name} v{__version__}\n`{error_text}`'
        telegram = Telegram(bot_token=config.BOT_TOKEN, chat_id=config.ADMIN_USER_ID)
        telegram.send_message(error_text_caption)
    sys.exit(1)