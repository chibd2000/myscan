# coding=utf-8

import openpyxl

a = [
    {'spider': 'baidu', 'keyword': '后台', 'link': 'https://www.nbcc.cn/jyw/xwdt/201401/t20140106_35963.shtml', 'title': '宁波城市职业技术学院就业网'},
    {'spider': 'baidu', 'keyword': '后台', 'link': 'https://www.nbcc.cn/xxfy/xybg/', 'title': '宁波城市职业技术学院信息学院>>学院办公'},
    {'spider': 'baidu', 'keyword': '后台', 'link': 'https://www.nbcc.cn/jyw/xwdt/201401/t20140106_36148.shtml', 'title': '宁波城市职业技术学院就业网'}]

workbook = openpyxl.load_workbook("C:\\Users\\dell\\Desktop\\自己练手脚本\\MyFrameWork\\nbcc.cn.xlsx")
worksheet = workbook.worksheets[0]
index = 0

while index < len(a):
    web = list()
    web.append(a[index]['spider'])
    web.append(a[index]['keyword'])
    web.append(a[index]['link'])
    web.append(a[index]['title'])
    worksheet.append(web)
    index += 1
workbook.save("C:\\Users\\dell\\Desktop\\自己练手脚本\\MyFrameWork\\nbcc.cn.xlsx")