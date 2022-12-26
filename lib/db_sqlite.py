import sqlite3 as sq
from datetime import datetime


def sql_start(sqlite_db_filename: str):
    global base, cur
    base = sq.connect(sqlite_db_filename)
    cur = base.cursor()


    # if base:
    #     print('data base - connected - OK')
        
    cur.execute('''CREATE TABLE IF NOT EXISTS 
                        notice(
                            id INTEGER PRIMARY KEY, 
                            bidder_org_code TEXT, 
                            right_holder_code TEXT, 
                            document_type TEXT, 
                            reg_num TEXT, 
                            publish_date TEXT, 
                            href TEXT, 
                            done INTEGER DEFAULT 0, 
                            done_date TEXT, 
                            try_num INTEGER DEFAULT 1,
                            send INTEGER DEFAULT 0
                            )''')
    base.commit()

# ----------------------------------------
def sql_start_users(sqlite_db_filename: str):
    global base_users, cur_users
    base_users = sq.connect(sqlite_db_filename)
    cur_users = base_users.cursor()


def get_users() -> list:
    rows = cur_users.execute('SELECT DISTINCT user_id FROM users').fetchall()
    return [r[0] for r in rows]


def get_user_search(user_id: str) -> list:
    rows = cur_users.execute('SELECT id, search FROM users WHERE user_id = ?', (user_id, )).fetchall()
    return rows

def get_user_send_times(id: str) -> int:
    rows = cur_users.execute('SELECT send_times FROM users WHERE id = ?', (id, )).fetchone()
    return rows[0]

def set_user_search_sended(id: str):
    send_times = get_user_send_times(id)
    # print(f'***************{send_times =}')
    send_times_new = send_times +1
    cur_users.execute('UPDATE users SET send_datetime = ?, send_times = ? WHERE id = ?', 
                            (str(datetime.now()), send_times_new, id))
    base_users.commit()


# ----------------------------------------
def get_all_notice_href() -> list:
    rows = cur.execute('SELECT href FROM notice').fetchall()
    return [r[0] for r in rows]

def get_notice_by_done(done: int) -> list:
    rows = cur.execute('SELECT * FROM notice WHERE done = ?', (done, )).fetchall()
    return rows

def get_notice_href_by_done(done: int) -> list:
    rows = cur.execute('SELECT href FROM notice WHERE done = ?', (done, )).fetchall()
    return [r[0] for r in rows]

def is_got_notice_by_href(href: str) -> bool:
    res = get_notice_by_href(href)
    return True if res else False

def get_notice_by_href(href: str) -> list:
    rows = cur.execute('SELECT * FROM notice WHERE href = ?', (href, )).fetchall()
    return rows

def get_done_by_href(href: str) -> list:
    print(f'{href = }')
    rows = cur.execute('SELECT done FROM notice WHERE href = ?', (href, )).fetchall()
    # вернуть true или false
    return bool(rows[0][0])


def set_done_now_by_href(href: str):
    set_done_by_href(href, datetime.now())


def set_done_by_href(href: str, date_time: datetime):
    cur.execute('UPDATE notice SET done = ?, done_date = ? WHERE href = ?', (1, str(date_time), href))
    base.commit()


def set_send_by_href(href: str):
    cur.execute('UPDATE notice SET send = 1 WHERE href = ?', (href, ))
    base.commit()


def get_try_num_by_href(href: str) -> list:
    rows = cur.execute('SELECT try_num FROM notice WHERE href = ?', (href, )).fetchall()
    # вернуть целое число
    if len(rows) == 1:
        return rows[0][0]
    else:
        raise(f'multi href in base {href = }')


def add_notice(bidder_org_code: str, 
                        right_holder_code: str, 
                        document_type: str, 
                        reg_num: str, 
                        publish_date: str, 
                        href: str):

    cur.execute('''INSERT INTO notice(bidder_org_code, 
                                    right_holder_code, 
                                    document_type, 
                                    reg_num, 
                                    publish_date, 
                                    href, 
                                    done, 
                                    done_date, 
                                    try_num) VALUES (?, ?, ?, ?, ?, ?)''', 
                                    (bidder_org_code, 
                                    right_holder_code, 
                                    document_type, 
                                    reg_num, 
                                    publish_date, 
                                    href
                                    ))
    base.commit()

def add_notice_many(records: list[tuple]):
    # bidder_org_code: str, 
    #                     right_holder_code: str, 
    #                     document_type: str, 
    #                     reg_num: str, 
    #                     publish_date: str, 
    #                     href: str):

    cur.executemany('''INSERT INTO notice(bidder_org_code, 
                                    right_holder_code, 
                                    document_type, 
                                    reg_num, 
                                    publish_date, 
                                    href) 
                                    VALUES (?, ?, ?, ?, ?, ?)''', records)
                                    # (bidder_org_code, 
                                    # right_holder_code, 
                                    # document_type, 
                                    # reg_num, 
                                    # publish_date, 
                                    # href,
    base.commit()


def set_try_num_by_href(href: str, try_num: int) -> list:
    cur.execute('UPDATE notice SET try_num = ? WHERE href = ?', (try_num, href, ))
    base.commit()

# ---------------


# def del_notice_by_date(limit_datetime: datettime):
#     cur.execute('''DELETE FROM notice 
#                         WHERE user_id=? 
#                         AND 
#                         search_text=?''', (limit_datetime))
#     base.commit()
