# encoding=utf8
from datetime import datetime
from time import sleep
import sys
from telebot import TeleBot
from telebot.types import InputMediaPhoto
from telebot.formatting import escape_markdown as esc

import warnings
warnings.filterwarnings('ignore')

import config
import lib.app_logger_watcher as app_logger
import lib.db_sqlite as sql
from lib.torgigovru2 import Notification, TorgiGovRu
from lib.telegram import Telegram
from lib.tools import (
    replace_kadnum_to_maplink,
    users_prepare_sql,
    prepare_records_for_db,
    is_all_regex_in_str,
    attachment_id_name,
    del_file_attachment_id_name,
    close_tags_markdown_esc,
    cut_len,
    money_format,
    elem,
    pre_end,
    large_img_resize,
    getget,
    getget_str,
    fields_to_dict_from_list,
    compose_lot_link,
)
from __version__ import __version__


def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    if exctype != SystemExit:
        error_text = '\nКритическая ошибка.\n\nERROR : ' + str(value) + '\n' + str(traceback.tb_frame) + '\nline no : ' + str(traceback.tb_lineno)
        error_text_caption = f'{config.log_name} v{__version__}\n`{error_text}`'
        telegram = Telegram()
        telegram.send_message(error_text_caption)
    sys.exit(1)


def process_notification(notification_obj: Notification, notice_info: dict, bot: TeleBot, chat_id: str, send_link: int):

    # save_dict_to_json_file('notification.json', notice_info)
    notice = notice_info['exportObject']['structuredObject']['notice']
    notice_number = notice['commonInfo']['noticeNumber']
    log.info(f'{notice_number = }') 

    bidd_type_name = notice['commonInfo']['biddType']['name']
    procedure_name = notice['commonInfo']['procedureName']
    bidd_end_time = notice["biddConditions"]["biddEndTime"][:10]
    href = notice['commonInfo']['href']
    
    for lot in notice.get('lots'):
        lot_number = lot.get("lotNumber")

        if sql.is_lot_sended(reg_num=notice_number, lot_num=lot_number, user_id=chat_id):
            continue

        sleep(config.PROCESS_LOT_DELAY)

        log.info(f'лот - {lot_number}') 
        lot_name = lot.get("lotName")
        lot_description = lot.get("lotDescription")

        if lot_name == lot_description:
            lot_description = ''
        if lot_name == procedure_name:
            procedure_name = ''

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
        lot_contract_years = getget(lot_additional_details, 'DA_contractYears', 'value') or getget(lot_additional_details, 'DA_contractYears_BA(67)', 'value')
        lot_contract_months = getget(lot_additional_details, 'DA_contractMonths', 'value') or getget(lot_additional_details, 'DA_contractMonths_BA(67)', 'value')
        lot_contract_period = getget(lot_additional_details, 'DA_contractDate_EA(ZK)', 'value') or getget(lot_additional_details, 'DA_contractDate_PA(ZK)', 'value')

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
        lot_url = compose_lot_link(notice_number, lot_number) if send_link else ''
        
        lot_info = (
                    f'{esc(elem(lot_url))}'
                    f'_{esc(elem(procedure_name, end=f"{config.EOL*2}"))}_'
                    f'{pre_end(replace_kadnum_to_maplink(esc(lot_name)), end=config.EOL*2)}' 
                    f'{esc(elem(lot_price_elem))}' 
                    f'{esc(elem(lot_estate_address, emoji="compass"))}'
                    f'{esc(elem(lot_contract_period, text="Срок аренды", emoji="calendar"))}'
                    f'{esc(elem(lot_contract_years, text="Срок договора (лет)", emoji="calendar"))}'
                    f'{esc(elem(lot_contract_months, text="Срок договора (мес)", emoji="calendar"))}'
                    f'{esc(elem(bidd_end_time, text="Подача до", emoji="alarm_clock"))}\n'
                    f'`{esc(elem(lot_description, emoji="flag_small", end=config.EOL+config.EOL))}`'
                    f'{esc(lot_characteristics)}'
                    )

        print(f'{lot_info = }')
        lot_info_ready = close_tags_markdown_esc(cut_len(lot_info, config.TELEGRAM_MESSAGE_CAPTION_LIMIT))
        print(f'{lot_info_ready = }')

        img_ids = [i for i in lot.get('imageIds', []) if i.get('size') < config.IMG_SIZE_LIMIT][:9] 

        if len(img_ids) > 1: # несколько изображений лота
            media_group = []
            for attachment in img_ids:
                ok, filename = notification_obj.attachment_content_save(content_id=attachment['id'], 
                                                                    filename=attachment_id_name(attachment))
                if ok:  # если скачиваени прошло хорошо
                    large_img_resize(attachment_id_name(attachment), config.IMG_MAX_SIZE_XY)
                    with open(attachment_id_name(attachment), 'rb') as attachment_file:
                        data = attachment_file.read() 
                        if not media_group:
                            media_group.append(
                                            InputMediaPhoto(data, 
                                                caption=lot_info_ready, 
                                                            parse_mode=config.DEFAULT_PARSE_MODE))
                        else:
                            media_group.append(InputMediaPhoto(data))
                else:
                    log.error(f'cant download attachment {href} {attachment_id_name(attachment)}')
            bot.send_media_group(chat_id, media_group)
            sql.add_lot_sended(reg_num=notice_number, lot_num=lot_number, user_id=chat_id)

        elif len(img_ids) == 1: # одно изображение
            ok, filename = notification_obj.attachment_content_save(content_id=img_ids[0]['id'], filename=attachment_id_name(img_ids[0]))
            if ok:  # если скачиваени прошло хорошо
                large_img_resize(attachment_id_name(img_ids[0]), config.IMG_MAX_SIZE_XY)
                with open(attachment_id_name(img_ids[0]), 'rb') as f:
                    bot.send_photo(chat_id, f, caption=lot_info_ready)
                    sql.add_lot_sended(reg_num=notice_number, lot_num=lot_number, user_id=chat_id)
            else:                    
                log.error(f'cant download attachment {href} {attachment_id_name(attachment)}')
        else: # нет изображений
            bot.send_message(chat_id, lot_info, disable_web_page_preview=True)
            sql.add_lot_sended(reg_num=notice_number, lot_num=lot_number, user_id=chat_id)
        # bot.send_message(chat_id, f'{Telegram.emoji["arrow_up"]} [{notice_number}]({href})', parse_mode='MarkdownV2')
        del_file_attachment_id_name(img_ids)


