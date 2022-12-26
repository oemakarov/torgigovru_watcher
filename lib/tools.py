import re
import json
from pathlib import Path
from PIL import Image
import re
import lib.db_sqlite as sql
from lib.telegram import Telegram


def wraper(pattern:str) -> str:
    """
    Если строка обрамлена знаком * возвращает то, что внутри *_*
    Если @92, возвращает стандартную часть текста извещения с кодом субъекта 92
    В остальных случаях оборачивает регуляркой отдельного слова
    
    """

    if pattern[0] == pattern[-1] == '*':
        return pattern[1:-1]
    if pattern[0] == '@':
        return f"'subjectRF': {{'code': '{pattern[1:]}'"

    else:
        return wrap_word(pattern)

 
def wrap_word(pattern:str) -> str:
    """
    Обертка для регулярных выражений, обертка ищет словово не в составе других слов
    Возможны варианты с двух сторон слова знаки препинания, пробелы, начало/конец строки
    """
    return f'([^а-я]|^){pattern}([^а-я]|$)' # выделение чистого слова, не в составе другого слова


def search_pattern_prepare_one(search_item:str) -> list:
    if '+' in search_item:
        result = []
        for item in search_item.split('+'):
            result.append(wraper(item))
    else:
        result = [wraper(search_item)]
    return result


def search_pattern_prepare(pattern_list:list) -> list:
    prepared_pattern_list = []
    for search_item in pattern_list:
        if '+' in search_item:
            temp_search = []
            for item in search_item.split('+'):
                temp_search.append(wraper(item))
            prepared_pattern_list.append(temp_search)
        else:
            prepared_pattern_list.append(wraper(search_item))
    return prepared_pattern_list


def users_prepare_sql() -> list[dict]:
    users = sql.get_users()

    result ={}
    for u in users:
        searches = sql.get_user_search(user_id=u)
        s_data = []
        for s in searches:
            s_id, s_content = s
            s_pattern = search_pattern_prepare_one(s_content)
            s_data.append([s_id, s_pattern])

        result.update({u : s_data}) 
    return result


def prepare_records_for_db(notice_list: list, existing_href: list):
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


def is_all_regex_in_str(input_str:str, regex_list:list) -> bool:
    """Проверяет вхождение всех шаблонов regex в строку.
    Если элемент regex_list - список шаблонов - вернется True если все шаблоны входят в строку
        ['Шаблон2', 'Шаблон3']    True если вхождение обоих шаблонов        
    Arguments:
        input_str {str} -- строка в которой осуществляется поиск
        regex_list {list} -- список шаблонов    
    
    Returns:
        bool -- True в случае совпадения с любым шаблоном / группой шаблонов
    
    Raises:
        ValueError -- при передаче regex_list не список
    """

    return all([re.search(r, input_str, flags=re.IGNORECASE) for r in regex_list])



def is_any_regex_in_str(input_str:str, regex_list:list) -> bool:
    """Проверяет вхождение шаблонов regex в строку.

    Если элемент regex_list строка - возвращается True при вхождении этого паттерна,
    Если элемент regex_list - список шаблонов - вернется True если все шаблоны входят в строку
    [
    'Шаблон1',   True если вхождение
        ['Шаблон2', 'Шаблон3']    True если вхождение обоих шаблонов        
    ]    
    Arguments:
        input_str {str} -- строка в которой осуществляется поиск
        regex_list {list} -- список шаблонов    
    
    Returns:
        bool -- True в случае совпадения с любым шаблоном / группой шаблонов
    
    Raises:
        ValueError -- при передаче regex_list не список
    """

    if isinstance(regex_list, list):
        for item in regex_list:
            if isinstance(item, str):
                if re.search(item, input_str, flags=re.IGNORECASE):
                    return True
            elif isinstance(item, list):
                for pattern in item:
                    if not re.search(pattern, input_str, flags=re.IGNORECASE):
                        break
                else:
                    return True
        return False
    else:
        raise ValueError('@@@ ERROR : not list in is_any_in_str')


