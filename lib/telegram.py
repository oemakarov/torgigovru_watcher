# encoding=utf8
import requests

class Telegram(object):

    DEFAULT_BOT_TOKEN = '1789291819:AAFUjHmBLd_VnAStcBix9bq0n0J53Ui4L7U'  # @dzin_reminder_bot
    DEFAULT_CHAT_ID = '55562319'  #  @oemakarov

    URL_API_BASE = 'https://api.telegram.org/bot'
    METHOD_SEND_MESSAGE = '/sendMessage'
    METHOD_SEND_DOCUMENT = '/sendDocument'


    emoji = {
    'check_black' : u'\U00002714',
    'check_green' : u'\U00002705',
    'question' : u'\U00002753',
    'double_exclamation_mark' : u'\U0000203C',
    'multiplication' : u'\U00002716',
    'cross_red' : u'\U0000274C',
    'cross_black' : u'\U00002716',
    'warning' : u'\U000026A0',
    'large_red_circle' : u'\U0001F534',
    'arrow_right' : u'\U000027A1',
    'arrow_left' : u'\U00002B05',
    'arrow_up' : u'\U00002B06',
    'squared_up_with_exclamation_mark' : u'\U0001F199',
    'arrow_down' : u'\U00002B07',
    'arrow_refresh' : u'\U0001F504',
    'flag_small' : u'\U0001F6A9', 
    'no_entry' : u'\U0001F6AB', 
    'ok' : u'\U0001F197', 
    'new' : u'\U0001F195', 
    'money_bag' : u'\U0001F4B0',
    'calendar' : u'\U0001F4C5',
    'pushpin' : u'\U0001F4CC',
    'stopwatch' : u'\U000023F1',
    'prohibited' : u'\U0001F6AB',
    'no_entry' : u'\U000026D4',
    'minus' : u'\U00002796',
    'plus' : u'\U00002795',
    'compass' : u'\U0001F9ED',
    'page_facing_up' : u'\U0001F4C4',
    'alarm_clock' : u'\U000023F0',
    'red_circle' : u'\U0001F534',
    'up_pointing_red_triangle' : u'\U0001F53A',
    'red_question' : u'\U00002753',
    'pen' : u'\U0000270F',
    'key' : u'\U0001F511',
    'gear' : u'\U00002699',
    'pill' : u'\U0001F48A',
    'white_medium_star' : u'\U00002B50',
    'eyes' : u'\U0001F440',
    'construction_sign' : u'\U0001F6A7',
    'white_small_square' : u'\U000025AB',
    'man_silhouette' : u'\U0001F464',
    'airplane' : u'\U00002708',
    'left_pointing_magnifying_glass' : u'\U0001F50D',
    'floppy_disk' : u'\U0001F4BE',
    'high_voltage_sign' : u'\U000026A1',
    'globe_with_meridians' : u'\U0001F310',
    }



    def __init__(self, bot_token=None, chat_id=None, proxy=None, parse_mode='Markdown'):
        
        
        # if not bot_token:
        self.bot_token = bot_token or self.DEFAULT_BOT_TOKEN
            
        self.URL_API = self.URL_API_BASE + self.bot_token
        
        if not chat_id:
            self.chat_id = self.DEFAULT_CHAT_ID

        self.session = requests.Session()
        if proxy:
            self.session.proxies.update(proxy)
            self.session.trust_env = False

        self.parse_mode = parse_mode



    def set_chat_id(self, chat_id:str):
        self.chat_id = chat_id  


    def get_chat_id(self):
        return self.chat_id


    def send_message(self, message:str, silent:bool = False, parse_mode=None, chat_id=None):
        # parse_mode = Markdown / HTML
        """
        messageEntityBold => <b>bold</b>, <strong>bold</strong>, **bold**
        messageEntityItalic => <i>italic</i>, <em>italic</em> *italic*
        messageEntityCode => <code>code</code>, `code`
        messageEntityStrike => <s>strike</s>, <strike>strike</strike>, <del>strike</del>, ~~strike~~
        messageEntityUnderline => <u>underline</u>
        messageEntityPre => <pre language="c++">code</pre>,
        """

        data = {
        'chat_id' : chat_id or self.chat_id,
        'parse_mode' : parse_mode if parse_mode else self.parse_mode,
        'text' : str(message),
        }

        # print(data) 

        if silent == True: data.update({'disable_notification' : True})

        r = self.session.get(self.URL_API + self.METHOD_SEND_MESSAGE, data = data)
        return r.json()
    

    def send_document(self, path:str='', file_content:bytes=b'',caption=None, silent=None, parse_mode=None):

        data = {
            'chat_id': self.chat_id,
            'parse_mode' : parse_mode if parse_mode else self.parse_mode,
            }
        if silent == True: data.update({'disable_notification' : True})
        if caption: data.update({'caption' : caption})

        if path and file_content:
            print('@@ERROR - заданы 2 источника ресурса file') 

        if file_content:
            files = {'document': file_content}
            r = self.session.post(self.URL_API + self.METHOD_SEND_DOCUMENT, data=data, files=files)
        elif path:
            with open(path, 'rb') as file_content_import:
                files = {'document': file_content_import}
                r = self.session.post(self.URL_API + self.METHOD_SEND_DOCUMENT, data=data, files=files)

        
        return r.json()


if __name__ == '__main__':
    pass
    # res = 2
    # Telegram().send_message(f'itcom base updated {res = }')
    
    # t = Telegram()
    # ok = t.send_message('123', silent = True)
