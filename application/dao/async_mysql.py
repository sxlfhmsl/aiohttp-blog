# -*- coding: utf-8 -*-
"""
对aiomysql的二次封装，非ORM进行的操作
"""


import aiomysql


class MySqlOp:
    """
    mysql的没有使用orm的操作
    """

    s_instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.s_instance:
            cls.s_instance = super(MySqlOp, cls).__new__(cls, *args, **kwargs)
        return cls.s_instance

    def __init__(self):
        if hasattr(self, '_db_pool'):
            return
        self._db_pool = None

    async def init_mysql(self, config=None):
        """
        初始化，所有其他操作的第一步
        :param config:
        """
        if not config or not getattr(config, 'loop'):
            raise Exception('配置参数不正确，存在问题')
        self._db_pool = await aiomysql.create_pool(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            minsize=config.minsize,
            maxsize=config.maxsize,
            db=config.db,
            loop=config.loop,
            charset=config.charset,
            cursorclass=config.cursor_class)

    def _get_pool(self):
        """
        获取连接池
        :return:
        """
        if not self._db_pool:
            raise Exception('MySql连接池未初始化')
        return self._db_pool

    async def op_select(self, sql_str, *args):
        """
        查询操作
        :param sql_str: sql语句
        :param args: 参数列表
        :return: 执行结果
        """
        with await self._get_pool() as conn:
            cur = await conn.cursor()
            await cur.execute(sql_str, *args)
            await cur.close()
            return await cur.fetchall()

    async def op_insert(self, sql_str, *args):
        """
        插入操作
        :param sql_str: sql语句
        :param args: 参数列表
        :return: 执行结果
        """
        with await self._get_pool() as conn:
            cur = await conn.cursor()
            result = await cur.execute(sql_str, *args)
            await conn.commit()
            await cur.close()
            return result

