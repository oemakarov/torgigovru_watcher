# encoding=utf8
from datetime import datetime
from time import sleep
import sys
from telebot import TeleBot
from telebot.types import InputMediaPhoto
import warnings
warnings.filterwarnings('ignore')

import config
import lib.app_logger_watcher as app_logger
import lib.db_sqlite as sql
from lib.torgigovru2 import Notification, TorgiGovRu
from lib.telegram import Telegram
from lib.tools import (
    users_prepare_sql,
    # users_prepare_sql,
    # search_pattern_prepare,
    # search_pattern_prepare_one,
    # is_any_regex_in_str,
    is_all_regex_in_str,
    attachment_id_name,
    del_file_attachment_id_name,
    close_tags,
    cut_len,
    money_format,
    elem,
    large_img_resize,
    # save_dict_to_json_file,
    getget,
    getget_str,
    fields_to_dict_from_list,
)


__version__ = '0.13'
# 'москва+авто'
# '*частьслова*+обособленноеслово+@92'


# ------
# v0.13
# - вывод количества месяцев аренды lot_contract_months

# v0.12
# - рефакторинг кода, вынес глубину дней анализа извещений в конфиг


# ------


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    if exctype != SystemExit:
        error_text = '\nКритическая ошибка.\n\nERROR : ' + str(value) + '\n' + str(traceback.tb_frame) + '\nline no : ' + str(traceback.tb_lineno)
        error_text_caption = f'torgi gov ru watcher\n`{error_text}`'
        telegram = Telegram()
        telegram.send_message(error_text_caption)
    sys.exit(1)


