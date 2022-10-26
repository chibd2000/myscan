# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2020-11-23 20:45

from core.data import gLogger
from core.component.targetmanager import TargetManager
from core.utils.tools import random_md5, create_xlsx
from argparse import ArgumentParser

import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def start(parser: ArgumentParser):
    loop = asyncio.get_event_loop()
    args = parser.parse_args()
    task_name = random_md5()[8:-8]
    try:
        if args.output:
            if args.domain:
                task_name += '_'+args.domain
            gLogger.myscan_info('generate_task_name: %s' % task_name)
            create_xlsx(task_name)
        target_manager = TargetManager.create_target_manager(task_name, parser)
        loop.run_until_complete(target_manager.search())
        loop.run_until_complete(target_manager.scan())
        if args.output:
            gLogger.myscan_info("result_save_in_%s.xlsx" % task_name)
    except KeyboardInterrupt:
        pass
