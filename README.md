# myscan

构建简单的信息搜集/漏洞扫描

已经实现的功能：

信息搜集（多线程+异步IO）：

1、DNS枚举爆破 (ksubdomain)

2、百度/Bing关键词爬取 

3、FOFA/SHODAN/QUAKE 域名爬取 C段爬取 等。。。。

4、子域名内容正则匹配域名

5、Ctfr证书查询

6、Masscan+Nmap端口扫描子域名解析的IP

7、域名DNS解析IP

8、IP反查域名

9、selenium爬取dns.bufferouver数据库

10、github域名爬取

11、第三方接口引擎查询

12、天眼查股权结构查询



====清洗数据====



漏洞扫描（异步IO）：

1、探测存活（config文件中设定，默认探测80、443端口）

2、CMS探测 -> 定向EXP利用

3、敏感路径扫描（只探测脆弱的资产，例如solr phpMyadmin weblogic jboss特征路径）

4、HTTP/IP未授权探测

5、sqlmap调用SQL检测

6、敏感端口反序列化探测

#用法：

python batch.py -d zjhzu.edu.cn

python batch.py -f zjhzu.edu.cn

python batch.py -d zjhzu.edu.cn

python batch.py -d zjhzu.edu.cn

python batch.py -v zjhzu.edu.cn

#参考作者：

1、broken_5

2、langzi

3、ske

#总结：

1、这个是自己学了python后 将近花了1个多星期的时间写的一个脚本，虽然比不过别人写的 但是也算对自己的一个小小的实现吧，再其中参考别人的代码的时候也学到了许多的构思以及想法！

2、前人栽树，后人乘凉，感谢ske大师兄

#参考文章：

1、https://xz.aliyun.com/t/9508

2、https://www.t00ls.net/viewthread.php?tid=62399

3、
