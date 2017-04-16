from __future__ import absolute_import
from itertools import izip_longest
import Queue

import MySQLdb as mysql
from MySQLdb.cursors import DictCursor

from database import Database


class SQLDatabase(Database):
    """
    Queries:

    1) Find duplicates (shouldn't be any, though):

        select `hash`, `ad_id`, `offset`, count(*) cnt
        from fingerprints
        group by `hash`, `ad_id`, `offset`
        having cnt > 1
        order by cnt asc;

    2) Get number of hashes by ad:

        select ad_id, ad_name, count(ad_id) as num
        from fingerprints
        natural join ads
        group by ad_id
        order by count(ad_id) desc;

    3) get hashes with highest number of collisions

        select
            hash,
            count(distinct ad_id) as n
        from fingerprints
        group by `hash`
        order by n DESC;

    => 26 different ads with same fingerprint (392 times):

        select ads.ad_name, fingerprints.offset
        from fingerprints natural join ads
        where fingerprints.hash = "08d3c833b71c60a7b620322ac0c0aba7bf5a3e73";
    """

    type = "mysql"

    # tables
    FINGERPRINTS_TABLENAME = "fingerprints"
    ADS_TABLENAME = "ads"

    # fields
    FIELD_FINGERPRINTED = "fingerprinted"

    # creates
    CREATE_FINGERPRINTS_TABLE = """
        CREATE TABLE IF NOT EXISTS `%s` (
             `%s` binary(10) not null,
             `%s` mediumint unsigned not null,
             `%s` int unsigned not null,
         INDEX (%s),
         UNIQUE KEY `unique_constraint` (%s, %s, %s),
         FOREIGN KEY (%s) REFERENCES %s(%s) ON DELETE CASCADE
    ) ENGINE=INNODB;""" % (
        FINGERPRINTS_TABLENAME, Database.FIELD_HASH,
        Database.FIELD_AD_ID, Database.FIELD_OFFSET, Database.FIELD_HASH,
        Database.FIELD_AD_ID, Database.FIELD_OFFSET, Database.FIELD_HASH,
        Database.FIELD_AD_ID, ADS_TABLENAME, Database.FIELD_AD_ID
    )

    CREATE_ADS_TABLE = """
        CREATE TABLE IF NOT EXISTS `%s` (
            `%s` mediumint unsigned not null auto_increment,
            `%s` varchar(250) not null,
            `%s` tinyint default 0,
            `%s` binary(20) not null,
            `%s` mediumint default 0,
        PRIMARY KEY (`%s`),
        UNIQUE KEY `%s` (`%s`)
    ) ENGINE=INNODB;""" % (
        ADS_TABLENAME, Database.FIELD_AD_ID, Database.FIELD_ADNAME, FIELD_FINGERPRINTED,
        Database.FIELD_FILE_SHA1, Database.FIELD_DURATION,
        Database.FIELD_AD_ID, Database.FIELD_AD_ID, Database.FIELD_AD_ID,
    )

    # inserts (ignores duplicates)
    INSERT_FINGERPRINT = """
        INSERT IGNORE INTO %s (%s, %s, %s) values
            (UNHEX(%%s), %%s, %%s);
    """ % (FINGERPRINTS_TABLENAME, Database.FIELD_HASH, Database.FIELD_AD_ID, Database.FIELD_OFFSET)

    INSERT_AD = "INSERT INTO %s (%s, %s, %s) values (%%s, UNHEX(%%s), %%s);" % (
        ADS_TABLENAME, Database.FIELD_ADNAME, Database.FIELD_FILE_SHA1, Database.FIELD_DURATION)

    # selects
    SELECT = """
        SELECT %s, %s FROM %s WHERE %s = UNHEX(%%s);
    """ % (Database.FIELD_AD_ID, Database.FIELD_OFFSET, FINGERPRINTS_TABLENAME, Database.FIELD_HASH)

    SELECT_MULTIPLE = """
        SELECT HEX(%s), %s, %s FROM %s WHERE %s IN (%%s);
    """ % (Database.FIELD_HASH, Database.FIELD_AD_ID, Database.FIELD_OFFSET,
           FINGERPRINTS_TABLENAME, Database.FIELD_HASH)

    SELECT_ALL = """
        SELECT %s, %s FROM %s;
    """ % (Database.FIELD_AD_ID, Database.FIELD_OFFSET, FINGERPRINTS_TABLENAME)

    SELECT_AD = """
        SELECT %s, %s, HEX(%s) as %s FROM %s WHERE %s = %%s;
    """ % (Database.FIELD_ADNAME, Database.FIELD_DURATION, Database.FIELD_FILE_SHA1, Database.FIELD_FILE_SHA1, ADS_TABLENAME, Database.FIELD_AD_ID)

    SELECT_NUM_FINGERPRINTS = """
        SELECT COUNT(*) as n FROM %s
    """ % (FINGERPRINTS_TABLENAME)

    SELECT_UNIQUE_AD_IDS = """
        SELECT COUNT(DISTINCT %s) as n FROM %s WHERE %s = 1;
    """ % (Database.FIELD_AD_ID, ADS_TABLENAME, FIELD_FINGERPRINTED)

    SELECT_ADS = """
        SELECT %s, %s, HEX(%s) as %s FROM %s WHERE %s = 1;
    """ % (Database.FIELD_AD_ID, Database.FIELD_ADNAME, Database.FIELD_FILE_SHA1, Database.FIELD_FILE_SHA1,
           ADS_TABLENAME, FIELD_FINGERPRINTED)

    # drops
    DROP_FINGERPRINTS = "DROP TABLE IF EXISTS %s;" % FINGERPRINTS_TABLENAME
    DROP_ADS = "DROP TABLE IF EXISTS %s;" % ADS_TABLENAME

    # update
    UPDATE_AD_FINGERPRINTED = """
        UPDATE %s SET %s = 1 WHERE %s = %%s
    """ % (ADS_TABLENAME, FIELD_FINGERPRINTED, Database.FIELD_AD_ID)

    # delete
    DELETE_UNFINGERPRINTED = """
        DELETE FROM %s WHERE %s = 0;
    """ % (ADS_TABLENAME, FIELD_FINGERPRINTED)

    def __init__(self, **options):
        super(SQLDatabase, self).__init__()
        self.cursor = cursor_factory(**options)
        self._options = options

    def after_fork(self):
        # Clear the cursor cache, we don't want any stale connections from
        # the previous process.
        Cursor.clear_cache()

    def setup(self):
        """
        Creates any non-existing tables required for dejavu to function.

        This also removes all ads that have been added but have no
        fingerprints associated with them.
        """
        with self.cursor() as cur:
            cur.execute(self.CREATE_ADS_TABLE)
            cur.execute(self.CREATE_FINGERPRINTS_TABLE)
            cur.execute(self.DELETE_UNFINGERPRINTED)

    def empty(self):
        """
        Drops tables created by dejavu and then creates them again
        by calling `SQLDatabase.setup`.

        .. warning:
            This will result in a loss of data
        """
        with self.cursor() as cur:
            cur.execute(self.DROP_FINGERPRINTS)
            cur.execute(self.DROP_ADS)

        self.setup()

    def delete_unfingerprinted_ads(self):
        """
        Removes all ads that have no fingerprints associated with them.
        """
        with self.cursor() as cur:
            cur.execute(self.DELETE_UNFINGERPRINTED)

    def get_num_ads(self):
        """
        Returns number of ads the database has fingerprinted.
        """
        with self.cursor() as cur:
            cur.execute(self.SELECT_UNIQUE_AD_IDS)

            for count, in cur:
                return count
            return 0

    def get_num_fingerprints(self):
        """
        Returns number of fingerprints the database has fingerprinted.
        """
        with self.cursor() as cur:
            cur.execute(self.SELECT_NUM_FINGERPRINTS)

            for count, in cur:
                return count
            return 0

    def set_ad_fingerprinted(self, aid):
        """
        Set the fingerprinted flag to TRUE (1) once a ad has been completely
        fingerprinted in the database.
        """
        with self.cursor() as cur:
            cur.execute(self.UPDATE_AD_FINGERPRINTED, (aid,))

    def get_ads(self):
        """
        Return ads that have the fingerprinted flag set TRUE (1).
        """
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_ADS)
            for row in cur:
                yield row

    def get_ad_by_id(self, aid):
        """
        Returns ad by its ID.
        """
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_AD, (aid,))
            return cur.fetchone()

    def insert(self, hash, aid, offset):
        """
        Insert a (sha1, ad_id, offset) row into database.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_FINGERPRINT, (hash, aid, offset))

    def insert_ad(self, adname, file_hash, duration):
        """
        Inserts ad in the database and returns the ID of the inserted record.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_AD, (adname, file_hash, duration))
            return cur.lastrowid

    def query(self, hash):
        """
        Return all tuples associated with hash.

        If hash is None, returns all entries in the
        database (be careful with that one!).
        """
        # select all if no key
        query = self.SELECT_ALL if hash is None else self.SELECT

        with self.cursor() as cur:
            cur.execute(query)
            for aid, offset in cur:
                yield (aid, offset)

    def get_iterable_kv_pairs(self):
        """
        Returns all tuples in database.
        """
        return self.query(None)

    def insert_hashes(self, aid, hashes):
        """
        Insert series of hash => ad_id, offset
        values into the database.
        """
        values = []
        for hash, offset in hashes:
            values.append((hash, aid, offset))

        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                cur.executemany(self.INSERT_FINGERPRINT, split_values)

    def return_matches(self, hashes):
        """
        Return the (ad_id, offset_diff) tuples associated with
        a list of (sha1, sample_offset) values.
        """
        # Create a dictionary of hash => offset pairs for later lookups
        mapper = {}
        for hash, offset in hashes:
            mapper[hash.upper()] = offset

        # Get an iteratable of all the hashes we need
        values = mapper.keys()

        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                # Create our IN part of the query
                query = self.SELECT_MULTIPLE
                query = query % ', '.join(['UNHEX(%s)'] * len(split_values))

                cur.execute(query, split_values)

                for hash, aid, offset in cur:
                    # (aid, db_offset - ad_sampled_offset)
                    yield (aid, offset - mapper[hash])

    def __getstate__(self):
        return (self._options,)

    def __setstate__(self, state):
        self._options, = state
        self.cursor = cursor_factory(**self._options)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in izip_longest(fillvalue=fillvalue, *args))


