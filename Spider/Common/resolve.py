# coding=utf-8
import asyncio
import functools
import dns.resolver
import aiodns
import sys

# DNS解析设置
resolver_nameservers = ['114.114.114.114', '8.8.8.8']
resolver_timeout = 5.0  # 解析超时时间
resolver_lifetime = 30.0  # 解析存活时间
limit_resolve_conn = 50


def dns_resolver():
    """
    dns解析器
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = resolver_nameservers
    resolver.timeout = resolver_timeout
    resolver.lifetime = resolver_lifetime
    return resolver


def dns_query_a(hostname):
    """
    查询A记录

    :param str hostname: 主机名
    :return: 查询结果
    """
    resolver = dns_resolver()
    return resolver.query(hostname, 'A')


def aiodns_resolver():
    """
    异步dns解析器
    """
    return aiodns.DNSResolver(nameservers=resolver_nameservers,
                              timeout=resolver_timeout)


async def aiodns_query_a(hostname, semaphore=None):
    """
    异步查询A记录

    :param str hostname: 主机名
    :param semaphore: 并发查询数量
    :return: 主机名或查询结果或查询异常
    """
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
    """
    解析结果回调处理
    :param future: future对象
    :param index: 下标
    :param datas: 结果集
    """
    try:
        result = future.result()
    except Exception as e:
        datas[index]['ips'] = ''  # 解析错误会默认返回空， 获取报错信息str(e.args)
    else:
        if isinstance(result, tuple):
            _, answers = result
            if answers:
                ips = answers[0].host  # 这里解析到的ip就拿一个
                datas[index]['ips'] = str(ips)
            else:
                datas[index]['ips'] = 'No answers'


async def bulk_query_a(datas):
    """
    批量查询A记录

    :param datas: 待查的数据集
    :return: 查询过得到的结果集
    """
    tasks = []
    semaphore = asyncio.Semaphore(limit_resolve_conn)
    for i, data in enumerate(datas):
        if not data.get('ips'):
            subdomain = data.get('subdomain')
            task = asyncio.ensure_future(aiodns_query_a(subdomain, semaphore))
            task.add_done_callback(functools.partial(resolve_callback, index=i, datas=datas))  # 回调
            tasks.append(task)
    if tasks:  # 任务列表里有任务不空时才进行解析
        await asyncio.wait(tasks)  # 等待所有task完成
    return datas
