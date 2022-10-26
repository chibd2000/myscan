# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 23:22

try:
    import openpyxl
    import requests
    import abc
    import re
    import chardet
    import logging
    import time
    import random
    import base64
    import json
    import os
    import socket
    import sys
    import copy

    abs_path = os.getcwd() + os.path.sep  # 路径

    from core.request.asynchttp import *
    from core.conf import api_config
    from core.utils.tools import *

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # if sys.platform == 'win32':
    #     loop = asyncio.ProactorEventLoop()
    #     asyncio.set_event_loop(loop)

    requests.packages.urllib3.disable_warnings()
except ImportError as e:
    print('import public spider module error, {}'.format(e.__str__()))
    exit(0)
