
__version__ = '0.19'
# 'москва+авто'
# '*частьслова*+обособленноеслово+@92'


# v0.19
# - заменил кадастровый номер на ссылку с картой replace_kadnum_to_maplink

# v0.18
# - подключены новые данные о сроке договора аренды

# v0.17
# - message new text order

# v0.16
# - message link to lot url

# v0.15
# - bugfix

# v0.14
# - переписано на sqlite, завязка на user_data

# v0.13
# - вывод количества месяцев аренды lot_contract_months

# v0.12
# - рефакторинг кода, вынес глубину дней анализа извещений в конфиг

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