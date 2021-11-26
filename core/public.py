# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-26 20:30

try:
    from abc import abstractmethod, ABCMeta
    import logging
    import openpyxl
    import asyncio
    import sys
    import requests
    import abc
    import re
    import chardet
    import time
    import random
    import base64
    import json
    import os
    import socket
    import copy
    from tqdm import tqdm
    from core.request.asynchttp import *
    from spider.common.config import *
    from common.tools import *

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # if sys.platform == 'win32':
    #     loop = asyncio.ProactorEventLoop()
    #     asyncio.set_event_loop(loop)

    requests.packages.urllib3.disable_warnings()
    abs_path = os.getcwd() + os.path.sep  # 路径
except ImportError as e:
    print('import public exploit module error, {}', e.__str__())
    exit(0)