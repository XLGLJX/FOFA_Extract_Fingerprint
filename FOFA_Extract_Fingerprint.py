import requests
from lxml import etree
import base64
import time
import config
from urllib.parse import quote
import os
import fofa
import yaml
import json
from requests.packages import urllib3
from tqdm import trange
import re

urllib3.disable_warnings()
def logo():
    print('''
   ,--,                  ,--,                                                                          
,---.'|               ,---.'|        ,---._                        ,----..                             
|   | :     ,----..   |   | :      .-- -.' \             ,---,.   /   /   \      ,---,.   ,---,        
:   : |    /   /   \  :   : |      |    |   :          ,'  .' |  /   .     :   ,'  .' |  '  .' \       
|   ' :   |   :     : |   ' :      :    ;   |        ,---.'   | .   /   ;.  \,---.'   | /  ;    '.     
;   ; '   .   |  ;. / ;   ; '      :        |        |   |   .'.   ;   /  ` ;|   |   .':  :       \    
'   | |__ .   ; /--`  '   | |__    |    :   :        :   :  :  ;   |  ; \ ; |:   :  :  :  |   /\   \   
|   | :.'|;   | ;  __ |   | :.'|   :                 :   |  |-,|   :  | ; | ':   |  |-,|  :  ' ;.   :  
'   :    ;|   : |.' .''   :    ;   |    ;   |        |   :  ;/|.   |  ' ' ' :|   :  ;/||  |  ;/  \   \ 
|   |  ./ .   | '_.' :|   |  ./___ l                 |   |   .''   ;  \; /  ||   |   .''  :  | \  \ ,' 
;   : ;   '   ; : \  |;   : ;/    /\    J   :        '   :  '   \   \  ',  / '   :  '  |  |  '  '--'   
|   ,/    '   | '/  .'|   ,//  ../  `..-    ,        |   |  |    ;   :    /  |   |  |  |  :  :         
'---'     |   :    /  '---' \    \         ;         |   :  \     \   \ .'   |   :  \  |  | ,'         
           \   \ .'          \    \      ,'          |   | ,'      `---`     |   | ,'  `--''           
            `---`             "---....--'            `----'                  `----'               
                                                                            —— extends from fofa spider       
    ''')    

def get_file_names(folder_path):
    file_names = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_names.append(file_name)
    return file_names

def other_to_fofa_query(other_query):
    fofa_query_elements = []
    inside_quotes = False
    current_element = ""
    
    for char in other_query:
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == ' ' and not inside_quotes:
            if current_element:
                fofa_query_elements.append(current_element)
                current_element = ""
            continue
        
        current_element += char
    
    if current_element:
        fofa_query_elements.append(current_element)

    converted_elements = []
    flag = False
    flag2 = False
    # print(fofa_query_elements)
    for element in fofa_query_elements:
        if flag == True:
            flag = False
            converted_elements[-1] += " " + element + "'"
        if element.startswith("ip:"):
            converted_elements.append("ip=" + element[3:])
        elif element.startswith("port:"):
            converted_elements.append("port=" + element[5:])
        elif element.startswith("hostname:"):
            converted_elements.append("host=" + element[9:])
        elif element.startswith("os:"):
            converted_elements.append("os=" + element[3:])
        elif element.startswith("country:"):
            converted_elements.append("country=" + element[8:])
        elif element.startswith("city:"):
            converted_elements.append("city=" + element[5:])
        elif element.startswith("org:"):
            converted_elements.append("isp=" + element[4:])
        elif element.startswith("product:") or element.startswith("version:"):
            converted_elements.append("banner=" + element[8:])
        elif element.startswith("after:"):
            converted_elements.append("first_seen=>" + element[6:])
        elif element.startswith("before:"):
            converted_elements.append("first_seen=<" + element[7:])
        elif element.startswith("html:"):
            converted_elements.append("body=" + element[5:])
        elif element.startswith("http.html:"):
            converted_elements.append("body=" + element[10:])
        elif element.startswith("http.title:"):
            converted_elements.append("title=" + element[11:])
        elif element.startswith("title:"):
            converted_elements.append("title=" + element[6:])
        elif element.startswith("http.favicon.hash:"):
            converted_elements.append("icon_hash=" + element[18:])
        elif element.startswith("intext:"):
            converted_elements.append("body=" + element[7:])
        elif element.startswith("inurl:"):
            converted_elements.append("body=" + element[6:])
        elif element.startswith("Server:"):
            converted_elements.append("banner='" + element)
            flag = True
        elif element == "||":
            flag2 = True
    
    if flag2:
        fofa_query = " || ".join(converted_elements)
    else:
        fofa_query = " && ".join(converted_elements)
    return fofa_query

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def init(file):
    filepath = config.folder_path+ "\\" + file
    yaml_data = read_yaml(filepath)
    try:
        metadata = yaml_data['detail']['metadata']
        print(f"metadata: {metadata}")
    except:
        print("Metadata not found.")
        return False
    
    query_list = ["fofa-query", "shodan-query", "google-query"]
    for query in query_list:
        try:
            if query == "fofa-query":
                config.SearchKEY = metadata[query]
            else:
                config.SearchKEY = other_to_fofa_query(metadata[query])
            break
        except:
            continue
    
    print(f"SearchKEY: {config.SearchKEY}")
    return True

