import lib.app_logger_watcher as app_logger
from lib.torgigovru2 import Notification, TorgiGovRu
from telebot import TeleBot
import config


log = app_logger.get_logger(config.log_name)
torgi = TorgiGovRu()
n = Notification()
bot=TeleBot(config.BOT_TOKEN, parse_mode=config.DEFAULT_PARSE_MODE)