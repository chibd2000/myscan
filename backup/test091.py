from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import json

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')

browser = webdriver.Chrome()  # 常用的有Chrome()，PhantomJS(),Firefox() 注意大小写

browser.get('https://dns.bufferover.run/dns?q=.beidian.com')

WebDriverWait(browser, 20, 0.5).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))

try:
    json_data = json.loads(browser.find_element_by_tag_name('pre').text)
except:
    json_data = json.loads(browser.find_element_by_tag_name('pre').text)
finally:
    print(json_data['FDNS_A'])
    print(json_data['RDNS'])

    browser.close()