def process_notification(notification_obj:Notification, notice_info:dict, bot:TeleBot, chat_id:int):

    # save_dict_to_json_file('notification.json', notice_info)
    notice = notice_info['exportObject']['structuredObject']['notice']
    notice_number = notice['commonInfo']['noticeNumber']
    log.info(f'{notice_number = }') 

    bidd_type_name = notice['commonInfo']['biddType']['name']
    procedure_name = notice['commonInfo']['procedureName']
    bidd_end_time = notice["biddConditions"]["biddEndTime"][:10]
    href = notice['commonInfo']['href']
    
    for lot in notice.get('lots'):
        sleep(config.PROCESS_LOT_DELAY)

        lot_number = lot.get("lotNumber")
        log.info(f'лот - {lot_number}') 
        lot_name = lot.get("lotName")
        lot_description = lot.get("lotDescription")

        if lot_name == lot_description:
            lot_description = ''
        if lot_name == procedure_name:
            procedure_name = ''

        # breakpoint()
        lot_address_subject_code = getget(lot, 'biddingObjectInfo', 'subjectRF', 'code')
        lot_address_subject_name = getget(lot, 'biddingObjectInfo', 'subjectRF', 'name')
        lot_estate_address = getget(lot, 'biddingObjectInfo', 'estateAddress')
        lot_price_min = lot.get("priceMin")
        lot_price_step = lot.get("priceStep")
        lot_deposit = lot.get("deposit")


        print(f'{lot_address_subject_code =}') 
        print(f'{lot_address_subject_name =}') 
            
        lot_characteristics = ''
        for lot_characteristic in lot.get('biddingObjectInfo',{}).get('characteristics', []):
            if isinstance(lot_characteristic, dict):
                lot_characteristic_name = lot_characteristic.get('name')
                if isinstance(lot_characteristic.get('characteristicValue'), dict):
                    lot_characteristic_value = str(getget(lot_characteristic, 'characteristicValue', 'name'))
                elif isinstance(lot_characteristic.get('characteristicValue'), list):
                    lot_characteristic_value = str(lot_characteristic.get('characteristicValue')[0].get('name'))
                else:
                    lot_characteristic_value = str(lot_characteristic.get('characteristicValue'))
                lot_characteristics += elem(element=lot_characteristic_value, text=lot_characteristic_name, emoji='white_small_square') 

        lot_additional_details = fields_to_dict_from_list(lot.get('additionalDetails',[]))
        lot_additional_details_keys = ['DA_contractYears', 'DA_yearlyPrice', 'DA_monthlyPricePerSqMeter', 'DA_contractType'] + \
        ['DA_depositRecipient', 'DA_isDepositSpecified', 'DA_inquiryRules', 'DA_limitations', 'DA_intendedUse', 'DA_paymentOrder', 'DA_monthlyPrice']

        lot_contract_type = getget(lot_additional_details, 'DA_contractType', 'value', 'name')
        lot_contract_years = getget(lot_additional_details, 'DA_contractYears', 'value')
        lot_contract_months = getget(lot_additional_details, 'DA_contractMonths', 'value')
        lot_yearly_price = getget_str(lot_additional_details, 'DA_yearlyPrice', 'value')
        lot_monthly_price = getget_str(lot_additional_details, 'DA_monthlyPrice', 'value')
        lot_payment_order = getget_str(lot_additional_details, 'DA_paymentOrder', 'value')

        lot_price_min_elem = elem(money_format(lot_price_min), text='Цена', emoji='money_bag')
        lot_yearly_price_elem = elem(money_format(lot_yearly_price), text='Аренда в год', emoji='money_bag')
        lot_monthly_price_elem = elem(money_format(lot_monthly_price), text='Аренда в мес', emoji='money_bag')
        lot_monthly_price_per_sq_meter = getget(lot_additional_details, 'DA_monthlyPricePerSqMeter', 'value')

        # for k,v in lot_additional_details.items():
        #     if k not in lot_additional_details_keys:
        #         print(f'=== {k}') 
        #         print(f'    {v.get("name")} = {v.get("value")}') 


        lot_price_elem = lot_monthly_price_elem or lot_yearly_price_elem or lot_price_min_elem
        lot_contract_period = elem(lot_contract_years, end='')
        lot_url = f'[{notice_number}]({href})'
        lot_info = close_tags(
            cut_len(
                        (
                            # f'{lot_title}'
                            f'_{procedure_name}_\n' 
                            f'*{elem(lot_name)}*' 
                            f'{elem(lot_price_elem)}' 
                            f'{elem(lot_estate_address, emoji="compass")}'

                            f'{elem(lot_contract_years, text="Срок договора (лет)", emoji="calendar")}'
                            f'{elem(lot_contract_months, text="Срок договора (мес)", emoji="calendar")}'
                            f'{elem(bidd_end_time, text="Подача до", emoji="alarm_clock")}\n'
                            f'`{elem(lot_description, emoji="flag_small", end=config.EOL+config.EOL)}`'
                            f'{lot_characteristics}'
                        )
                , config.TELEGRAM_MESSAGE_LIMIT)
                )
        lot_info += f'{config.EOL} {elem(lot_url, pre=" ", emoji="globe_with_meridians")}'

        print(f'{lot_info = }')
        img_ids = list(filter(lambda i: i.get('size') < config.IMG_SIZE_LIMIT, lot.get('imageIds', [])))[:9]

        if len(img_ids) > 1: # если есть изображения лота
            media_group = []
            for attachment in img_ids:
                ok, filename = notification_obj.attachment_content_save(content_id=attachment['id'], 
                                                                    filename=attachment_id_name(attachment))
                if ok:  # если скачиваени прошло хорошо
                    large_img_resize(attachment_id_name(attachment), config.IMG_MAX_SIZE_XY)
                    with open(attachment_id_name(attachment), 'rb') as attachment_file:
                        data = attachment_file.read() 
                        if not media_group:
                            media_group.append(InputMediaPhoto(data, caption=close_tags(cut_len(lot_info, config.TELEGRAM_MESSAGE_CAPTION_LIMIT)), parse_mode='MARKDOWN'))
                        else:
                            media_group.append(InputMediaPhoto(data))
                else:
                    log.error(f'cant download attachment {href} {attachment_id_name(attachment)}')
            bot.send_media_group(chat_id, media_group)
            # sleep(1)

        elif len(img_ids) == 1: # оджно изображение
            # log.info('--- mode --- one media') 
            ok, filename = notification_obj.attachment_content_save(content_id=img_ids[0]['id'], filename=attachment_id_name(img_ids[0]))
            if ok:  # если скачиваени прошло хорошо
                large_img_resize(attachment_id_name(img_ids[0]), config.IMG_MAX_SIZE_XY)
                with open(attachment_id_name(img_ids[0]), 'rb') as f:
                    bot.send_photo(chat_id, f, caption=close_tags(cut_len(lot_info, config.TELEGRAM_MESSAGE_CAPTION_LIMIT)))
            else:                    
                log.error(f'cant download attachment {href} {attachment_id_name(attachment)}')
        else:
            bot.send_message(chat_id, lot_info)

        # bot.send_message(chat_id, f'{Telegram.emoji["arrow_up"]} [{notice_number}]({href})', parse_mode='MarkdownV2')
        # удалить файлы аттача 
        del_file_attachment_id_name(img_ids)


