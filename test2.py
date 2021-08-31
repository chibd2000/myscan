# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-28 0:00

import asyncio


async def test():
    await asyncio.sleep(1)
    return 1


async def main():
    t = await test()
    print(t)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())

    # a = [{"aaa": 111}, {"bbb": "222"}]
    # for _ in a:
    #     if _.get('aaa'):
    #         _['aaa'] = 333
    # print(a)

    IpPortList = []
    domainList = [
        {'ip': '1.1.1.1', 'port': 80},
        {'ip': '1.1.1.1', 'port': 443},
        {'ip': '1.1.1.1', 'port': 3389},
        {'ip': '1.1.1.1', 'port': 8080},
        {'ip': '2.2.2.2', 'port': 443},
        {'ip': '3.3.3.3', 'port': 7777},
        {'ip': '3.3.3.3', 'port': 8080},
        {'ip': '4.4.4.4', 'port': 9999},
        {'ip': '5.5.5.5', 'port': 8009},
    ]

    for i in domainList:
        _ip = i['ip']
        _port = i['port']
        flag = True
        for j in IpPortList:
            if j['ip'] == i['ip']:
                flag = False
        if flag:
            IpPortList.append({'ip': _ip, 'port': []})

    for j in domainList:
        _ip = j['ip']
        _port = j['port']
        if _port == 443 or _port == 80:
            continue
        flag = True
        for k in IpPortList:
            if k['ip'] == _ip:
                for m in k['port']:
                    if m == _port:
                        flag = False
        if flag:
            for p in IpPortList:
                if p['ip'] == _ip:
                    p['port'].append(_port)
    print(IpPortList)