def get_fingerprint(all_count,url_list):
    html_list = []
    header_list = []
    for i in trange(len(url_list)):
        url = url_list[i]
        for _ in range(2):
            try:
                response = requests.get(url, headers=config.headers,verify=False)
                if response.status_code != 200:
                    continue
                html_list.append(response.text)
                header_list.append(response.headers)
                break
            except:
                pass

    print(f"total count of web: {len(url_list)}, effective count: {len(html_list)}")
    
    json_ans = {
        "product_name": "",
        "company": "",
        "industry": "",
        "level": 2,
        "rules": {
            "body": [],
            "header": [],
            "icon_hash": ""
        }
    }
    # get name
    for key in json_ans.keys():
        if key == "level":
            break
        s = input("input "+key+" :")
        if s != "q":
            json_ans[key] = s
    
    def check(new_query):
        new_count = fofa.spider_count(config.SearchKEY + " && " + new_query)
        per = new_count/all_count
        print(f"        {new_query} —— {per}")
        if per >= 0.93:
            return True
        return False
            
    def find_header_json():
        print("Begin to find fingerprint headers.")
        common_headers = dict(header_list[0])

        for headers in header_list[1:]:
            tmp_key = []
            for key, value in common_headers.items():
                if key not in headers or headers[key] != value:
                    tmp_key.append(key)
            for key in tmp_key:
                common_headers.pop(key)

        
        print(f"    Find {len(common_headers)} common_headers in the first web.")
        for key, value in common_headers.items():
            if key == 'Content-Type' and "text/html" in value:
                print("    Skip Content-Type: text/html")
                continue
            new_query = f"header='{value}'"
            if check(new_query):
                json_ans["rules"]["header"].append(key+": "+value)
                print(f"            new rule: {key}: {value}")        
    
    def find_icon_json():
        print("Begin to find fingerprint icon hash.")
        searchbs64 = quote(str(base64.b64encode(config.SearchKEY.encode()), encoding='utf-8'))
        print("    Target page :https://fofa.info/result?qbase64=" + searchbs64)
        opt = input("   Please enter whether the icon is valid (yes or no): ")
        if opt[0] != 'y':
            return 
        hash = input("  Please input icon hash: ")
        json_ans["rules"]["icon_hash"] = hash
        print(f"    new rule: icon_hash: {hash}")
    
    def find_js_json():
        print("Begin to find fingerprint js file.")
        js_file_common_names = [
                    "main.js",
                    "script.js",
                    "app.js",
                    "utils.js",
                    "jquery.js",
                    "jquery.min.js",
                    "bootstrap.js",
                    "analytics.js",
                    "carousel.js",
                    "validation.js",
                    "ajax.js",
                    "default.min.js",
                    "default.js"
                ]

        script_elements = tmp_tree.xpath('//script[@src]')
        js_files = [element.get('src') for element in script_elements]
        js_files = [x.split('/')[-1] for x in js_files]
        print(f"    Find {len(js_files)} js files in the first web.")
        for js_file in js_files:
            cnt = 1
            if js_file in js_file_common_names:
                continue
            for i in range(1,len(html_list)):
                if js_file in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            print(f"    {js_file} —— {percent}")
            if percent >= 0.9:
                new_query = f"body='{js_file}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(js_file)
                    print(f"        new rule: {js_file}")
    
    def find_fun_json():
        print("Begin to find fingerprint function.")
        script_elements = tmp_tree.xpath('//script[contains(text(), "function ")]')

        function_names = []
        for script_element in script_elements:
            script_text = script_element.text.strip()
            lines = script_text.split("\n")
            for line in lines:
                if line.strip().startswith("function "):
                    function_name = line.strip().split(" ")[1].split("(")[0]
                    function_names.append(function_name)
                    
        print(f"    Find {len(function_names)} functions in the first web.")
        function_names = list(set(function_names))
        for function_name in function_names:
            cnt = 1
            for i in range(1,len(html_list)):
                if function_name in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            print(f"    {function_name} —— {percent}")
            if percent >= 0.9:
                new_query = f"body='{function_name}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(function_name)
                    print(f"        new rule: {function_name}")
    
    def find_color_json():
        color_elements = tmp_tree.xpath('//*[@style[contains(@style, "color:")]]')
        colors = [element.attrib['style'].split('color:')[1].split(';')[0].strip() for element in color_elements]

        css_selector = '[style*="color:"]'
        color_elements = tmp_tree.cssselect(css_selector)
        colors = [element.get('style').split('color:')[1].split(';')[0].strip() for element in color_elements]
        colors = list(set(colors))
        
        print(f"    Find {len(colors)} colors in the first web.")
        for color in colors:
            if color in "#000000" or color.upper() in "#FFFFFF":
                continue
            cnt = 1
            for i in range(1,len(html_list)):
                if color in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            print(f"    {color} —— {percent}")
            if percent >= 0.9:
                new_query = f"body='{color}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(color)
                    print(f"        new rule: {color}")
    
    def find_remark_json():
        pattern1 = r"(<!--.*?-->)"
        comments = re.findall(pattern1, tmp_html, re.DOTALL)
        pattern2 = r"(//.*)"
        comments2 = re.findall(pattern2, tmp_html)
        comments.extend(comments2)
        
        print(f"    Find {len(comments)} comments in the first web.")
        comments = list(set(comments))
        for comment in comments:
            if len(comment)>20:
                continue
            cnt = 1
            for i in range(1,len(html_list)):
                if comment in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            
            print(f"    {comment} —— {percent}")
            if percent >= 0.9:
                new_query = f"body='{comment}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(comment)
                    print(f"        new rule: {comment}")
    
    # get rules
    tmp_html = html_list[0]
    tmp_tree = etree.HTML(tmp_html)
    
    #header
    find_header_json()
    #icon hash
    find_icon_json()
    #body
    ## js file
    find_js_json()
    ## function name
    find_fun_json()
    ## color
    find_color_json()
    ## remark
    find_remark_json()
    
    tmp_key = []
    for key,value in json_ans["rules"].items():
        if len(value) == 0:
            tmp_key.append(key) 
    for key in tmp_key:
        json_ans["rules"].pop(key)
    return json_ans


def work(file):
    # print(f"Begin to process file: {file}")
    # if not init(file):
    #     return 
    all_count, url_list = fofa.spider()
    print(f"File {file} 's target url gets.")
    fgp = get_fingerprint(all_count,url_list)
    
    with open(config.output_path + "\\" + file[:-5]+"_fingerprint.json", "w") as f:
        json.dump(fgp, f, indent=4)
    print(f"File {file} 's fingerprint gets.")
    
def main():
    
    fofa.checkSession()
    file_names = get_file_names(config.folder_path)
    
    work("")
    start = int(input(f"Please enter a starting index(0, {len(file_names)}): "))
    # for i,file in enumerate(file_names):
    for i in range(start,len(file_names)):
        file = file_names[i]
        print("="*50 + f" INDEX {i} " + "="*50)
        work(file)
        print("="*110)
        print()

if __name__ == '__main__':
    logo()
    main()
