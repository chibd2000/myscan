

import execjs

a = '''
function a(){
    document.getElementById('challenge-form');
    return 1;
}
'''

code = 'const jsdom = require("jsdom");' \
       'const { JSDOM } = jsdom;' \
       'const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);' \
       'window = dom.window;' \
       'document = window.document;' \
       'XMLHttpRequest = window.XMLHttpRequest;' + a

node = execjs.get()
func = node.compile(code, cwd=r"C:\Users\dell\AppData\Roaming\npm\node_modules")
t = func.call('a')
print(t)
