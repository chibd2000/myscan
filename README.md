# myscan

没写完，等九月份去学校了有时间慢慢把要写的都写上...

构建简单的信息搜集/漏洞扫描

已经实现的功能：

信息搜集（多线程+异步IO）：

- 1-DNS枚举爆破 (ksubdomain) 

- 2-百度/Bing关键词爬取 

- 3-FOFA/SHODAN/QUAKE 域名爬取 C段爬取 等。。。。

- 4-ctfr证书查询

- 5-第三方接口查询

- 6-github域名爬取

- 7-域名DNS解析IP

- 8-IP反查域名

- 9-nmap指纹库socket探测开放端口服务

- 10-子域名内容正则匹配域名

- 11-爱企查股权结构查询

中间环节

- 12、探测存活，整理数据，如下格式所示  
```

# 资产IP+端口格式

[+] [ipPortList] [280] [{'ip': '202.103.147.144', 'port': [8080, 8090]}, {'ip': '125.19.57.134', 'port': []}, {'ip': '58.60.230.103', 'port': [8000, 2000]}, {'ip': '202.103.147.169', 'port': [25]}]


# 存储可注入探测参数列表(相似度对比)

[+] [gParamsList] [24] ['http://supporthk.zjhu.xxx.cn/support/news/NewsMain.aspx?type=CenterProfile', 'http://mobdl.support.xxx.edu.cn/support/EReadFiles/AppReleaseDownload/chapter_en.htm?v=5']

# 存储js文件中的js敏感接口

gJavaScriptParamList = []

# 存储资产IP区段分布以及资产IP在指定的区段出现的次数

[+] [gIpSegmentList] [228] [{'ipSegment': '183.232.187.0/24', 'ip': ['183.232.187.210', '183.232.187.201', '183.232.187.197'], 'num': 3}, {'ipSegment': '218.2.178.0/24', 'ip': ['218.2.178.29', '218.2.178.22', '218.2.178.23', '218.2.178.21', '218.2.178.15', '218.2.178.14', '218.2.178.27', '218.2.178.32'], 'num': 8}]

# ASN记录

[gAsnList] [28] [9498, 11419, 3356, 14618, 45090, 3491, 4134, 58541, 45102, 58543, 15169, 58952, 36937, 9929, 37963, 4812, 4808, 17621, 17623, 23650, 4837, 56040, 132203, 1267, 7160, 16509]

# 显示/隐形资产IP
 
[gIpList] [343] ['183.232.187.210', '218.2.178.29', '103.27.119.242', '59.83.221.138', '111.3.79.208', '61.132.54.18', '58.60.230.102', '47.92.49.128', '58.60.230.42']

# 显示/隐形资产域名

[+] [domainList] [522] ['b2bprodhk.xxx.com.cn', 'out2.xxx.com.cn', 'topicscn.xxx.com.cn', '18.184.132.222:443', 'ilearning.xxx.com.cn', '47.75.103.207:443', 'sslsfshct.xxx.com.cn', 'pantheon-akamaigs1.wpc.edgecastcdn.net.xxx.com.cn', 'support.xxx.com.cn', 'mx10.xxx.com.cn', 'ca.xxx.com.cn', '47.92.49.128', 'guide.xxx.com', 'mx5.xxx.com.cn', '39.98.88.177:443', 'xxxtcm.xxx.com.cn', '47.111.170.47', 'apimes.sc.xxx.com.cn']
```

漏洞扫描（多进程、多线程、异步IO）：

1、CMS框架漏洞

2、端口服务漏洞

3、SQL注入漏洞

#用法：

```angular2
python batch.py -d zjhzu.edu.cn

python batch.py -file topDomainList.txt

python batch.py -u zjhzu.edu.cn -p jira

python batch.py -fofa "cert=\"zjhzu.edu.cn\"" -p jira

python batch.py -quake "cert:\"zjhzu.edu.cn\"" -p jira

python batch.py -shodan "ssl:\"zjhzu.edu.cn\"" -p jira

python batch.py -v
```

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

1、基于请求数据的时候实现进度可视化，比如进度条

2、基于fofa/quake 指定关键词 -> 利用探测，有时候新写的EXP需要待验证

3、基于C段 -> 利用探测，指定IP段多资产存活需要进行单独探测