def process_error(href: str):
    try_num = sql.get_try_num_by_href(href)
    sql.set_try_num_by_href(href, str(try_num + 1))
    if try_num > 2:
        log.error(f'cant get ni by url {href}\n{try_num =}')


def prepare_records_for_db(notice_list: list, existing_href: list):
    pass
    records = []
    for i in notice_list:
        if not i.get('href') in existing_href:
            records.append(
                            (i.get('bidderOrgCode'),
                            i.get('rightHolderCode'),
                            i.get('documentType'),
                            i.get('regNum'),
                            i.get('publishDate'),
                            i.get('href'),
                            )
                        )
    return records


def get_few_days_notice_list(deepnes:int) -> list[dict]:
    few_days_notice_list = []
    for d_num in range(-1, -deepnes, -1):
        one_day_notice_list = torgi.get_day_notice_list(day_index=d_num)
        # save_dict_to_json_file(f'day{d_num}.json', one_day_notice_list)
        few_days_notice_list += one_day_notice_list
    return few_days_notice_list


# def users_prepare() -> list[dict]:
#     users = sql.get_users()

#     result ={}
#     for u in users:
#         searches = sql.get_user_search(user_id=u)
#         s_data = []
#         for s in searches:
#             s_id, s_content = s
#             s_pattern = search_pattern_prepare_one(s_content)
#             s_data.append([s_id, s_pattern])

#         result.update({u : s_data}) 
#     return result




def main():

    log.info(f'-------------- START - {datetime.now()}')
    sql.sql_start(config.sqlite_db_filename)
    sql.sql_start_users(config.sqlite_db_users_filename)

    few_days_notice_list = get_few_days_notice_list(config.DAYS_DEEP_NOTICE_WATCH)
    log.info(f'last few_days_notice_list = {len(few_days_notice_list)}, days = {config.DAYS_DEEP_NOTICE_WATCH}')

    db_all_records_href_list = sql.get_all_notice_href()
    log.info(f'db all_records_url_list = {len(db_all_records_href_list)}')

    records = prepare_records_for_db(notice_list=few_days_notice_list, existing_href=db_all_records_href_list)
    log.info(f'notice to append = {len(records)}')
    sql.add_notice_many(records)

    notice_todo = sql.get_notice_href_by_done(done=0)
    log.info(f'notice_todo = {len(notice_todo)}')


    users_search_data = users_prepare_sql()

    for href in notice_todo:
        print(f'{href = }') 
        try:
            ni = n.info(href)
        except:
            process_error(href)
            continue
            
        if not ni:
            process_error(href)
        else:
            for user_id, user_all_searches in users_search_data.items():
                for one_search in user_all_searches:
                    s_id, s_content = one_search
                    if config.DEBUG_PASS_ALL_NOTICE or is_all_regex_in_str(input_str=str(ni), regex_list=s_content): # в извещении есть искомое
                        process_notification(notification_obj=n, notice_info=ni, bot=bot, chat_id=user_id)
                        sql.set_send_by_href(href)
                        sql.set_user_search_sended(s_id)

            sql.set_done_now_by_href(href)
            sleep(config.PROCESS_NOTICE_DELAY)
    

if __name__ == '__main__':
    sys.excepthook = my_exception_hook
    log = app_logger.get_logger('tw2')
    # log.info('')
    torgi = TorgiGovRu()
    n = Notification()
    bot=TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')
    main()



 
 # v0.11
# - set_send_by_href

# v0.10
# - перевел работу с базой на sqlite

# v0.06
# - добавлено поле try если не получены сведения с первого раза, далее уведомление об ошибке после нескольких try

# v0.05
# - добавлен поиск по коду субъекта размещения лота по тэгу @92
# - добавлен поиск по вхождению части слова в извещении по обертке *часть*
# - выведение типа договора и срока договора аренды

# v0.04
# - сообщение об ошибке и переход к новой итерации при отсутствии данных по url json
# - формат цены лота учитывает цену в год/месяц или стопро чистую стоимость

# v0.03
# - добавлена стрелка вверх для уведомления с ссылкой на извещение
