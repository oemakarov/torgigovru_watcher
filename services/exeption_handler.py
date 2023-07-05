from lib.telegram import Telegram
import sys
from telebot.apihelper import ApiTelegramException

import config
from __version__ import __version__
from lib.db_sqlite import del_all_user_searches

from init import log


def telebot_exception_handler(user_id: str, e: ApiTelegramException):
    if e.description == config.BOT_ERRORS['BLOCKED_BY_USER']:
        del_all_user_searches(user_id, log)
        raise e  # выходим для перезагрузки пользовательских растроек после удаления
    else:
        log.error(f'{user_id = }\n{e.description}')


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    if exctype != SystemExit:
        error_text = '\nКритическая ошибка.\n\nERROR : ' + str(value) + '\n' + str(traceback.tb_frame) + '\nline no : ' + str(traceback.tb_lineno)
        error_text_caption = f'{config.log_name} v{__version__}\n`{error_text}`'
        telegram = Telegram()
        telegram.send_message(error_text_caption)
    sys.exit(1)