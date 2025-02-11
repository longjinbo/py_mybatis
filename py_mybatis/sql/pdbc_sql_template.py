import contextlib
from DBUtils.PooledDB import PooledDB
#from dbutils.pooled_db import PooledDB
from py_mybatis.logger import LOG


class Page(object):
    pageSize: int = None
    pageNum: int = None
    total: int = None
    list: list = None


class RowBound(object):
    def __init__(self, pageNum: int, pageSize: int):
        self.pageSize = pageSize
        self.pageNum = pageNum


"""
基本操作:增删改查,分页
"""


class PdbcSqlTemplate(object):
    def __init__(self, dataSource: PooledDB):
        self.dataSource = dataSource

    """

    when con is not None
    must be commit manually by the calling function

    """

    def update(self, sql: str, con=None, args=None):
        auto_commit = not con
        with self.get_connection(con) as connection:
            cursor = connection.cursor()
            LOG.debug('execute sql {},args {}', sql, args)
            data = {}
            data['columnNum'] = cursor.execute(sql, args)
            data['columnId'] = cursor.lastrowid
            if auto_commit:
                connection.commit()
                cursor.close()
            return data

    def insert_batch(self, sql: str, con=None, args=None):
        auto_commit = not con
        with self.get_connection(con) as connection:
            cursor = connection.cursor()
            LOG.debug('execute sql {},args {}', sql, args)
            data = cursor.executemany(sql, args)
            if auto_commit:
                connection.commit()
                cursor.close()
            return data

    def insert(self, sql: str, con=None, args=None):
        return self.update(sql, con, args)

    def delete(self, sql, con=None, args=None):
        return self.update(sql, con, args)

    def select_one(self, sql: str, con=None, args=None):
        with self.get_connection(con) as connection:
            cursor = connection.cursor()
            LOG.debug('execute sql {},args {}', sql, args)
            cursor.execute(sql, args)
            data = cursor.fetchone()
            cursor.close()
            return data

    def select_list(self, sql: str, row_bound: RowBound = None, con=None, args=None):
        with self.get_connection(con) as connection:
            cursor = connection.cursor()
            if row_bound:
                sql = limit_query(sql, row_bound)
            LOG.debug('execute sql {},args {}'.format(sql, args))
            cursor.execute(sql, args)
            data = cursor.fetchall()
            cursor.close()
            return data

    def select_page(self, sql: str, count_sql: str = None, row_bound: RowBound = None, con=None, args=None):
        with self.get_connection(con) as connection:
            cursor = connection.cursor()
            page_result = Page()
            page_result.pageNum = row_bound.pageNum
            page_result.pageSize = row_bound.pageSize
            if count_sql is None:
                LOG.debug('execute count_sql {},args {}'.format(count_sql, args))
                count_sql = count_query(sql)
                cursor.execute(count_sql, args)
                page_result.total = cursor.fetchone()['count(*)']
            else:
                LOG.debug('execute count_sql {},args {}'.format(count_sql, args))
                cursor.execute(count_sql, args)
                page_result.total = get_one_value(cursor.fetchone())
            sql = limit_query(sql, row_bound)
            LOG.debug('execute sql {},args {}'.format(sql, args))
            cursor.execute(sql, args)
            page_result.list = cursor.fetchall()
            cursor.close()
        return page_result

    def execute_in_connection(self, fun):
        with self.get_connection() as con:
            return fun(con)

    @contextlib.contextmanager
    def get_connection(self, connection=None):
        auto_close = True
        if connection:
            auto_close = False
        else:
            connection = self.dataSource.connection()
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            if auto_close:
                connection.close()


"""
分页查询
"""


def count_query(sql: str):
    return "select count(*) from ( " + sql + " ) temp"


def limit_query(sql: str, row_bound: RowBound):
    start = (row_bound.pageNum - 1) * row_bound.pageSize
    return sql + " limit {},{}".format(start, row_bound.pageSize)


def get_one_value(count_dict: dict):
    for count in count_dict.values():
        return count
