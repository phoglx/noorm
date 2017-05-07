import sqlite3
from table import Table


class NoORM(object):
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = lambda cur, row: {key[0]: row[idx] for idx, key in enumerate(cur.description)}
        self.cursor = self.connection.cursor()
        self.commit = self.connection.commit
        self.close = self.connection.close

    def rename_table(self, old_table_name, new_table_name):
        return self.cursor.execute("""alter table {} rename to {}""".format(old_table_name, new_table_name))

    def drop_table(self, table_name):
        return self.cursor.execute("""drop table {}""".format(table_name))

    def get_table_info(self):
        self.cursor.execute("""select * from sqlite_master where type = 'table'""")
        table_names = [i['tbl_name'] for i in self.cursor.fetchall()]
        db_info = {}
        for tbl_name in table_names:
            self.cursor.execute("""PRAGMA TABLE_INFO({})""".format(tbl_name))
            cfo = [i for i in self.cursor.fetchall()]
            db_info[tbl_name] = {c['name']: c['cid'] for c in cfo}
        return db_info

    def dump(self):
        result = {}
        for tablename in self.get_table_info().keys():
            self.cursor.execute("""select * from {}""".format(tablename))
            result[tablename] = self.cursor.fetchall()
        return result

    def __getitem__(self, tablename):
        return Table(self, tablename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()
