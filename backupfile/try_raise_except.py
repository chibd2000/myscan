import json

string = '''
{
    "name": [],
    "age": "23",
    "job": "web engineer",
    "motto": "专业前端，不至于前端"
}
'''

json_data = json.loads(string)
print(json_data)

try:
    if not json_data['name']:
        pass
        # raise KeyError("{} {} {} 无数据爬取 结束自身线程!!!")
except KeyError:
    print(1)
    exit(0)
