# myscan

构建简单的信息搜集/漏洞扫描

已经实现的功能：

信息搜集（多线程）：

1、DNS枚举爆破 

2、百度关键词爬取 

3、FOFA SHODAN 域名爬取 C段爬取

4、子域名内容正则匹配域名

5、Ctfr证书查询

6、Masscan+Nmap端口扫描子域名解析的IP

7、域名DNS解析IP

8、selenium爬取DNS数据库

9、第三方的接口搜索引擎查询

漏洞扫描（多线程多进程）：

1、探测存活（config文件中设定，默认探测80、443端口）

2、CMS探测（CMS探测两种方法，另外探测shiro，thinkphp等脆弱资产）

3、敏感路径扫描（只探测脆弱的资产，例如solr phpMyadmin weblogic jboss特征路径）

4、HTTP/IP未授权探测

5、NGINX/APACHE解析漏洞

#用法：

python batch.py -d xxx.cn

![image](https://s1.ax1x.com/2020/06/03/taihIU.md.png)

#参考作者：

1、broken_5

2、langzi

3、ske

#总结：

这个是自己学了python后 将近花了1个多星期的时间写的一个脚本，虽然比不过别人写的 但是也算对自己的一个小小的实现吧，再其中参考别人的代码的时候也学到了许多的构思以及想法！
