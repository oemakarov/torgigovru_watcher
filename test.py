import re 

KADNUM_PATTERN = '\d{2}:\d{2}:\d{6,7}:\d*'
MAP_LINK = 'https://egrp365.org/map/?kadnum={}'

TELERGAM_LINK_TEMPLATE = '[{}]({})'

def replace_kadnum_to_maplink(source: str) -> str:
    for kadnum in re.findall(KADNUM_PATTERN, source):
        source = source.replace(kadnum, TELERGAM_LINK_TEMPLATE.format(kadnum,MAP_LINK.format(kadnum)))
    return source


input_str='Встроенные нежилые помещения, общей площадью 239,5 кв.м, кадастровый номер: 91:03:002001:2021, расположенные по адресу: г. Севастополь, ул. Хрусталева, д. 29.'

print(replace_kadnum_to_maplink(input_str))



# 'площадью 239,5 кв.м, кадастровый номер: 91:03:002001:2021, расположенные по адресу:'
# 'площадью 239,5 кв.м, кадастровый номер: https://egrp365.org/map/?kadnum=91:03:002001:2021, расположенные по адресу:'