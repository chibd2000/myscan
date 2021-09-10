# coding=utf-8

try:
    import requests
    import logging
    import json
    import time
    import re
    from core.MyAsyncHttp import *
    from spider.common import config
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logging.basicConfig(level=logging.INFO, filemode='a', format="[%(levelname)s]%(asctime)s %(message)s")
    requests.packages.urllib3.disable_warnings()
except:
    print('import public third module error.')
    exit(0)
