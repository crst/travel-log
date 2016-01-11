from contextlib import contextmanager

import psycopg2

from util import config


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

def fetch_one(cur):
    return Row(cur, cur.fetchone())

def query_one(cur, query, env):
    cur.execute(query, env)
    return fetch_one(cur)

def query_all(cur, query, env):
    cur.execute(query, env)
    return [Row(cur, r) for r in cur.fetchall()]


def get_user_id(user_name):
    with pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            cur.execute('SELECT * FROM travel_log.user WHERE user_name = %(name)s', {'name': user_name})
            result = fetch_one(cur)
            return result.id_user


class User(object):
    def __init__(self, name, authenticated=False, id_user=None):
        self.name = name
        self.authenticated = authenticated
        self.id_user = id_user or get_user_id(self.name)


    def set_authenticated(self, password):
        with pg_connection(config['app-database']) as (_, cur, err):
            if not err:
                cur.execute(
                    'SELECT pw_hash = crypt(%(pw)s, pw_hash) AS auth FROM travel_log.user WHERE id_user = %(id)s',
                    {'pw': password, 'id': self.id_user})
                result = fetch_one(cur)
                if result.auth:
                    self.authenticated = True

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name


def load_user(key):
    with pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            cur.execute(
                'SELECT * FROM travel_log.user WHERE user_name = %(name)s',
                {'name': key})
            user = fetch_one(cur)
            if user:
                return User(user.user_name, id_user=user.id_user)
    return None
