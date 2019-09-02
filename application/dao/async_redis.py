# -*- coding: utf-8 -*-
"""
对aioredis的二次封装，提供set，get，通道发布订阅等操作
"""

import aioredis


class RedisOp:
    """
    redis 操作类，提供get，set等， 必须先调用初始化方法
    """
    # 单例模式
    s_instance = None

    def __new__(cls, *args, **kwargs):
        """
        控制唯一实例
        :param args:
        :param kwargs:
        :return:
        """
        if not cls.s_instance:
            cls.s_instance = super(RedisOp, cls).__new__(cls, *args, **kwargs)
        return cls.s_instance

    def __init__(self):
        if hasattr(self, '_RedisOp__redis_pool'):
            # 保持连接池初始化1次
            return
        self.__redis_pool = None

    async def init_redis(self, config=None):
        """
        根据配置config初始化redis，并创建连接池
        所有其他操作的第一步
        :param config: 相关配置参数
        :return:
        """
        if not config or not getattr(config, 'loop'):
            raise Exception('配置参数不正确')
        self.__redis_pool = await aioredis.create_pool(
            address=config.address,
            password=config.password,
            db=config.db,
            minsize=config.minsize,
            maxsize=config.maxsize,
            encoding=config.encoding,
            loop=config.loop,
        )

    def __get_pool(self):
        """
        获取redis连接池
        :return:
        """
        if not self.__redis_pool:
            raise Exception('redis连接池不存在')
        return self.__redis_pool

    async def get_normal(self, key):
        """
        获取键(key)对应的值
        :param key: 键
        :return: 查询到的值
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.get(key)

    async def set_normal(self, key, value, expire_time=None):
        """
        添加或者设置 redis值
        :param key: 键
        :param value: 值
        :param expire_time: 过期时间
        :return: 执行结果
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            if expire_time:
                return await m_redis.setex(key, expire_time, value)
            else:
                return await m_redis.set(key, value)

    async def keys(self, pattern='*'):
        """
        获取按指定条件(pattern)过滤后的key
        :param pattern: 过滤条件
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.keys(pattern=pattern)

    async def remove_items(self, *keys):
        """
        删除keys对应的所有条目
        :param keys: 欲删除的keys
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.delete(*keys)

    async def remove_all(self):
        """
        清空库中的条目
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.flushdb()

    async def get_hash(self, key):
        """
        获取redis中的hash的值
        :param key: 键
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.hgetall(key)

    async def set_hash(self, key, **values):
        """
        设置redis中的hash值
        :param key: 键
        :param values: 值字典
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            return await m_redis.hmset_dict(key, **values)

    async def subscribe_sig(self, channel):
        """
        订阅redis通道
        :param channel:
        :return:
        """
        conn = await self.__get_pool().acquire()
        m_redis = aioredis.Redis(conn)
        channel = await m_redis.subscribe(channel)
        return channel[0], self.__get_pool().release, conn

    async def publish(self, channel, msg):
        """
        发布消息
        :param channel: 通道名
        :param msg: 消息
        :return:
        """
        with await self.__get_pool() as conn:
            m_redis = aioredis.Redis(conn)
            await m_redis.publish(channel, msg)


class RedisSub:
    """
    redis订阅类 _m_channel为通道名称
    """
    _m_channel = 'm_channel'

    def __init__(self):
        self._redis_op = RedisOp()

    async def __aenter__(self):
        self.channel, self.release_cb, self.conn = await self._redis_op.subscribe_sig(self._m_channel)
        return self.channel

    async def __aexit__(self, *exc_info):
        if self.release_cb and self.conn:
            self.channel.close()
            self.release_cb(self.conn)