def attachment_id_name(attachment_record:dict):
    """
    Получение имени изображения из поля content_id.исходное имя картинка.jpg, результирующее [content_id].jpg
    """    
    return attachment_record['id'] + Path(attachment_record['name']).suffix


def del_file_attachment_id_name(attachment_record_list:list):
    """
    Удаление файла с преобразованным именем исходное имя картинка.jpg, результирующее [content_id].jpg
    """

    for attachment_record in attachment_record_list:
        Path(attachment_id_name(attachment_record)).unlink()


def close_tags(message:str):
    """
    Закрываем не закрытые тэги для telegram markdown 
    """
    tags = ['`', '*', '_']
    stack = []

    for char in message:
        if char in tags:
            if stack and char == stack[-1]:
                stack.pop()
            else:
                stack.append(char)
    if stack: 
        return message[:len(message)-len(stack)-3] + ''.join(reversed(stack)) + '...'        
    else:
        return message


def cut_len(message:str, limit:int) -> str:
    """
    Обрезаем строку до необходимой длины, если длина больше то в конец вставляются ... 
        message - входная строка
        limit - ограничение длины
    """
    if len(message) < limit:
        return message
    else:
        return message[:limit-3] + '...'


def money_format(mny:str, end=' р.') -> str:
    """Приведение строки с суммой 1000000,00 или 1.0E6 к виду 1 000 000,00
    
    Arguments:
        mny {str} -- число  
    
    Keyword Arguments:
        end {str} -- вставка для описания валюты в конце результирующей строки (default: {' р.'})
    """
    if mny != None:
        if 'E' in mny:
            multiplicator = 10**int(mny[mny.find('E')+1:])
            base = float(mny[:mny.find('E')])
            mny = str(base * multiplicator)
        
        if mny:
            x = mny.split('.')[0] # целая часть
            return '{0:,}'.format(int(x)).replace(',', ' ') + end # -----------
        return ''
    else:
        return ''



def elem(element:str, text:str='', emoji:str='', pre='', end='\n') -> str:
    
    emoji_str = Telegram.emoji[emoji] if emoji else ''
    text_str = text + ': ' if text else ''

    if element and element != 'None':
        return emoji_str + text_str + pre + ' '.join(str(element).split()) + end
    else:
        return ''


def let(year_count:str) -> str:
    """
    Из численного представления получаем словесное обозначение количества лет
    1 - год
    2 - года
    5 - лет
    ...
    """
    try:
        y = int(year_count)
        if y>100 :
            y = y % 100
        suffix = ("лет" if y in (11,12,13,14) or y % 10 in (5,6,7,8,9,0) else
          "год" if y % 10 == 1 else
          "года")
    except:
        suffix = f'year ({year_count})'
    return suffix


def large_img_resize(file_name, max_size_xy:int):
    """
    Преобразуем картинку из file_name в размер, где сумма высоты и ширины не больше max_size_xy
    """
    with Image.open(file_name) as im:
        width, height = im.size
        while width + height > max_size_xy:
            width //= 2
            height //= 2
        else:
            new = im.resize((width, height))
            new.save(file_name)


def save_dict_to_json_file(filename, dict_input):
    """
    Сохраняем словарь в json файл
        filename - файл куда происходит сохранение
        dict_input - сохраняемый словарь

    """

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dict_input, f, ensure_ascii=False, indent=4)



def getget(input_dict:dict, *keys):
    """
    Получает значение вложенных словарей, если значение не найдено возвращает None
    """
    for key in keys:
        input_dict = input_dict.get(key, {}) if isinstance(input_dict, dict) else None 
    return input_dict


def getget_str(input_dict:dict, *keys):
    """
    Получает значение вложенных словарей, если значение не найдено возвращает 
    """
    value = getget(input_dict, *keys)
    return str(value) if value else None



def fields_to_dict_from_list(list_of_fields : list) -> dict:
    """
    Преобразует список словарей с полями id value в словарь с полями id:value

    Входящий список:
    [   {'id' : значение id, 'value' : значение value }, ...  ]

    Результирующий словарь
    { значение id : значение value  }
    """

    _result = {}
    for field in list_of_fields:

        _result.update({field['code'] : {'name' : field['name'], 'value' : field['value']}})
    return _result
