from contextlib import contextmanager
import glob
import os
import sys

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


def migrate(version):
    if not os.path.isfile('CURRENT_VERSION'):
        print('Can not read current version.')
        return False

    with open('CURRENT_VERSION', 'r') as f:
        current_version = int(f.read())
    print('Current schema version: %s' % current_version)

    def get_migrations(direction, from_version, to_version):
        migrations = {int(m.split('_')[0]): m for m in glob.glob('*_%s.sql' % direction)}
        sorted_keys = sorted([k for k in migrations.keys() if k > from_version and k <= to_version],
                             reverse=direction == 'down')
        return migrations, sorted_keys

    migrations, sorted_keys = [], []
    if current_version < version:
        next_version = lambda x: x
        migrations, sorted_keys = get_migrations('up', current_version, version)
    elif current_version > version:
        next_version = lambda x: x - 1
        migrations, sorted_keys = get_migrations('down', version, current_version)

    for k in sorted_keys:
        migration = migrations[k]
        success = run_migration(k, next_version(k), migration)
        if not success:
            return False

    return True


def run_migration(from_version, to_version, migration_file):
    with open(migration_file, 'r') as f:
        sql = f.read()

    cmd = 'BEGIN TRANSACTION;\n%s\nCOMMIT;' % (sql)

    with pg_connection(user='travel_log_admin', database='travel_log') as (_, cur, _):
        print('Running migration %s' % migration_file)
        try:
            cur.execute(cmd)
        except Exception as e:
            print('Migration failed!')
            print(e)
            return False

    with open('CURRENT_VERSION', 'w') as f:
        f.write('%s\n' % to_version)

    print('Successfully migrated to version %s!' % to_version)


if __name__ == '__main__':
    try:
        version = int(sys.argv[1])
    except:
        print('Please specify a version where to migrate')
        sys.exit(0)

    success = migrate(version)
    if success:
        print('Database is at version %s!' % version)
