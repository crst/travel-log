from cStringIO import StringIO
import datetime
import hashlib
from io import BytesIO
import os
import time

from dateutil.parser import parse as date_parser
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from werkzeug import secure_filename

import shared.db as db
from shared.util import config, get_logger

logger = get_logger(__name__)


MAX_ALLOWED_IMAGE_SIZE = int(0.5 * 1024 * 1024)
DEFAULT_JPEG_QUALITY = 90
DEFAULT_ZOOM_LEVEL = 14


def store_background_fs(file_storage, user_name, album_title):
    fname = _make_file_path(user_name, album_title, file_storage.filename)
    if not fname:
        return False
    fs_file, rel_path, aid = fname

    try:
        img = Image.open(StringIO(file_storage.read()))
    except Exception as e:
        logger.error(e)
        return False
    write_image(file_storage, img, fs_file)

    result = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)
        try:
            cur.execute(
                '''
UPDATE travel_log.album
   SET background = %(path)s
 WHERE id_album = %(aid)s
   AND NOT is_deleted
                ''',
                {'path': rel_path, 'aid': aid}
            )
            result = True
        except Exception as e:
            logger.error(e)
    return result


def store_item_fs(file_storage, user_name, album_title):
    fname = _make_file_path(user_name, album_title, file_storage.filename)
    if not fname:
        return False
    fs_file, rel_path, aid = fname

    # TODO: we need to make sure writing to the
    # filesystem/database happens as a transaction, i.e. either
    # both or none.

    try:
        img = Image.open(StringIO(file_storage.read()))
    except Exception as e:
        logger.error(e)
        return False

    file_storage.seek(0)
    meta_data = get_meta_data(img)
    zoom = (meta_data['lat'] and meta_data['lon']) and DEFAULT_ZOOM_LEVEL or None
    write_image(file_storage, img, fs_file)

    result = False
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            logger.error(err)

        # Store item in database
        try:
            new_item = db.query_one(
                cur,
                '''
INSERT INTO travel_log.item (fk_album, image, ts, lat, lon, zoom)
VALUES (%(aid)s, %(image)s, %(ts)s, %(lat)s, %(lon)s, %(zoom)s)
RETURNING id_item
                ''',
                {
                    'aid': aid,
                    'image': rel_path,
                    'ts': meta_data['date_time'],
                    'lat': meta_data['lat'],
                    'lon': meta_data['lon'],
                    'zoom': zoom
                }
            )
            result = new_item.id_item
        except Exception as e:
            logger.error(e)

    return result



# -----------------------------------------------------------------------------
# Process and write image

def write_image(storage, img, file_path):
    file_size = get_img_size(img)
    if not is_jpeg(img) or file_size > MAX_ALLOWED_IMAGE_SIZE:
        processed_image = process_image(img, file_size, MAX_ALLOWED_IMAGE_SIZE)
        processed_image.save(file_path, 'JPEG', quality=DEFAULT_JPEG_QUALITY)
    else:
        storage.save(file_path)

def process_image(img, file_size, max_allowed_size):
    resize_factor = 1.0
    if file_size > max_allowed_size:
        resize_factor /= (float(file_size) / float(max_allowed_size))

    width, height = img.size
    new_width, new_height = int(width * resize_factor), int(height * resize_factor)
    return img.resize((new_width, new_height), Image.ANTIALIAS)

def is_jpeg(img):
    return img.format == 'JPEG'

def get_img_size(img):
    mem_file = BytesIO()
    img.save(mem_file, 'JPEG', quality=DEFAULT_JPEG_QUALITY)
    return mem_file.tell()



# -----------------------------------------------------------------------------
# Read meta data

def get_meta_data(img):
    meta = {
        'date_time': None,
        'lat': None,
        'lon': None
    }
    exif = get_exif_data(img)

    if 'DateTime' in exif:
        parsed_date = date_parser(exif['DateTime'])
        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        meta['date_time'] = formatted_date

    lat, lon = get_lat_lon(exif)
    if lat and lon:
        meta['lat'] = lat
        meta['lon'] = lon

    return meta


def get_exif_data(img):
    result = {}
    data = img._getexif()
    if data:
        for tag, val in data.items():
            key = TAGS.get(tag, tag)
            if key == 'GPSInfo':
                result[key] = {GPSTAGS.get(t, t): val[t] for t in val}
            else:
                result[key] = val
    return result


def get_lat_lon(exif):
    lat, lon = None, None

    if 'GPSInfo' in exif:
        info = exif['GPSInfo']
        keys = ('GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef')
        exif_lat, exif_lat_ref, exif_lon, exif_lon_ref = [get_key(info, key) for key in keys]

        if exif_lat and exif_lat_ref and exif_lon and exif_lon_ref:
            lat = dms_to_dd(exif_lat)
            if exif_lat_ref != 'N':
                lat = 0 - lat

            lon = dms_to_dd(exif_lon)
            if exif_lon_ref != 'E':
                lon = 0 - lon

    return lat, lon


def get_key(data, key):
    return key in data and data[key] or None


def dms_to_dd(dms):
    """Converts EXIF coordinates in (degrees, minutes, seconds) format to
    decimal degrees.

    https://en.wikipedia.org/wiki/Geographic_coordinate_conversion
    """
    d, m, s = [float(dms[i][0]) / float(dms[i][1]) for i in range(3)]
    return d + (m / 60.0) + (s / 3600.0)


def _make_file_path(user_name, album_title, fname):
    with db.pg_connection(config['app-database']) as (_, cur, err):
        if err:
            return False

        # Get database id's
        data = db.query_one(
            cur,
            '''
SELECT u.id_user, a.id_album
FROM travel_log.album a
JOIN travel_log.user u ON u.id_user = a.fk_user
WHERE u.user_name = %(user)s AND album_title = %(album)s AND NOT is_deleted
            ''',
            {'user': user_name, 'album': album_title}
        )
        uid, aid = data.id_user, data.id_album

        # Generate file path and name
        fs_path = os.path.join(
            config['storage-engine']['path'],
            str(uid), str(aid))
        if not os.path.isdir(fs_path):
            os.makedirs(fs_path)

        filename = hashlib.sha256(
            '%s-%s-%s-%s' % (uid, aid, time.time(), secure_filename(fname))
        ).hexdigest()
        fs_file = os.path.join(fs_path, '%s.jpg' % filename)
        rel_path = os.path.join(str(uid), str(aid), '%s.jpg' % filename)

        return (fs_file, rel_path, aid)
    return False
