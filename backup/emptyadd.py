import os
import openpyxl

abs_path = os.getcwd() + os.path.sep

def write_file(web_lists, target, page):
    workbook = openpyxl.load_workbook(abs_path + str(target) + ".xlsx")
    worksheet = workbook.worksheets[page]
    index = 0
    while index < len(web_lists):
        web = list()
        web.append(web_lists[index]['name'])
        web.append(web_lists[index]['url'])
        web.append(web_lists[index]['cms'])
        worksheet.append(web)
        index += 1
    workbook.save(abs_path + str(target) + ".xlsx")
    workbook.close()


write_file([], 'nbcc.cn', 9)
