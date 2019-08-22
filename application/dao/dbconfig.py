# -*- coding: utf-8 -*-
"""
异步数据库，配置参数
"""


import aiomysql


class MySqlConfig:
    host = 'localhost'
    port = 3306
    user = 'root'
    password = 'admin123'
    minsize = 5
    maxsize = 30
    db = 'aiohttp-blog'
    loop = None
    charset = 'utf8'
    cursor_class = aiomysql.DictCursor

    @classmethod
    def set_loop(cls, loop):
        cls.loop = loop


class RedisConfig:
    """
    Redis 连接信息
    """
    address = ('localhost', 6379)
    password = 'admin123'
    db = 0
    minsize = 5
    maxsize = 30
    encoding = 'utf8'
    loop = None

    @classmethod
    def set_loop(cls, loop):
        """
        设置事件循环loop
        :param loop: 循环loop
        :return:
        """
        cls.loop = loop

