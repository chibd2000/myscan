# myscan

构建简单的信息搜集/漏洞扫描

实现的功能：<br/>

信息搜集（多线程）：<br/>
1、DNS枚举爆破 <br/>
2、百度关键词爬取 <br/>
3、FOFA SHODAN 域名爬取 C段爬取<br/>
4、子域名内容正则匹配域名<br/>
5、Ctfr证书查询<br/>
6、Masscan+Nmap端口扫描子域名解析的IP<br/>
7、域名DNS解析IP<br/>
8、selenium爬取DNS数据库<br/>

漏洞扫描（多线程进程）：<br/>
1、探测存活（config文件中设定，默认探测80、443端口）<br/>
2、CMS探测（CMS探测两种方法，另外探测shiro，thinkphp等脆弱资产）<br/>
3、敏感路径扫描（只探测脆弱的资产，例如solr phpMyadmin weblogic jboss特征路径）<br/>
4、HTTP/IP未授权探测<br/>
5、NGINX/APACHE解析漏洞<br/>

参考作者：
1、broken_5
2、langzi
