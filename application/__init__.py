# -*- coding:utf-8 -*-
"""
项目入口，app初始化
"""

from aiohttp import web
import asyncio


async def create_app(argv):
    """
    创建初始化web服务器
    :param argv: 参数
    :return:
    """
    from .dao.async_redis import RedisOp
    server = web.Application()
    await init_db()

    async def hello(request):
        return web.Response(text=str(await RedisOp().keys()))
    server.add_routes([web.get('/', hello)])
    return server


async def init_db():
    from .dao.async_redis import RedisOp
    from .dao.async_mysql import MySqlOp
    from .dao.dbconfig import AioMysqlConfig, AioRedisConfig
    # 初始化mysql和redis
    loop = asyncio.get_event_loop()
    AioMysqlConfig.set_loop(loop)
    AioRedisConfig.set_loop(loop)
    await RedisOp().init_redis(AioRedisConfig)
    await MySqlOp().init_mysql(AioMysqlConfig)
