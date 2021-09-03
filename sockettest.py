# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-03 16:52

import socket
import asyncio

banner = {
    b'http': [b'^HTTP/.*\nServer: Apach', b'^HTTP/.*\nServer: nginx', b'HTTP.*?text/html', b'http.*?</html>'],
    b'ssh': [b'^SSH-.*openssh', b'^ssh-', b'connection refused by remote host.'],
    b'netbios': [b'\xc2\x83\x00\x00\x01\xc2\x8f', b'^y\x08.*browse', b'^y\x08.\x00\x00\x00\x00',
                 b'^\x05\x00\r\x03', b'^\x82\x00\x00\x00', b'\x83\x00\x00\x01\x8f'],
    b'backdoor-fxsvc': [b'^500 Not Loged in'],
    b'backdoor-shell': [b'^sh[$#]'],
    b'bachdoor-shell': [b'[a-z]*sh: .* command not found'],
    b'backdoor-cmdshell': [b'^Microsoft Windows .* Copyright .*>'],
    b'db2': [b'.*SQLDB2RA', b'.*sqldb2ra'],
    b'db2jds': [b'^N\x00', b'^n\x00'],
    b'dell-openmanage': [b'^N\x00\r'],
    b'finger': [b'finger: GET: ', b'^\r\n\tline\t  user', b'line\t user', b'login name: ',
                b'login.*name.*tty.*idle', b'^no one logged on', b'^\r\nwelcome', b'^finger:',
                b'^must provide username', b'finger: get: '],
    b'ftp': [b'^220 .* UserGate', b'^220.*\n331', b'^220.*\n530', b'^220.*ftp', b'^220 .* microsoft .* ftp',
             b'^220 inactivity timer', b'^220 .* usergate', b'^220.*filezilla server', b'^220-', b'^220.*?ftp',
             b'^220.*?filezilla'],
    b'http-iis': [b'^<h1>Bad Request .Invalid URL.</h1>'],
    b'http-jserv': [b'^HTTP/.*Cookie.*JServSessionId'],
    b'http-tomcat': [b'.*Servlet-Engine'],
    b'http-weblogic': [b'^HTTP/.*Cookie.*WebLogicSession'],
    b'http-vnc': [b'^HTTP/.*RealVNC/'],
    b'ldap': [b'^0E', b'^0\x0c\x02\x01\x01a', b'^02\x02\x01', b'^03\x02\x01', b'^08\x02\x01', b'^0\x84',
              b'^0e'],
    b'smb': [b'^\x00\x00\x00.\xc3\xbfSMBr\x00\x00\x00\x00.*', b'^\x00\x00\x00.\xffsmbr\x00\x00\x00\x00.*',
             b'^\x83\x00\x00\x01\x8f'],
    b'msrdp': [b'^\x03\x00\x00\x0b\x06\xc3\x90\x00\x004\x12\x00'],
    b'msrdp-proxy': [b'^nmproxy: Procotol byte is not 8\n$'],
    b'msrpc': [b'\x05\x00\r\x03\x10\x00\x00\x00\x18\x00\x00\x00....\x04\x00\x01\x05\x00\x00\x00\x00$',
               b'^\x05\x00\r\x03\x10\x00\x00\x00\x18\x00\x00\x00\x00\x00',
               b'\x05\x00\r\x03\x10\x00\x00\x00\x18\x00\x00\x00....\x04\x00\x01\x05\x00\x00\x00\x00$'],
    b'mssql': [b';MSSQLSERVER;', b'^\x05n\x00', b'^\x04\x01', b';mssqlserver;', b'mssqlserver'],
    b'telnet': [b'^\xc3\xbf\xc3\xbe', b'telnet', b'^\xff[\xfa-\xff]',
                b'^\r\n%connection closed by remote host!\x00$'],
    b'mysql': [b"whost '", b'mysql_native_password', b'^\x19\x00\x00\x00\n', b'^,\x00\x00\x00\n', b"hhost '",
               b"khost '", b'mysqladmin', b"whost '", b'^[.*]\x00\x00\x00\n.*?\x00', b'this mysql server',
               b'mariadb server', b'\x00\x00\x00\xffj\x04host'],
    b'mysql-blocked': [b'^\\(\x00\x00'], b'mysql-secured': [b'this MySQL'],
    b'mongodb': [b'^.*version.....([\\.\\d]+)', b'mongodb'],
    b'nagiosd': [b'Sorry, you \\(.*are not among the allowed hosts...',
                 b'sorry, you \\(.*are not among the allowed hosts...'],
    b'nessus': [b'< NTP 1.2 >\nUser:', b'< ntp 1.2 >\nuser:'],
    b'oracle-tns-listener': [b'\\(ADDRESS=\\(PROTOCOL=', b'\\(error_stack=\\(error=\\(code=',
                             b'\\(address=\\(protocol='],
    b'oracle-dbsnmp': [b'^\x00\x0c\x00\x00\x04\x00\x00\x00\x00', b'^\x00\x0c\x00\x00\x04\x00\x00\x00\x00'],
    b'oracle-https': [b'^220- ora', b'^220- ora'],
    b'oracle-rmi': [b'^N\x00\t'],
    b'postgres': [b'^EFATAL'],
    b'rlogin': [b'^\x01Permission denied.\n', b'login: ', b'rlogind: ', b'^\x01permission denied.\n'],
    b'rpc-nfs': [b'^\x02\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00',
                 b'^\x02\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00'],
    b'rpc': [b'^\xc2\x80\x00\x00', b'\x01\x86\xa0', b'\x03\x9beb\x00\x00\x00\x01', b'^\x80\x00\x00'],
    b'rsync': [b'^@RSYNCD:.*', b'^@rsyncd:', b'@rsyncd:'], b'smux': [b'^A\x01\x02\x00', b'^a\x01\x02\x00'],
    b'snmp-public': [b'public\xc2\xa2', b'public\xa2'],
    b'snmp': [b'A\x01\x02', b'a\x01\x02'],
    b'socks': [b'^\x05[\x00-\x08]\x00', b'^\x05[\x00-\x08]\x00'],
    b'ssl': [b'^\x16\x03\x00..\x02...\x03\x00', b'^..\x04\x00.\x00\x02', b'^\x16\x03\x01..\x02...\x03\x01',
             b'^\x16\x03\x00..\x02...\x03\x00', b'ssl.*get_client_hello', b'^-err .*tls_start_servertls',
             b'^\x16\x03\x00\x00j\x02\x00\x00f\x03\x00', b'^\x16\x03\x00..\x02\x00\x00f\x03\x00',
             b'^\x15\x03\x00\x00\x02\x02\\.*', b'^\x16\x03\x01..\x02...\x03\x01',
             b'^\x16\x03\x00..\x02...\x03\x00'], b'sybase': [b'^\x04\x01\x00', b'^\x04\x01\x00'],
    b'tftp': [b'^\x00[\x03\x05]\x00', b'^\x00[\x03\x05]\x00'],
    b'uucp': [b'^login: password: ', b'^login: password: '],
    b'vnc': [b'^RFB.*', b'^rfb'],
    b'webmin': [b'^0\\.0\\.0\\.0:.*:[0-9]', b'.*miniserv', b'^0\\.0\\.0\\.0:.*:[0-9]'],
    b'websphere-javaw': [b'^\x15\x00\x00\x00\x02\x02\n', b'^\x15\x00\x00\x00\x02\x02\n'],
    b'xmpp': [b"^\\<\\?xml version='1.0'\\?\\>"],
    b'backdoor': [b'^500 not loged in', b'get: command', b'sh: get:', b'^bash[$#]', b'^sh[$#]',
                  b'^microsoft windows'],
    b'bachdoor': [b'*sh: .* command not found'],
    b'rdp': [b'^\x00\x01\x00.*?\r\n\r\n$', b'^\x03\x00\x00\x0b', b'^\x03\x00\x00\x11',
             b'^\x03\x00\x00\x0b\x06\xd0\x00\x00\x12.\x00$',
             b'^\x03\x00\x00\x17\x08\x02\x00\x00z~\x00\x0b\x05\x05@\x06\x00\x08\x91j\x00\x02x$',
             b'^\x03\x00\x00\x11\x08\x02..}\x08\x03\x00\x00\xdf\x14\x01\x01$',
             b'^\x03\x00\x00\x0b\x06\xd0\x00\x00\x03.\x00$', b'^\x03\x00\x00\x0b\x06\xd0\x00\x00\x00\x00\x00',
             b'^\x03\x00\x00\x0e\t\xd0\x00\x00\x00[\x02\xa1]\x00\xc0\x01\n$',
             b'^\x03\x00\x00\x0b\x06\xd0\x00\x004\x12\x00'],
    b'rdp-proxy': [b'^nmproxy: procotol byte is not 8\n$'], b'rmi': [b'\x00\x00\x00vinva', b'^n\x00\t'],
    b'postgresql': [b'^EInvalid packet length\0$', b'^efatal'],
    b'imap': [b'^\\* ok.*?imap'],
    b'pop': [b'^\\+ok.*?'],
    b'smtp': [b'^220.*?smtp', b'^554 smtp'],
    b'rtsp': [b'^rtsp/'],
    b'sip': [b'^sip/'],
    b'nntp': [b'^200 nntp'],
    b'sccp': [b'^\x01\x00\x00\x00$'],
    b'squid': [b'x-squid-error'],
    b'vmware': [b'vmware'],
    b'iscsi': [b'\x00\x02\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'],
    b'redis': [b'^-err unknown command', b'^-err wrong number of arguments', b'^-denied redis is running'],
    b'memcache': [b'^error\r\n'],
    b'websocket': [b'server: websocket'],
    b'https': [b'instead use the https scheme to accesshttps', b'http request to an https server',
               b'location: https'],
    b'svn': [b'^\\( success \\( 2 2 \\( \\) \\( edit-pipeline svndiff1'],
    b'dubbo': [b'^unsupported command'],
    b'elasticsearch': [b'cluster_name.*elasticsearch'],
    b'rabbitmq': [b'^amqp\x00\x00\t\x01'],
    b'zookeeper': [b'^zookeeper version: '],
    b'jdwp': [b'xxxxxxxxxxxxxxx'],
    b'log4j': [b'xxxxxxxxxxx'],
    b'ajp': [b'^AB\0\x13\x04\x01\x90']
}


async def test():
    reader, writer = await asyncio.open_connection('127.0.0.1', 6377)
    writer.write(b'*1\r\n$4\r\ninfo\r\n\n')
    await writer.drain()

    data = await reader.read(100)
    print(data)
    writer.close()

    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.settimeout(0.7)
    # s.connect(('127.0.0.1', 6377))
    # s.send(b'INFO\r\n')
    # data = s.recv(1024)
    # print(data)

if __name__ == '__main__':
    asyncio.run(test())