def cursor_factory(**factory_options):
    def cursor(**options):
        options.update(factory_options)
        return Cursor(**options)
    return cursor


class Cursor(object):
    """
    Establishes a connection to the database and returns an open cursor.


    ```python
    # Use as context manager
    with Cursor() as cur:
        cur.execute(query)
    ```
    """
    _cache = Queue.Queue(maxsize=5)

    def __init__(self, cursor_type=mysql.cursors.Cursor, **options):
        super(Cursor, self).__init__()

        try:
            conn = self._cache.get_nowait()
        except Queue.Empty:
            conn = mysql.connect(**options)
        else:
            # Ping the connection before using it from the cache.
            conn.ping(True)

        self.conn = conn
        self.conn.autocommit(False)
        self.cursor_type = cursor_type

    @classmethod
    def clear_cache(cls):
        cls._cache = Queue.Queue(maxsize=5)

    def __enter__(self):
        self.cursor = self.conn.cursor(self.cursor_type)
        return self.cursor

    def __exit__(self, extype, exvalue, traceback):
        # if we had a MySQL related error we try to rollback the cursor.
        if extype is mysql.MySQLError:
            self.cursor.rollback()

        self.cursor.close()
        self.conn.commit()

        # Put it back on the queue
        try:
            self._cache.put_nowait(self.conn)
        except Queue.Full:
            self.conn.close()
