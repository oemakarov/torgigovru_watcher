from pathlib import Path
import secret

sqlite_db_filename = Path('data', 'data.db')
sqlite_db_users_filename = Path('user_data', 'user_data.db')

log_filename = Path('log', 'run.log')
log_format = '[%(asctime)s.%(msecs)03d]:%(lineno)d [%(levelname)s] (%(filename)s).%(funcName)s - %(message)s'
_log_format_debug = '[%(asctime)s.%(msecs)03d]:%(lineno)d [%(levelname)s] (%(filename)s).%(funcName)s - %(message)s'
_log_format_debug_file = '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s'
_log_format_print = '|%(lineno)d| %(filename)s - %(funcName)s - %(message)s'
datefmt='%Y-%m-%d %H:%M:%S'
# log_datefmt = '%H:%M:%S'

admin_user_id = '55562319'

DAYS_DEEP_NOTICE_WATCH= 8

BOT_TOKEN = secret.BOT_TOKEN
TELEGRAM_MESSAGE_LIMIT = 4000 # длина сообщения в телеграм
TELEGRAM_MESSAGE_CAPTION_LIMIT = 900 #длина описания для картинки в телеграм
IMG_SIZE_LIMIT = 20000000  # изображения до 20Mb, размером больше не будут обрабатываться для уменьшения
IMG_MAX_SIZE_XY = 10000 # сумма сторон до которой уменьшается изображение 
PROCESS_NOTICE_DELAY = 1 # задержка перед обработкой следующего извещения
PROCESS_LOT_DELAY = 1 # задержка перед обработкой следующего лота
EOL = '\n'

DEBUG_PASS_ALL_NOTICE = True
DEBUG_PASS_ALL_NOTICE = False

users = {
    # 55562319 : [
    # 'севастополь',
    # ],


    55562319 : [
    '@92',
    '@77+lexus+*202*',
    ],

    -1001303355596 : [
    '@91'
    ],
}

# 'москва+авто'
# '*частьслова*+обособленноеслово+@92'