def process_all_users_searches(href: str, users_search_data: dict, ni: dict):
    for user_id, user_all_searches in users_search_data.items():
        for one_search in user_all_searches:
            s_id, s_content, s_send_link = one_search
            if config.DEBUG_PASS_ALL_NOTICE or \
                    is_all_regex_in_str(input_str=str(ni), regex_list=s_content): # в извещении есть искомое
                log.info(f'MATCH {user_id = } {s_content = }')
                process_notification(notification_obj=n, notice_info=ni, bot=bot, chat_id=str(user_id), send_link=s_send_link)
                sql.set_add1_send_by_href(href)
                sql.set_user_search_sended(s_id)
                sleep(config.TELEGRAM_MESSAGE_DELAY)


def process_error(href: str, msg: str = ''):
    """обработка ошибки получения данных поста
    вносим +1 в базу по данному url, выводим сообщение в логи

    Args:
        href (str): ссылка на данные при обращении к которым проихошла ошибка
    """
    try_num = sql.get_try_num_by_href(href)
    sql.set_try_num_by_href(href, str(try_num + 1))
    if try_num > config.HREF_TRY_LIMIT_ADMIN_ALERT:
        # log.error(f'{msg} {href}\n{try_num =}')
        sql.set_done_error_now_by_href(href)


def get_few_days_notice_list(deepnes:int) -> list[dict]:
    """Получение списка ссылок на данные извещений за несколько дней в глубину

    Args:
        deepnes (int): количество дней в глубину. натуральное число

    Returns:
        list[dict]: список со словарями 
            {
      "bidderOrgCode": "2100001469",
      "rightHolderCode": "2100001469",
      "documentType": "notice",
      "regNum": "21000014690000000007",
      "publishDate": "2022-07-07T00:01:30.593Z",
      "href": "https://torgi.gov.ru/new/opendata/7710568760-notice/docs/notice_21000014690000000007_f99a356e-4165-48ab-aee9-5bcfae47f463.json"
            },
    """
    few_days_notice_list = []
    for d_num in range(-1, -deepnes, -1):
        one_day_notice_list = torgi.get_day_notice_list(day_index=d_num)
        # save_dict_to_json_file(f'day{d_num}.json', one_day_notice_list)
        few_days_notice_list += one_day_notice_list
    return few_days_notice_list



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

    notice_todo = sql.get_notice_href_by_done(value=0)
    log.info(f'notice_todo = {len(notice_todo)}')

    users_search_data = users_prepare_sql()
    log.info(f'{users_search_data = }')

    for href in notice_todo:
        log.info(f'{href = }')
        try:
            ni = n.info(href)
        except:
            process_error(href, 'n.info(href)')
            continue

        try:
            process_all_users_searches(href, users_search_data, ni)
        except Exception as e:
            process_error(href, 'process_all_users_searches')
            log.warning(f'{href = }\n{e}')
            raise e
        else:
            sql.set_done_ok_now_by_href(href)

        sleep(config.PROCESS_NOTICE_DELAY)

    log.info('.............. EXIT')
    

if __name__ == '__main__':
    sys.excepthook = my_exception_hook
    log = app_logger.get_logger(config.log_name)
    torgi = TorgiGovRu()
    n = Notification()
    bot=TeleBot(config.BOT_TOKEN, parse_mode=config.DEFAULT_PARSE_MODE)
    main()



 
