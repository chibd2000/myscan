# coding:utf-8

#from Exploit.Exploit import *

import http.client
import socket
import time
import pymongo
import requests
import re
from threading import Thread
import multiprocessing
from multiprocessing import Manager
requests.packages.urllib3.disable_warnings()

timeout = 3
socket.setdefaulttimeout(timeout)


class IpUnauth(object):

    def __init__(self, result_queue, ip):
        self.user_list = ['root', 'sa', 'system', 'Administrtor', 'ubuntu']
        self.password_list = ['root', 'sa', 'admin', 'test', 'mysql', '123456', 'admin1234', 'admin12345', '000000', '987654321', '1234', '12345']
        self.headers = {"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
        self.result_queue = result_queue
        self._ip = ip

    def exploit(self):
        '''Mongodb数据库未授权访问漏洞'''
        try:
            conn = pymongo.MongoClient(str(self._ip), 27017)
            dbname = conn.list_database_names()
            if dbname:
                self.result_queue.put("Mongodb数据库未授权访问漏洞 : ' + str(ip) + ':27017'")
        except:
            pass
        finally:
            conn.close()

        '''Mongodb数据库未授权访问漏洞'''
        try:
            conn = pymongo.MongoClient(str(self._ip), 27018)
            dbname = conn.list_database_names()
            if dbname:
                self.result_queue.put("Mongodb数据库未授权访问漏洞 : ' + str(ip) + ':27017'")

        except:
            pass
        finally:
            conn.close()

        '''Redis未授权'''
        try:
            s = socket.socket()
            s.connect((str(self._ip), 6379))
            s.send(b"INFO\r\n")
            result = s.recv(1024)
            if b"redis_version" in result:
                self.result_queue.put('Redis数据库未授权访问漏洞 : ' + str(ip) + ':6379')
        except:
            pass
        finally:
            s.close()

        '''Redis弱口令漏洞'''
        try:
            s = socket.socket()
            s.connect((ip, int(6379)))
            s.send(b"INFO\r\n")
            result = s.recv(1024)
            if b"Authentication" in result:
                for _pass in self.password_list:
                    s = socket.socket()
                    s.connect((self._ip, int(6379)))
                    s.send("AUTH %s\r\n" % _pass)
                    result = s.recv(1024)
                    if '+OK' in result:
                        self.result_queue.put('Redis弱口令漏洞 : ' + str(self._ip) + ':6379|' + str(_pass))
        except:
            pass
        finally:
            s.close()

        '''ZooKeeper未授权访问漏洞'''
        try:
            s = socket.socket()
            s.connect((str(self._ip), 2181))
            s.send(b"envi")
            result = s.recv(1024)
            if b"zookeeper.version" in result:
                self.result_queue.put('ZooKeeper未授权访问漏洞 : ' + str(self._ip) + ':2181')
        except:
            pass
        finally:
            s.close()

        '''Elasticsearch未授权访问漏洞'''
        try:
            conn = http.client.HTTPConnection(str(self._ip), 9200, True)
            conn.request("GET", '/_cat/master')
            resp = conn.getresponse()
            if resp.status == 200:
                self.result_queue.put('Elasticsearch未授权访问漏洞 : ' + str(self._ip) + ':9200')
        except:
            pass
        finally:
            s.close()

        '''Memcache未授权访问漏洞'''
        try:
            s = socket.socket()
            s.connect((str(self._ip), 11211))
            s.send(b"stats")
            result = s.recv(1024)
            if b"STAT version" in result:
                self.result_queue.put('Memcache未授权访问漏洞 : ' + str(self._ip) + ':11211')
        except:
            pass
        finally:
            s.close()

        '''iis WebDav未授权，收集的'''
        try:
            s = socket.socket()
            s.connect((self._ip, 80))
            s.send(b"PUT /iisput.txt HTTP/1.1\r\nHost: %s:%d\r\nContent-Length: 9\r\n\r\nxxscan0\r\n\r\n" % (self._ip, 80))
            time.sleep(1)
            data = s.recv(1024)
            s.close()
            if 'PUT' in data:
                url = 'http://' + self._ip + ":" + str(80) + '/vultest.txt'
                resp = requests.get(url, Verify=False)
                if 'xxscan0' in resp.text:
                    self.result_queue.put('IIS WebDav未授权上传漏洞 : ' + str(url))
        except:
            pass

        finally:
            s.close()

        '''Docker未授权访问漏洞'''
        try:
            conn = http.client.HTTPConnection(str(self._ip), 2375, True)
            conn.request("GET", '/containers/json')
            resp = conn.getresponse()
            if resp.status == 200 and "HostConfig" in resp.read():
                self.result_queue.put('Docker未授权访问漏洞 : ' + str(self._ip) + ':2375/containers/json')
                # with open('result.txt', 'a+')as aaa:
                #     aaa.write('Docker未授权访问漏洞 : ' + str(ip) + ':2375/containers/json' + '\n')
        except:
            pass
        finally:
            conn.close()

        '''CouchDB未授权访问漏洞'''
        try:
            rr = requests.get(url=str('http://' + str(self._ip) + '/_config'), headers=self.headers, timeout=timeout)
            if "couch" in rr.content:
                self.result_queue.put('CouchDB未授权访问漏洞 : ' + str(rr.url))

                # with open('result.txt', 'a+')as aaa:
                #     aaa.write('CouchDB未授权访问漏洞 : ' + str(rr.url) + '\n')
        except:
            pass

        '''Jenkins未授权访问漏洞'''
        try:
            r_ = []
            r2 = 'http://' + str(self._ip) + '/manage'
            r4 = 'http://' + str(self._ip) + ':8080/manage'
            r_.append(r2)
            r_.append(r4)
            for r_r in r_:
                try:
                    Jenkins_resp = requests.get(url=r_r, headers=self.headers, timeout=timeout)
                    if 'arbitrary' in Jenkins_resp.content:
                        self.result_queue.put('Jenkins未授权访问漏洞 : ' + str(r_r))
                except:
                    pass
        except:
            pass

        '''Hadoop YARN ResourceManager 未授权访问漏洞，这个还没写探测的脚本'''
        try:
            r1_ = []
            r2_ = 'http://' + str(self._ip)
            r4_ = 'http://' + str(self._ip) + ':8088'
            r1_.append(r2_)
            r1_.append(r4_)
            for target in r1_:
                url = target + '/ws/v1/cluster/apps/new-application'
                resp = requests.post(url)
                app_id = resp.json()['application-id']
                if app_id:
                    self.result_queue.put("Hadoop未授权访问漏洞 : " + str(self._ip))
        except:
            pass

        '''rsync未授权访问'''
        try:
            s = socket.socket()
            s.connect(("192.168.1.168", 873))
            s.send(b"@RSYNCD: 31\n")
            s.send(b'\n')
            time.sleep(0.5)
            result = s.recv(1024)
            if result:
                for path_name in re.split('\n', result.decode()):
                    if path_name and not path_name.startswith('@RSYNCD: '):
                        self.result_queue.put("rsync未授权访问 : " + str(self._ip))
        except:
            pass
        finally:
            s.close()

    @property
    def main(self):
        self.exploit()
        for i in range(self.result_queue.qsize()):
            print(self.result_queue.get())


if __name__ == '__main__':
    multiprocessing.freeze_support()

    starttime = time.time()


    list_ = ['192.168.43.10']
    aaa = Manager().Queue()
    # thread_list = []
    # for _ in list_:
    #     xxx = IpUnauth(aaa, _)
    #     thread_list.append(Thread(target=xxx.main))
    #
    # for i in thread_list:
    #     i.start()
    # for i in thread_list:
    #     i.join()


    p = multiprocessing.Pool(10)
    for _ in list_:
        xxx = IpUnauth(aaa, _)
        p.apply_async(xxx.main)
    p.close()
    p.join()

    print(time.time() - starttime)
