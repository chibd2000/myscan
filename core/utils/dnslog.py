# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 21:44
import asyncio

import requests
from core.exception.ceye import CeyePrivilegeError, EyesPrivilegeError
from core.data import gLogger
from core.data import config_dict
from aiohttp import ClientSession

"""
write in 2021.12.06 18.17 @zpchcbd

写这个原因还是因为weblogic poc的验证，在写weblogic相关的t3反序列化无回显漏洞验证的时候遇到的问题：

1、我把相关的t3反序列化weblogic调试完了之后，想作为poc写上去发现一个问题就是python无法实现完整的t3反序列化，查阅了相关资料，难度比较大。
2、于是打包抓包进行传输，发现t3协议回显通用的方法是通过注册RMI实例，这个包通过wireshark完整了，但是后面请求rmi服务的时候这个自己发现无法
通过抓包发送相同的数据包进行解决了，因为其中分为两个步骤，自己无法实现，最后还是想通过反序列化urlClassLoader进行dns验证吧
"""


class Dnslog(object):
    def __init__(self):
        pass

    def init(self):
        pass

    def _get_session(self):
        pass

    def get_records(self, type, filter):
        pass



class Ceye(Dnslog):
    """
    curl http://api.ceye.io/v1/records?token={token}&type={dns|http}&filter={filter}
    """

    def __init__(self):
        super().__init__()
        self.token = config_dict['ceye']['ceye_api']
        self.session = config_dict['ceye']['ceye_identifier']
        self.domain = 'http://api.ceye.io/v1/records?token={token}&type={type}&filter={filter}'
        self.init()

    def init(self):
        self._get_session()

    async def _get_session(self):
        session = requests.session()
        self.session = session
        resp = session.get('http://dnslog.cn/getdomain.php?t=0.4503404253301704')
        self.domain = resp.text

    def get_records(self, type, filter):
        resp = self.session.get('http://dnslog.cn/getrecords.php?t=0.7209060121871593')


def get_ceye_identifier():
    return config_dict['ceye']['ceye_identifier']


async def ceye_dnslog_verify(type, filter_keyword):
    token = config_dict['ceye']['ceye_api']
    url = 'http://api.ceye.io/v1/records?token={TOKEN}&type={TYPE}&filter={FILTER}'.format(TOKEN=token, TYPE=type, FILTER=filter_keyword)
    try:
        async with ClientSession() as session:
            async with session.get(url=url, verify_ssl=False) as response:
                if response is not None:
                    await asyncio.sleep(2)
                    text = await response.text()
                    if 'Invalid token' in text:
                        raise CeyePrivilegeError from None
                    if filter_keyword in text:
                        return True
                    else:
                        return False
    except CeyePrivilegeError:
        gLogger.myscan_error('please check your dnslog token is Exist.')
        return False
    except Exception:
        return False


def get_eyes_identifier():
    return config_dict['eyes']['eyes_identifier']


async def eyes_dnslog_verify(type, filter_keyword):
    token = config_dict['eyes']['eyes_api']
    url = 'http://eyes.sh/api/{TYPE}/9999/{FILTER}/?token={TOKEN}'.format(TOKEN=token, TYPE=type, FILTER=filter_keyword)
    try:
        async with ClientSession() as session:
            async with session.get(url=url, verify_ssl=False) as response:
                if response is not None:
                    await asyncio.sleep(2)
                    text = await response.text()
                    if 'Invalid token' in text:
                        raise EyesPrivilegeError from None
                    if 'True' in text:
                        return True
                    else:
                        return False
    except EyesPrivilegeError:
        gLogger.myscan_error('please check your dnslog token is Exist.')
        return False
    except Exception:
        return False

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(eyes_dnslog_verify('dns', 'abcdef'))