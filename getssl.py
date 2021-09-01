# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 14:19

import socket
import ssl


s = socket.socket()
s.settimeout(1)
c = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs='./cacert.pem')
c.settimeout(10)
c.connect(('www.geely.com', 443))
cert = c.getpeercert()
dns_domains = [each[1] for each in cert['subjectAltName']]
print(dns_domains)

# SSLCertVerificationError 存在
#