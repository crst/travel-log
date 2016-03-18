from shared.common import is_current_user
import shared.db as db
from shared.util import config, get_logger

logger = get_logger(__name__)


def is_allowed(current_user, user_name):
    if not current_user.is_anonymous and current_user.name == user_name:
        return True
    return False


def is_shared(current_user, user_name, album_title, secret_part):
    if is_current_user(user_name, current_user):
        return True

    with db.pg_connection(config['app-database']) as (_, cur, err):
        share_type = db.query_one(
            cur,
            '''
SELECT
  st.share_type_name,
  s.secret
FROM travel_log.share s
JOIN travel_log.share_type st ON st.id_share_type = s.fk_share_type
JOIN travel_log.album a ON a.id_album = s.fk_album
JOIN travel_log.user u ON u.id_user = s.fk_user
WHERE a.album_title = %(album)s
  AND u.user_name = %(user)s
  AND NOT a.is_deleted
            ''',
            {'user': user_name, 'album': album_title}
        )
        if share_type.share_type_name == 'Public':
            return True

        if share_type.share_type_name == 'Hidden':
            if share_type.secret and share_type.secret == secret_part:
                return True

    return False
