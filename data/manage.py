from contextlib import contextmanager
import glob
import os

import psycopg2


@contextmanager
def pg_connection(user=None, password=None, database=None, host=None, port=None):
    try:
        con = psycopg2.connect(user=user,
                               password=password,
                               database=database,
                               host=host,
                               port=port)
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


def migrate_up():
    if not os.path.isfile('CURRENT_VERSION'):
        print('Can not read current version.')
        return False

    # Read current version
    # Apply all changes
    with open('CURRENT_VERSION', 'r') as f:
        version = int(f.read())
    print('Current schema version: %s' % version)

    migrations_up = glob.glob('*_up.sql')
    available_migrations = {int(m.split('_')[0]): m for m in migrations_up}
    keys = sorted([k for k in available_migrations.keys() if k > version])
    for k in keys:
        migration = available_migrations[k]
        success = run_migration(k, migration)
        if not success:
            return False

    return True


def run_migration(version, up_file):
    with open(up_file, 'r') as f:
        sql = f.read()

    cmd = 'BEGIN TRANSACTION;\n%s\nCOMMIT;' % (sql)

    with pg_connection(user='travel_log_admin', database='travel_log') as (_, cur, _):
        print('Running migration to version %s' % version)
        try:
            cur.execute(cmd)
        except Exception as e:
            print('Migration to version %s failed!' % version)
            print(e)
            return False

    with open('CURRENT_VERSION', 'w') as f:
        f.write('%s\n' % version)

    print('Successfully migrated to version %s!' % version)


if __name__ == '__main__':
    success = migrate_up()
    if success:
        print('Database is a latest version!')
