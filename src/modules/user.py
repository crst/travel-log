import shared.db as db
from shared.util import config, get_logger
from shared.auth import is_shared

logger = get_logger(__name__)


def get_albums(user_name, current_user):
    logger.debug('{Module|User} get_albums(%s, %s)', user_name, current_user)

    albums = []
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if not err:
            albums = db.query_all(
                cur,
                '''
SELECT
  a.id_album, a.album_title, a.album_desc, st.share_type_name, s.secret
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
JOIN travel_log.share s ON s.fk_album = a.id_album AND s.fk_user = u.id_user
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
WHERE u.user_name=%(user)s AND NOT a.is_deleted
ORDER BY a.id_album
                ''',
                {'user': user_name})
        else:
            logger.debug('{Module|User}: %s' % err)

    result = [a for a in albums if is_shared(current_user, user_name, a.album_title, None)]
    return result
