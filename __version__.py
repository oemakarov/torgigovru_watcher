
__version__ = '0.42'
# 'москва+авто'
# '*частьслова*+обособленноеслово+@92'


# v0.42
# - доработка безопасности

# v0.41
# - доп логирование
# - из-а смены схемы данных torgi.gov.ru изменил глубину дней для анализа извещеий с 8 до 1. спустя неделю нужно вернуть 8

# v0.40
# - удаление всех запросов пользователя при ошибке - Bad Request: failed to send message #1 with the error message "USER_IS_BLOCKED"

# v0.39
# - добавил в регулярку wrap_word английские буквы, теперь можно искать на английском

# v0.38
# - BLOCKED_BY_USER edit description text

# v0.37
# - flood control handler for telegram exception

# v0.36
# - telebot_exception_handler для обработки ошибок отправки сообщений
# - refactoring

# v0.35
# - try except для отправки медиагруппы. для отлова ошибок по описанию

# v0.34
# - добавен Dockerfile, исправлены пути до data, data_user, log

# v0.33
# - вынесены наружу log и data

# v0.32
# - убрал 'v' и номера версии

# v0.31
# - fix datetime - timedelta issue

# v0.30
# - удаление старых извещений и информации об обработанных извещениях/лотах 
# - метод del old notice
# - константа config.DELETE_TIME_DELTA_DAYS
# - сжатие базы VACUUM

# v0.29
# - исправлена ошибка формирования url, теперь используется mlink от telebot. ранее сообщения с url не доходили
# - убран раздел отправки сообщения с одной фото, теперь все фотки отправляются как mediagroup

# v0.28
# - переписан метод масштабирования изображения, введена константа, определяющая лимит выше которого картинки не прикрепляются

# v0.27
# - lot_url char_escape fix

# v0.26
# - добавлен вывод ссылки на карту для кадастровых номеров

# v0.25
# - экранирование тэгов в сообщении, закрытие тэгов и экранирование при подборе длины сообщения

# v0.24
# - обработка поля send_link - регулирует отправлять ли ссылку на лот

# v0.23
# - добавлена таблица sended для фиксации отправки сообщений по каждому лоту, для исключения повторной отправки
#     так же не будет отправлен лот если данное извещение попадает под другой поисковой запрос пользователя

# v0.22
# - убрал уведомление о недоступном url, теперь в базу в поле done ставится значение 2

# v0.21
# - изменение логирования ошибок обработки извещения *process_error

# v0.20
# - отслеживание количества отправлений по href notice.send
# - config.HREF_TRY_LIMIT_ADMIN_ALERT

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