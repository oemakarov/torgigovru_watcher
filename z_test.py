import lib.db_sqlite as sql
sql.sql_start('test.db')

# sql.add_notice('2100002974', '2100002974', 'notice', 
#             '21000029740000000155', '2022-12-02T00:24:03.935Z', 
#             'https://torgi.gov.ru/new/opendata/7710568760-notice/docs/notice_21000029740000000155_1f4d5252-7634-41fd-b0c0-c4eb21e75310.json')
# res = sql.get_done_by_href('1')
# print(res)

# res1 = sql.get_notice_by_done(1)
# print(res1)

res1 = sql.set_done_now_by_href('https://torgi.gov.ru/new/opendata/7710568760-notice/docs/notice_21000014540000000063_4ef17223-ebd9-4540-aa2f-120d84e3434d.json')
# print(res1)

# res1 = sql.get_try_num_by_href('https://torgi.gov.ru/new/opendata/7710568760-notice/docs/notice_21000029740000000155_1f4d5252-7634-41fd-b0c0-c4eb21e75310.json')
# res1 = sql.get_try_num_by_href('https://torgi.gov.ru/new/opendata/7710568760-notice/docs/notice_21000029740000000155_1f4d5252-7634-41fd-b0c0-c4eb21e75310.json')
# print(res1)
# for i in res1:
#     print(i)
#     print('--'*20)