import json

string = '''
[

{
    "name": [],
    "age": "23",
    "job": "web engineer",
    "motto": "专业前端，不至于前端"
}]
'''


json_list = json.loads(string)

if not json_list['name']:
    print(1111111)
print(json_list)