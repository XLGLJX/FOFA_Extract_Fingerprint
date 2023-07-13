import requests
from lxml import etree
import base64
import time
import config
from urllib.parse import quote
import chardet

def logo():
    print('''


             /$$$$$$$$ /$$$$$$  /$$$$$$$$ /$$$$$$                                   
            | $$_____//$$__  $$| $$_____//$$__  $$                                  
            | $$     | $$  \ $$| $$     | $$  \ $$                                  
            | $$$$$  | $$  | $$| $$$$$  | $$$$$$$$                                  
            | $$__/  | $$  | $$| $$__/  | $$__  $$                                  
            | $$     | $$  | $$| $$     | $$  | $$                                  
            | $$     |  $$$$$$/| $$     | $$  | $$                                  
            |__/      \______/ |__/     |__/  |__/                                  



                                /$$$$$$            /$$       /$$                    
                               /$$__  $$          |__/      | $$                    
                              | $$  \__/  /$$$$$$  /$$  /$$$$$$$  /$$$$$$   /$$$$$$ 
                              |  $$$$$$  /$$__  $$| $$ /$$__  $$ /$$__  $$ /$$__  $$
                               \____  $$| $$  \ $$| $$| $$  | $$| $$$$$$$$| $$  \__/
                               /$$  \ $$| $$  | $$| $$| $$  | $$| $$_____/| $$      
                              |  $$$$$$/| $$$$$$$/| $$|  $$$$$$$|  $$$$$$$| $$      
                               \______/ | $$____/ |__/ \_______/ \_______/|__/      
                                        | $$                                        
                                        | $$                                        
                                        |__/                                        

                                                                                version:1.01
    ''')    



def preCheckSession():
    checkKeyword="thinkphp"
    searchbs64 = quote(str(base64.b64encode(checkKeyword.encode()), encoding='utf-8'))
    rep = requests.get('https://fofa.info/result?qbase64=' + searchbs64 + "&page=1&page_size=10",
                       headers=config.headers)

    tree = etree.HTML(rep.text.encode('utf-8'))
    urllist = tree.xpath('//span[@class="hsxa-host"]/a/@href')
    return len(urllist)==0

def checkSession():
    if config.cookie=="":
        print("请配置config文件")
        exit(0)
    print("检测cookie存在")
    if preCheckSession():
        print("警告:请检查cookie是否正确!")
        exit(0)
    else:
        print("提示:cookie可用")
    return

def init():
    config.SearchKEY = input('请输入fofa搜索关键字 \n')
    return


def spider():
    searchbs64 = quote(str(base64.b64encode(config.SearchKEY.encode()), encoding='utf-8'))
    print("Target page :https://fofa.info/result?qbase64=" + searchbs64)
    # html = requests.get(url="https://fofa.info/result?qbase64=" + searchbs64, headers=config.headers).text
    response = requests.get(url="https://fofa.info/result?qbase64=" + searchbs64, headers=config.headers)
    response.encoding = response.apparent_encoding
    html = response.text
    tree = etree.HTML(html.encode('utf-8'))
    try:
        pagenum = tree.xpath('//li[@class="number"]/text()')[-1]
    except Exception as e:
        print(e)
        pagenum = '0'
    print("    Page number found: " + pagenum)
    try:
        all_count = tree.xpath('//span[@class="el-pagination__total"]/text()')[-1].split(' ')[1]
    except Exception as e:
        print(e)
        all_count = '0'
    print("    Results:", all_count)

    urllist = []
    for i in range(int(config.StartPage),int(pagenum)):
        print("    Now write " + str(i) + " page")
        rep = requests.get('https://fofa.info/result?qbase64=' + searchbs64+"&page="+str(i)+"&page_size=10", headers=config.headers)

        tree = etree.HTML(rep.text.encode('utf-8'))
        urllist.extend(tree.xpath('//span[@class="hsxa-host"]/a/@href'))
        if i==int(config.StopPage):
            break
        time.sleep(config.TimeSleep)
    print(urllist)
    # print("OK,Spider is End .")
    return int(all_count), urllist

def spider_count(new_key):
    import random
    time.sleep(random.randint(4,8))
    searchbs64 = quote(str(base64.b64encode(new_key.encode()), encoding='utf-8'))
    # html = requests.get(url="https://fofa.info/result?qbase64=" + searchbs64, headers=config.headers).text
    response = requests.get(url="https://fofa.info/result?qbase64=" + searchbs64, headers=config.headers)
    response.encoding = response.apparent_encoding
    html = response.text
    tree = etree.HTML(html.encode('utf-8'))
    try:
        all_count = tree.xpath('//span[@class="el-pagination__total"]/text()')[-1].split(' ')[1]
    except Exception as e:
        print(e)
        all_count = '0'
    return int(all_count)

def main():
    logo()
    checkSession()
    init()
    spider()

if __name__ == '__main__':
    main()
