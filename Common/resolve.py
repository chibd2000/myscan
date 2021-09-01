# coding=utf-8
import asyncio
import functools
import dns.resolver
import aiodns
import sys
from common.tools import *

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# DNS解析设置
resolver_nameservers = ['114.114.114.114', '114.114.115.115']

# 指定查询的DNS域名服务器

resolver_timeout = 5.0  # 解析超时时间
resolver_lifetime = 30.0  # 解析存活时间
limit_resolve_conn = 50


def dns_resolver():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = resolver_nameservers
    resolver.timeout = resolver_timeout
    resolver.lifetime = resolver_lifetime
    return resolver


def dns_query_a(hostname):
    resolver = dns_resolver()
    return resolver.query(hostname, 'A')


def aiodns_resolver():
    return aiodns.DNSResolver(nameservers=resolver_nameservers,
                              timeout=resolver_timeout)


async def aiodns_query_a(hostname, semaphore=None):
    if semaphore is None:
        resolver = aiodns_resolver()
        answers = await resolver.query(hostname, 'A')
        return hostname, answers
    else:
        async with semaphore:
            resolver = aiodns_resolver()
            answers = await resolver.query(hostname, 'A')
            return hostname, answers


def resolve_callback(future, index, datas):
    try:
        result = future.result()
    except Exception as e:
        datas[index]['ip'] = ''  # 解析错误会默认返回空， 获取报错信息str(e.args)
    else:
        if isinstance(result, tuple):
            _, answers = result
            if answers:
                ips = answers[0].host  # 这里解析到的ip就拿一个
                datas[index]['ip'] = str(ips)
            # else:
            #     datas[index]['ip'] = 'No answers'


async def bulk_query_a(datas):
    tasks = []
    semaphore = asyncio.Semaphore(limit_resolve_conn)
    for i, data in enumerate(datas):
        if not data.get('ip'):
            subdomain = data.get('subdomain')
            task = asyncio.ensure_future(aiodns_query_a(subdomain, semaphore))
            task.add_done_callback(functools.partial(resolve_callback, index=i, datas=datas))  # 回调
            tasks.append(task)
    if tasks:  # 任务列表里有任务不空时才进行解析
        await asyncio.wait(tasks)  # 等待所有task完成
    return getUniqueList(datas)


if __name__ == '__main__':
    domainList = ['120.79.66.58', 'www.zjhu.edu.cn', 'www.zjhu.edu.cn']
    ip2domainList = []
    for i in domainList:
        aDict = {'subdomain': i, 'ip': ''}
        ip2domainList.append(aDict)

    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    task = bulk_query_a(ip2domainList)  # 解析域名地址A记录
    t = loop.run_until_complete(task)
    print(t)
