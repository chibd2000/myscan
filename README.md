# myscan

没写完，等九月份去学校了有时间慢慢把要写的都写上...

构建简单的信息搜集/漏洞扫描

已经实现的功能：

信息搜集（多线程+异步IO）：

- 1-DNS枚举爆破 (ksubdomain)

- 2-百度/Bing关键词爬取 

- 3-FOFA/SHODAN/QUAKE 域名爬取 C段爬取 等。。。。

- 4-ctfr证书查询

- 5-第三方接口引擎查询

- 6-github域名爬取

- 7-域名DNS解析IP

- 8-IP反查域名

- 9-Masscan+Nmap端口扫描子域名解析的IP

- 10-子域名内容正则匹配域名

- 11-爱企查股权结构查询

中间环节

- 12、探测WEB存活，清理数据，格式为        
```
[
    {"subdomain": "jwc.zjhu.edu.cn", "ip": "1.1.1.1", "port":[7777,8888]},
    {"subdomain": "","ip": "2.2.2.2","port":[]}
]

# 存储可注入探测参数列表(相似度对比)
gWebParamsList = []

# 存储js文件中的js敏感接口
gJavaScriptParamList = []

# 存储资产IP区段分布以及资产IP在指定的区段出现的次数{"111.111.111.0/24":1,"111.111.222.0/24":1}
gIpSegmentDict = {}  

# ASN记录
gAsnList = []

# 显示/隐形资产IP
gIpList = []

```

漏洞扫描（多进程、多线程、异步IO）：

1、CMS框架漏洞

2、端口服务漏洞

3、SQL注入漏洞

#用法：

python batch.py -d zjhzu.edu.cn

python batch.py -file topDomainList.txt

python batch.py -u zjhzu.edu.cn -p jira

python batch.py -fofa "cert=\"zjhzu.edu.cn\"" -p jira

python batch.py -quake "cert:\"zjhzu.edu.cn\"" -p jira

python batch.py -shodan "ssl:\"zjhzu.edu.cn\"" -p jira

python batch.py -v

#总结：

1、学习python

2、前人栽树，后人乘凉，感谢ske大师兄和其他人的项目

#参考文章：

1、https://xz.aliyun.com/t/9508

2、https://www.t00ls.net/viewthread.php?tid=62399

3、https://github.com/0x727/ShuiZe_0x727/

4、https://github.com/shmilylty/OneForAll

5、https://github.com/laramies/theHarvester

6、https://github.com/knownsec/ksubdomain

#需要优化

1、相关进度条展示

2、fofa/quake 指定关键词->利用探测，有时候新写的EXP需要待验证


