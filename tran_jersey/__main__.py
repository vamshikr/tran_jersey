from aiohttp import web

from tran_jersey.app import init_app


if __name__ == '__main__':
    web.run_app(init_app(), host="127.0.0.1", port=8080, access_log=None)
