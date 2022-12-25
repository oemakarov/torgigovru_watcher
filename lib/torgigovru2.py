# encoding=utf8
# https://torgi.gov.ru/new/public/opendata/reg

__version__ = '0.05'

import json
import logging
import requests
from pathlib import Path
from time import sleep
import warnings
warnings.filterwarnings('ignore')



def save_dict_to_json_file(filename, dict_input):

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dict_input, f, ensure_ascii=False, indent=4)


def dict_value(dict_input:dict, keys:list, default = False):
    """"
    в словаре dict_input проверяет наличие пути с ключами keys, если нашел - выдает результат,
    если не нашел False или значение default

    """

    dict_temp = dict_input
    for key_n in range(0, len(keys)):
        key = keys[key_n]
        if type(dict_temp) == dict and key in dict_temp:
            dict_temp = dict_temp[key]
            if key_n == len(keys)-1:
                return dict_temp
    return default



def save_data_to_file(filename, data_to_write):

    if type(data_to_write) == bytes:
        open_mode = 'wb' # открытие как байтовый файл
    else:
        open_mode = 'w'  # открытие как строковый файл

    with open(filename, open_mode) as f:
        f.write(data_to_write)




class Req():

    def __init__(self, log=None, **kwargs):
        self.log = log or logging.getLogger("request-log")
        self.init_kwargs = kwargs


    def is_response_ok(self, response, url=None):
        if response.status_code != requests.codes.ok :
            self.log.error(f'url response error : {url if url else ""}. error code ={response.status_code}')
            return False 
        else:
            return True 


    def get(self, url, **kwargs):
        r = requests.get(url, **{**self.init_kwargs, **kwargs})

        if self.is_response_ok(r, url):
            return r
        else:
            return None
        

    def post(self, url, **kwargs):
        r = requests.post(url, **{**self.init_kwargs, **kwargs})
        if self.is_response_ok(r, url):
            return r
        else:
            return None




class TorgiGovRu():

    URL_NOTICE_META = 'https://torgi.gov.ru/new/opendata/7710568760-notice/meta.json'
    
    def __init__(self):
        self.log = logging.getLogger("torgigovru-new")
        self.req = Req(log=self.log, verify=False)
    

    def get_meta(self):

        r_text = self.req.get(self.URL_NOTICE_META).text
        return json.loads(r_text)


    def get_meta_day_info(self, day_index:int):

        def create_date(notice_item:dict):
            return notice_item['created'][:8] + notice_item['created'][9:]    

        meta = self.get_meta()
        # save_dict_to_json_file('meta.json', meta)  #
        
        if not meta.get('data'):
            self.log.warning('error: no field "data" in meta')
            return
        return sorted(meta['data'], key=create_date)[day_index]


    def get_meta_lastday_info(self):
        return self.get_meta_day_info(-1)


    def get_day_notice_list(self, day_index:int):

        day_info = self.get_meta_day_info(day_index)
        # print(day_info['provenance']) 

        list_objects = json.loads(self.req.get(url=day_info['source']).text).get('listObjects', [])
        notice_list = list(filter(lambda x: x.get('documentType') == 'notice', list_objects))
        return notice_list


    def get_lastday_notice_list(self):
        return self.get_day_notice_list(day_index=-1)

        # lastday = self.get_meta_lastday_info()
        # list_objects = json.loads(self.req.get(url=lastday['source']).text)['listObjects']
        # notice_list = list(filter(lambda x: x.get('documentType') == 'notice', list_objects))

        # return notice_list




class Notification():
    """Извещение с портала torgi.gov.ru"""

    URL_FILESTORE_IMAGE = "https://torgi.gov.ru/new/file-store/v1/"

    def __init__(self, notification_url=None):
        self.log = logging.getLogger("notification_new")
        self.req = Req(self.log, verify=False)
        self.notification_url = notification_url

    def info(self, notification_url=None):

        if notification_url:
            self.notification_url = notification_url

        result = self.req.get(self.notification_url)
        if result:
            r_text = self.req.get(self.notification_url).text
            return json.loads(r_text)
        else:
            return None




    def attachment_content(self, content_id:str=None, url:str=None, **kwargs):
        FILENAME_MAX_LENGTH = 100


        if content_id:
            url = self.URL_FILESTORE_IMAGE + content_id

        response = self.req.get(url, **kwargs)
        filename_content = requests.utils.unquote(
            list(
                filter(lambda x: x.startswith('filename'), response.headers.get('Content-Disposition','').split('; '))
                )[0].split('\'\'')[1]
            )

        fc = Path(filename_content)
        if response.content:
            return ''.join([fc.stem[:FILENAME_MAX_LENGTH], fc.suffix]), response.content
        else:
            return None, None


    def attachment_content_save(self, content_id:str=None, url:str=None, filename=None, path=None, **kwargs):

        filename_content, content = self.attachment_content(content_id, url, **kwargs)

        filename = filename or filename_content
        if path: 
            filename = path + filename

        if content:
            with open(filename, 'wb') as f:
                f.write(content)
            return True, filename
        else:
            return False, None

# class Dict2(dict):
#     # https://stackoverflow.com/a/3405143/190597
#     def __missing__(self, key):
#         value = self[key] = type(self)()
#         return value




if __name__ == '__main__':
    pass

    # torgi = TorgiGovRu()

    # day_notice_list = torgi.get_day_notice_list(day_index=-1)
    # print('day_notice_list LEN = ', len(day_notice_list)) 
    # save_dict_to_json_file('day_notice_list.json', day_notice_list)
    # # url = day_notice_list[8]['href']

    # for day_item in day_notice_list:
    #     url = day_item['href']
    #     path_url = url.split('/')[-1].split('.')[0] + '\\'

    #     # Path(cwd / path_url).mkdir(exist_ok=True)

    #     n = Notification(url)
    #     ni = n.info()
    #     notice = ni['exportObject']['structuredObject']['notice']
    #     save_dict_to_json_file('export.json', ni)

    #     print(notice['commonInfo']['href']) 
    #     print(notice['commonInfo']['biddType']['name']) 
    #     print(notice['commonInfo']['procedureName']) 
        
    #     print('biddEndTime =', notice['biddConditions']['biddEndTime']) 
    #     for lot in notice['lots']:
    #         print('ЛОТ №', lot['lotNumber']) 
    #         print(' '*3, 'lotName =', lot['lotName']) 
    #         print(' '*3, 'lotDescription =', lot['lotDescription']) 
    #         print(' '*3, 'priceMin =', lot.get('priceMin')) 
    #         print(' '*3, 'priceStep =', lot.get('priceStep')) 
    #         print(' '*3, 'deposit =', lot.get('deposit'))
    #         print(' '*3, 'estateAddress =', lot.get('biddingObjectInfo',{}).get('estateAddress'))
            
            
    #         for characteristic in lot.get('biddingObjectInfo',{}).get('characteristics', []):
    #             print(' '*7, characteristic.get('name'), '=', characteristic.get('characteristicValue'))


    #         for attachment in lot['imageIds']:
    #             ok, filename = n.attachment_content_save(content_id=attachment['id'])
    #             if ok: print('OK - filename =', filename) 
    #         print('-'*20) 
    #     sleep(15)
    #     print('*'*40) 












        





   