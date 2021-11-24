# coding=utf-8

try:
    import requests
    import logging
    import json
    import time
    import re
    from core.request.asynchttp import *
    from spider.common import config
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    print('import public third module error.')
    exit(0)
