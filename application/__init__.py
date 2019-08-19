# -*- coding:utf-8 -*-
"""
项目入口，app初始化
"""

from aiohttp import web


def create_app(argv):
    """
    创建初始化web服务器
    :param argv: 参数
    :return:
    """
    server = web.Application()

    async def hello(request):
        return web.Response(text='{code: 200, msg: "测试"}')
    server.add_routes([web.get('/', hello)])
    return server

