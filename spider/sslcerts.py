# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 22:23

from core.data import gLogger
from spider import BaseSpider
from core.setting import CONCURRENCY
from async_timeout import timeout
from queue import Queue
import ssl
import asyncio


def get_ssl_context():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations('pymotw.crt')
    return ssl_context


class SSLSpider(BaseSpider):
    def __init__(self, domain, name, domain_list):
        super().__init__()
        self.source = 'SSLSpider'
        self.domain = domain
        self.name = name
        self.ssl_context = get_ssl_context()
        self.queue = Queue(-1)
        for _ in domain_list:
            self.queue.put(_)

    async def get_certs(self, semaphore):
        async with semaphore:
            try:
                with timeout(10):
                    domain = self.queue.get()
                    reader, writer = await asyncio.open_connection(domain, 443, ssl=self.ssl_context)
                    if writer:
                        writer.close()
                    certs = writer.transport.get_extra_info('peercert')
                    cert_domain_list = [_[1] for _ in certs['subjectAltName']]
                    for cert_domain in cert_domain_list:
                        self.res_list.append(cert_domain.strip('*.'))
            except Exception:
                pass
            finally:
                self.queue.task_done()

    async def spider(self):
        semaphore = asyncio.Semaphore(CONCURRENCY)
        task_list = []
        for _ in range(self.queue.qsize()):
            task_list.append(asyncio.create_task(self.get_certs(semaphore)))
        await asyncio.gather(*task_list)
        self.queue.join()
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    asyncio.run(SSLSpider('www.baidu.com', '1e2e1e1eds12', ['www.baidu.com', 'huolala.cn']).main())
