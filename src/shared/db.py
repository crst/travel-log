from contextlib import contextmanager

import psycopg2

from shared.util import config, get_logger

logger = get_logger(__name__)


@contextmanager
def pg_connection(cnf):
    try:
        con = psycopg2.connect(user=cnf['user'],
                               password=cnf['password'],
                               database=cnf['database'],
                               host=cnf['host'],
                               port=cnf['port'])
        cur = con.cursor()
    except psycopg2.Error as err:
        yield None, None, err
    else:
        try:
            yield con, cur, None
        finally:
            con.commit()
            cur.close()
            con.close()


class Row(object):
    def __init__(self, cursor, result):
        result = result or [None for _ in cursor.description]
        for (column, value) in zip((d[0] for d in cursor.description), result):
            setattr(self, column, value)

def fetch_one_row(cur):
    return Row(cur, cur.fetchone())

def query_one(cur, query, env=None):
    cur.execute(query, env)
    return fetch_one_row(cur)

def query_all(cur, query, env=None):
    cur.execute(query, env)
    return [Row(cur, r) for r in cur.fetchall()]


# TODO: this is duplicated in common.py
def get_user_id(user_name):
    result = None
    with pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
            cur.execute(
                '''
SELECT *
  FROM travel_log.user
 WHERE user_name = %(name)s
                ''',
                {'name': user_name}
            )
            result = fetch_one_row(cur)
        except Exception as e:
            logger.error(e)

    if result:
        return result.id_user
    return None


class User(object):
    def __init__(self, name, authenticated=False, id_user=None):
        self.name = name
        self.authenticated = authenticated
        self.id_user = id_user or get_user_id(self.name)
        self.is_anonymous = False

    def set_authenticated(self, password):
        with pg_connection(config['app-database']) as (_, cur, err):
            if err:
                logger.error(err)
            try:
                cur.execute(
                    '''
SELECT pw_hash = crypt(%(pw)s, pw_hash) AS auth
  FROM travel_log.user
 WHERE id_user = %(id)s
                    ''',
                    {'pw': password, 'id': self.id_user})
                result = fetch_one_row(cur)
                if result.auth:
                    self.authenticated = True
            except Exception as e:
                logger.error(e)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.name


def load_user(key):
    user = None
    with pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        try:
            cur.execute(
                '''
SELECT *
  FROM travel_log.user
 WHERE user_name = %(name)s
                ''',
                {'name': key})
            user = fetch_one_row(cur)
        except Exception as e:
            logger.error(e)

    if user:
        return User(user.user_name, id_user=user.id_user)
    return None
