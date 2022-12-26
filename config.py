from pathlib import Path
import secret

sqlite_db_filename = Path('data', 'data.db')
sqlite_db_users_filename = Path('user_data', 'user_data.db')

log_name = 'torgigovru_watcher'
log_filename = Path('log', 'run.log')
log_format = '[%(asctime)s.%(msecs)03d]:%(lineno)d [%(levelname)s] (%(filename)s).%(funcName)s - %(message)s'
_log_format_debug = '[%(asctime)s.%(msecs)03d]:%(lineno)d [%(levelname)s] (%(filename)s).%(funcName)s - %(message)s'
_log_format_debug_file = '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s'
_log_format_print = '|%(lineno)d| %(filename)s - %(funcName)s - %(message)s'
datefmt='%Y-%m-%d %H:%M:%S'

admin_user_id = '55562319'

DAYS_DEEP_NOTICE_WATCH= 8

BOT_TOKEN = secret.BOT_TOKEN
TELEGRAM_MESSAGE_LIMIT = 4000 # длина сообщения в телеграм
TELEGRAM_MESSAGE_CAPTION_LIMIT = 1000 #длина описания для картинки в телеграм
TELEGRAM_MESSAGE_DELAY = .1 #задержка после отправки сообщения в телегу, чтобы не напороться на антифлуд

IMG_SIZE_LIMIT = 20_000_000  # изображения до ~20Mb, размером больше не будут обрабатываться для уменьшения
IMG_MAX_SIZE_XY = 10_000 # сумма сторон до которой уменьшается изображение 

PROCESS_NOTICE_DELAY = 1 # задержка перед обработкой следующего извещения
PROCESS_LOT_DELAY = 1 # задержка перед обработкой следующего лота
EOL = '\n'

DEBUG_PASS_ALL_NOTICE = True  # тестовый режим обработки всех извещений
DEBUG_PASS_ALL_NOTICE = False # рабочий режим

# 'москва+авто'
# '*частьслова*+обособленноеслово+@92'
