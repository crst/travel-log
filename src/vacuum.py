import glob
import os

import shared.db as db
from shared.util import config


def vacuum():
    # TODO: log deleted filenames

    # Step 1:
    # Search for database entries that have the `is_deleted` flag. If
    # an album is marked as deleted, this cascaded to all the items,
    # even if the flag isn't actually set.
    print('Searching for image files marked as deleted...')
    found_stale_items = False
    with db.pg_connection(config['app-database']) as (_, cur, _):
        stale_items = db.query_all(
            cur,
            '''
SELECT
  CASE WHEN a.is_deleted THEN a.id_album END AS id_album,
  i.id_item,
  i.image
FROM travel_log.album a
LEFT JOIN travel_log.item i ON a.id_album = i.fk_album
WHERE a.is_deleted OR i.is_deleted
'''
        )

    album_ids = tuple([int(item.id_album) for item in stale_items if item.id_album])
    item_ids = tuple([int(item.id_item) for item in stale_items if item.id_item])
    for item in stale_items:
        found_stale_items = True
        if item.id_item:
            fs_path = os.path.join(
                config['storage-engine']['path'],
                item.image
            )
            print('  - Deleting file %s' % fs_path)
            if os.path.isfile(fs_path):
                os.remove(fs_path)
    if not found_stale_items:
        print(' - None found!')


    # Step 2:
    # Once files are deleted, we can delete the corresponding database
    # entries.
    print('Searching for database entries to delete...')
    found_db_entries = False
    with db.pg_connection(config['app-database']) as (_, cur, _):
        if item_ids:
            found_db_entries = True
            print('  - Deleting items')
            cur.execute(
                'DELETE FROM travel_log.item WHERE id_item IN %(items)s',
                {'items': item_ids}
            )
        if album_ids:
            print('  - Deleting share entries')
            cur.execute(
                'DELETE FROM travel_log.share WHERE fk_album IN %(albums)s',
                {'albums': album_ids}
            )
            found_db_entries = True
            print('  - Deleting albums')
            cur.execute(
                'DELETE FROM travel_log.album WHERE id_album IN %(albums)s',
                {'albums': album_ids}
            )
    if not found_db_entries:
        print(' - None found!')


    # Step 3:
    # Find image files that are no longer referenced from the database
    # and delete them. This ideally shouldn't happen, but if anything
    # goes wrong it does, so we search for them.
    print('Searching stale image files...')
    found_stale_files = False

    with db.pg_connection(config['app-database']) as (_, cur, _):
        ref_items = db.query_all(
            cur,
            '''
SELECT image FROM travel_log.item WHERE NOT is_deleted
 UNION
SELECT background FROM travel_log.album WHERE NOT is_deleted
            ''')
    ref = set([
        os.path.join(config['storage-engine']['path'], i.image) for i in ref_items
    ])

    on_disk = set(glob.glob(os.path.join(
        config['storage-engine']['path'],
        '*',
        '*',
        '*.jpg'
    )))
    # TODO: this is not very efficient, but works for now.
    diff = on_disk.difference(ref)
    for stale in diff:
        found_stale_files = True
        print(' - Deleting image from disk: %s' % stale)
        os.remove(stale)
    if not found_stale_files:
        print(' - None found!')


    # Step 4:
    # Remove empty directories
    print('Searching stale folders...')
    with db.pg_connection(config['app-database']) as (_, cur, _):
        albums = db.query_all(
            cur,
            'SELECT fk_user, id_album FROM travel_log.album WHERE NOT is_deleted'
        )
    albums = set([(a.fk_user, a.id_album) for a in albums])
    folders = [d for d in glob.glob(os.path.join(config['storage-engine']['path'], '*', '*'))]
    found_stale_folders = False
    for f in folders:
        rest, aid = os.path.split(f)
        rest, uid = os.path.split(rest)
        if (int(uid), int(aid)) not in albums:
            found_stale_folders = True
            print(' - Delete folder from disk: %s' % f)
            os.rmdir(f)
    if not found_stale_folders:
        print(' - None found')


if __name__ == '__main__':
    vacuum()
