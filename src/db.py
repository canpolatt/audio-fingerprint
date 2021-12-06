import psycopg2
from itertools import izip_longest
from psycopg2.extensions import register_adapter, AsIs
import numpy as np
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)


class PostgreSQLDatabase():
    TABLE_SONGS = 'songs'
    TABLE_FINGERPRINTS = 'fingerprints'
    DB_FILE_NAME = 'db/shazam_demo.db'

    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = psycopg2.connect(dbname="audiodb", user="postgres", password="1234", host="localhost")
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def query(self, query, values=[]):
        self.cur.execute(query, values)

    def executeOne(self, query, values=[]):
        self.cur.execute(query, values)
        return self.cur.fetchone()

    def executeAll(self, query, values):
        self.cur.execute(query, (values,))
        return self.cur.fetchall()

    def buildSelectQuery(self, table, params):
        conditions = []
        values = []

        for k, v in enumerate(params):
            key = v
            value = params[v]
            conditions.append("%s = ?" % key)
            values.append(value)

        conditions = ' AND '.join(conditions)
        query = "SELECT * FROM %s WHERE %s" % (table, conditions)

        return {
            "query": query,
            "values": values
        }

    def findOne(self, params):
        select = self.buildSelectQuery(self.TABLE_SONGS, params)
        return self.executeOne(select['query'], select['values'])

    def findAll(self, table, params):
        select = self.buildSelectQuery(table, params)
        return self.executeAll(select['query'], select['values'])

    def insert(self, table, params):
        keys = ', '.join(params.keys())
        values = params.values()

        query = "INSERT INTO songs (%s) VALUES (?, ?)" % (keys);

        self.cur.execute(query, values)
        self.conn.commit()

        return self.cur.lastrowid

    def insertMany(self, table, columns, values):
        def grouper(iterable, n, fillvalue=None):
            args = [iter(iterable)] * n
            return (filter(None, values) for values
                    in izip_longest(fillvalue=fillvalue, *args))

        for split_values in grouper(values, 1000):
            query="INSERT INTO fingerprints (song_fk,hash_value,offset_value) VALUES(%s,%s,%s)"
            self.cur.executemany(query, split_values)

        self.conn.commit()

    def get_song_hashes_count(self, song_id):
        query = 'SELECT count(*) FROM %s WHERE song_fk = %d' % (self.TABLE_FINGERPRINTS, song_id)
        rows = self.executeOne(query)
        return int(rows[0])

    def get_song_by_filehash(self, filehash):
        return self.findOne({
            "filehash": filehash
        })

    # def add_song(self, filename, filehash):
    # song = self.get_song_by_filehash(filehash)
    # if not song:
    #     song_id = self.insert(self.TABLE_SONGS, {
    #         "name": filename,
    #         "filehash": filehash
    #     })
    # else:
    #     song_id = song[0]

    # return song_id

    def add_song(self, filename, filehash):
        self.cur.execute("INSERT INTO songs (name,filehash) VALUES(%s,%s) RETURNING id", (filename, filehash))
        lastrowid=self.cur.fetchone()[0]
        return lastrowid

    # def store_fingerprints(self, values):
    #     self.insertMany(self.TABLE_FINGERPRINTS,
    #                     ['song_fk', 'hash', 'offset'], values
    #                     )

    def store_fingerprints(self,values):
        for record in values:
            self.cur.execute("INSERT INTO fingerprints (song_fk,hash_value,offset_value) VALUES(%s,%s,%s)", record)
        self.conn.commit()
        return 1

    def get_song_by_id(self, id):
        # return self.findOne({
        #     "id": id
        # })
        self.cur.execute('SELECT * FROM songs WHERE id=%s', [id])
        x = self.cur.fetchone()
        return x
