# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08

from queue import Queue
from core.data import gLogger
from core.setting import CONCURRENCY
from spider import BaseSpider
from bs4 import BeautifulSoup

import aiohttp
import asyncio
import time

class AliveSpider(BaseSpider):

    def __init__(self, domain, name, domain_list):
        super().__init__()
        self.source = 'AliveSpider'
        self.domain = domain
        self.name = name
        self._is_continue = True
        self.alive_list = list()  # 最终存活域名
        self.queue = Queue(-1)
        self.start_time = time.time()
        self.all_task_num = 0
        self.remain_task_num = 0
        self.finish_task_num = 0
        self.error_task_num = 0
        for domain in domain_list:
            if 'http://' in domain:
                self.queue.put(domain)
                self.all_task_num += 1
            elif 'https://' in domain:
                self.queue.put(domain)
                self.all_task_num += 1
            else:
                self.queue.put(f'http://{domain}')
                self.queue.put(f'https://{domain}')
                self.all_task_num += 2

    async def _getAlive(self, semaphore):
        url = self.queue.get()
        try:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, verify_ssl=False, timeout=60) as response:
                        if response is not None:
                            await asyncio.sleep(2)
                            text = await response.text()
                            title = self._getTitle(BeautifulSoup(text, 'lxml'))
                            status = response.status
                            x_power_by_header = response.headers.get('X-Powered-By', '')
                            self.res_list.append({'url': url, 'status': status, 'title': title, 'frame': x_power_by_header})
                            self.alive_list.append(url)
                            self.finish_task_num += 1
        except (ConnectionRefusedError, TimeoutError) as e:
            # print('[-] curl {} error, the error is {}.'.format(url, e.args))
            self.error_task_num += 1
        except aiohttp.ClientPayloadError:
            # 协议问题导致的无法访问，这种情况下这个域名如果通过正常的浏览器访问还是可以正常访问的
            self.res_list.append({'url': url, 'status': '手动访问', 'title': '', 'frame': ''})
            gLogger.warn('curl {} error, the error is payloadError, check HTTP 1.1.'.format(url))
            self.error_task_num += 1
        except Exception as e:
            # print('[-] curl {} error, the error is {}.'.format(url, e.args))
            self.error_task_num += 1
        finally:
            self.queue.task_done()

    def _getTitle(self, soup):
        """
        这个方法后面加的，我发现如果简单的通过正则来获取标题title的话获取的不完全，虽然把信息搜集过来了，但是如果主要的标题看不见的话，
        还是需要去访问来观察，有时候如果标题获取的完全的话，那么就能更多的省去访问的时间
        """
        title = soup.title
        if title:
            return title.text

        # for springboot
        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc.get('content')

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word.get('content')

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def print_progross(self):
        self.spend_time = time.time() - self.start_time
        print('%s found | %s error | %s remaining | %s scanned in %.2f seconds.(total %s)' % \
              (self.finish_task_num,
               self.error_task_num,
               self.all_task_num - self.finish_task_num - self.error_task_num,
               self.all_task_num - self.remain_task_num,
               self.spend_time,
               self.all_task_num))

    async def _print_progross(self):
        while self._is_continue:
            await asyncio.sleep(60)
            self.print_progross()

    async def spider(self):
        task_list = []
        semaphore = asyncio.Semaphore(CONCURRENCY)
        asyncio.ensure_future(self._print_progross())
        for _ in range(self.all_task_num):
            task_list.append(asyncio.create_task(self._getAlive(semaphore)))
        await asyncio.gather(*task_list)
        self.queue.join()
        self.alive_list = list(set(self.alive_list))
        self.print_progross()
        self._is_continue = False
        print(self.res_list)
        self.write_file(self.get_unique_list(self.res_list), 13)

    async def main(self):
        await self.spider()
        return self.alive_list


if __name__ == '__main__':
    alive = AliveSpider('test.com', 'test', [])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
