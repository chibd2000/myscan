# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 18:06

import re
import ssl
#
# cert = ssl.get_server_certificate(('www.4399.com',443))
# x509 = M2Crypto.X509.load_cert_string(cert)
#
# cert_val = x509.get_subject().as_text()
# cnames = cert_val.split('CN=')[1]
# if len(cnames) > 0:
#     print(cnames)
text = """
request_domain: {
    item: [
        "https://act.huolala.cn",
        "https://ads-log.huolala.cn",
        "https://api.map.baidu.com",
        "https://apis.map.qq.com",
        "https://cdn.moheweb.com",
        "https://charter.huolala.cn",
        "https://component-biz-pre.huolala.cn",
        "https://component-biz-stg.huolala.cn",
        "https://component-biz.huolala.cn",
        "https://cos.ap-shanghai.myqcloud.com",
        "https://coupe-api.huolala.work",
        "https://coupe-static.huolala.cn",
        "https://fp.fraudmetrix.cn",
        "https://fptest.fraudmetrix.cn",
        "https://hpay-cashiercore-pre.huolala.cn",
        "https://hpay-cashiercore-stg.huolala.cn",
        "https://hpay-cashiercore.huolala.cn",
        "https://log.aldwx.com",
        "https://uappweb-pre.huolala.cn",
        "https://uappweb.huolala.cn",
        "https://uba-dev.huolala.cn",
        "https://uba.huolala.cn",
        "https://web.sdk.qcloud.com",
        "https://webappsocket-dev.huolala.cn",
        "https://webappsocket-stg.huolala.cn",
        "https://webappsocket.huolala.cn",
        "https://webim.tim.qq.com",
        "https://wxa-dev.huolala.cn",
        "https://wxa-gra.huolala.cn",
        "https://wxa-pre.huolala.cn",
        "https://wxa-stg.huolala.cn",
        "https://wxa.huolala.cn",
    ]
}
};"""


t = re.search(r"item: (\[[\s\S]*\])", text, re.S | re.I).group(1)
print(eval(t))




