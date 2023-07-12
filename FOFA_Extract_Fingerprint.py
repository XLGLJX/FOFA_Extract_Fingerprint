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
from Tools import get_file_names, other_to_fofa_query, read_yaml
from Default_value import file_common_names, json_tmp, common_header, common_header_value
import copy
import re
from collections import Counter

urllib3.disable_warnings()
def logo():
    print('''
   _____ ____  ______        ______      _                  _     ______ _                                  _       _   
 |  ____/ __ \|  ____/\     |  ____|    | |                | |   |  ____(_)                                (_)     | |  
 | |__ | |  | | |__ /  \    | |__  __  _| |_ _ __ __ _  ___| |_  | |__   _ _ __   __ _  ___ _ __ _ __  _ __ _ _ __ | |_ 
 |  __|| |  | |  __/ /\ \   |  __| \ \/ / __| '__/ _` |/ __| __| |  __| | | '_ \ / _` |/ _ \ '__| '_ \| '__| | '_ \| __|
 | |   | |__| | | / ____ \  | |____ >  <| |_| | | (_| | (__| |_  | |    | | | | | (_| |  __/ |  | |_) | |  | | | | | |_ 
 |_|    \____/|_|/_/    \_\ |______/_/\_\\__|_|  \__,_|\___|\__| |_|    |_|_| |_|\__, |\___|_|  | .__/|_|  |_|_| |_|\__|
                        ______                               ______               __/ |         | |                     
                       |______|                             |______|             |___/          |_|                     
        
                                                                            —— extends from fofa spider       
    ''')    

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


def find_fingerprint(json_ans, html_list, header_list, all_count, exit_output = False):
    def check(new_query):
        nonlocal tot
        # new_count = fofa.spider_count(config.SearchKEY + " && " + new_query)
        new_count = fofa.spider_count(new_query)
        per = new_count/all_count
        print(f"        {new_query} —— {per}")
        if per >= config.pro_lower and per <= config.pro_upper:
            tot += 1
            return True
        return False
    
    def find_header_json():
        print("Begin to find fingerprint headers.")
        header_tmp = [(key, value) for header in header_list  for key, value in header.items() if key not in common_header and value not in common_header_value]
        tuple_counts = Counter(header_tmp)
        query_tuple = []
        for tuple_, count in tuple_counts.items():
            # print(f"{tuple_}: {count}")
            if count > len(header_list)*config.pro_first_lower:
                query_tuple.append(tuple_)
        
        print(f"    Find {len(query_tuple)} query header.")
        print(f"    Query header: {query_tuple}")
        for key, value in query_tuple:
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

        link_elements = tmp_tree.xpath('//a[@href]')
        link_files = [element.get('href') for element in link_elements]

        script_elements = tmp_tree.xpath('//script[@src]')
        script_files = [element.get('src') for element in script_elements]
        all_files = link_files + script_files
        all_files = all_files + [x.split('/')[-1] for x in all_files]
        all_files = list(set(all_files))
        # script_elements = tmp_tree.xpath('//script[@src]')
        # js_files = [element.get('src') for element in script_elements]
        # js_files = [x.split('/')[-1] for x in js_files]
        
        print(f"    Find {len(all_files)} js files in the first web.")
        for inner_file in all_files:
            cnt = 1
            if inner_file in file_common_names:
                continue
            for i in range(1,len(html_list)):
                if inner_file in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            print(f"    {inner_file} —— {percent}")
            if percent >= config.pro_first_lower:
                new_query = f"body='{inner_file}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(inner_file)
                    print(f"        new rule: {inner_file}")
    
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
            if percent >= 0.25:
                new_query = f"body='{function_name}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(function_name)
                    print(f"        new rule: {function_name}")
    
    def find_color_json():
        pattern = r'(#[A-Fa-f0-9]{6}|#[A-Fa-f0-9]{3})\b'
        colors = [color for html in html_list for color in re.findall(pattern, html)]
        colors = list(set(colors))
        
        print(f"    Find {len(colors)} colors.")
        for color in colors:
            if color in "#000000" or color.upper() in "#FFFFFF":
                continue
            cnt = 1
            for i in range(1,len(html_list)):
                if color in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            print(f"    {color} —— {percent}")
            if percent >= config.pro_first_lower:
                new_query = f"body='{color}'"
                new_query1 = f"body='color:{color}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(color)
                    print(f"        new rule: {color}")
                elif check(new_query1):
                    json_ans["rules"]["body"].append("color:"+color)
                    print(f"        new rule: color:{color}")
    
    def find_remark_json():
        pattern1 = r"(<!--.*?-->)"
        comments = re.findall(pattern1, tmp_html, re.DOTALL)
        pattern2 = r"(//.*)"
        comments2 = re.findall(pattern2, tmp_html)
        comments.extend(comments2)
        
        comments = list(set(comments))
        print(f"    Find {len(comments)} comments in the first web.")
        for comment in comments:
            if len(comment)>50:
                continue
            cnt = 1
            for i in range(1,len(html_list)):
                if comment in html_list[i]:
                    cnt += 1
            percent = cnt/len(html_list)
            
            print(f"    {comment} —— {percent}")
            if percent >= config.pro_first_lower:
                new_query = f"body='{comment}'"
                if check(new_query):
                    json_ans["rules"]["body"].append(comment)
                    print(f"        new rule: {comment}")
    
    # get rules
    tmp_html = html_list[0]
    tmp_tree = etree.HTML(tmp_html)
    tot = 0
    
    #header
    find_header_json()
    #icon hash
    if not exit_output:
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
    
    print(f"We find {tot} rules!!!")



def get_base_web(url_list):
    html_list = []
    header_list = []
    for i in trange(len(url_list)):
        url = url_list[i]
        for _ in range(2):
            try:
                response = requests.get(url, headers=config.headers,verify=False)
                if response.status_code != 200:
                    continue
                response.encoding = response.apparent_encoding
                html_list.append(response.text)
                # html_list.append(response.content)
                header_list.append(response.headers)
                break
            except:
                pass
    print(f"total count of web: {len(url_list)}, effective count: {len(html_list)}")
    return html_list, header_list

def get_fingerprint(file, all_count, url_list, output_file_names):
    html_list, header_list = get_base_web(url_list)
    
    output_file = file[:-5]+"_fingerprint.json"
    output_file_path = config.output_path + "\\" + output_file
    exit_output = False
    json_ans = {}
    if output_file in output_file_names:
        print(f"Successfully found the output file {output_file} in {config.output_path}.")
        exit_output = True
        json_ans = json.load(open(output_file_path, "r"))
        tmp = copy.deepcopy(json_tmp["rules"])
        if "icon_hash" in json_ans["rules"].keys():
            tmp["icon_hash"] = copy.deepcopy(json_ans["rules"]["icon_hash"])
        json_ans["rules"] = copy.deepcopy(tmp)
    else:
        print(f"Could not find output file.")
        json_ans = copy.deepcopy(json_tmp)
        # get name
        for key in json_ans.keys():
            if key == "level":
                break
            s = input("input "+key+" :")
            if s != "q":
                json_ans[key] = s
    if config.SearchKEY.count('"') == 2:
        if config.SearchKEY.startswith("icon_hash"):
            json_ans["rules"]["icon_hash"] = config.SearchKEY[10:]
        else:
            json_ans["rules"]["body"].append(config.SearchKEY[config.SearchKEY.index('"')+1:-1])
          
    if len(html_list) != 0:
        find_fingerprint(json_ans, html_list, header_list, all_count, exit_output)
    else:
        print("Error, no vaild web!!!")
    tmp_key = []
    for key,value in json_ans["rules"].items():
        if len(value) == 0:
            tmp_key.append(key) 
    for key in tmp_key:
        json_ans["rules"].pop(key)
        
    with open(output_file_path, "w") as f:
        json.dump(json_ans, f, indent=4)
    print(f"File {file} 's fingerprint gets.")


# def work(file, output_file_names):
#     print(f"Begin to process file: {file}")
#     if not init(file):
#         config.non_metadata_file.append(file)
#         return 
#     # print(config.SearchKEY)
#     all_count, url_list = fofa.spider()
#     print(f"File {file} 's target url gets.")
#     get_fingerprint(file, all_count, url_list, output_file_names)


menu = """
1. Batch extraction (From config.folder_path).
2. Batch extraction (From config.deal_file_names).
3. Single extraction.
4. No metadata file extraction."""

def Batch(opt):
    if opt == "1":
        input_file_names = get_file_names(config.folder_path)
    elif opt == "2":
        input_file_names = config.deal_file_names
    output_file_names = get_file_names(config.output_path)
    start = int(input(f"Please enter a starting index(0, {len(input_file_names)}): "))
    for i in range(start,len(input_file_names)):
        file = input_file_names[i]
        print("="*50 + f" INDEX {i} " + "="*50)
        print(f"Begin to process file: {file}")
        
        if not init(file):
            config.non_metadata_file.append(file)
            return 
        
        # work(file, output_file_names)
        all_count, url_list = fofa.spider()
        print(f"File {file} 's target url gets.")
        get_fingerprint(file, all_count, url_list, output_file_names)
        
        print("="*110+'\n')
        
    
    print(f"There are {len(config.non_metadata_file)} files which doesn't contains metadata.")
    print("Thay are: ")
    print(config.non_metadata_file)

def Single():
    config.SearchKEY = input("Please input your FOFA's query key: ")
    all_count, url_list = fofa.spider()
    # print(f"File {file} 's target url gets.")
    json_ans = copy.deepcopy(json_tmp)
    html_list, header_list = get_base_web(url_list)
    find_fingerprint(json_ans, html_list, header_list, all_count)
    print(json_ans)

def non_metadata_Batch():
    input_file_names = get_file_names(config.folder_path)
    
    for file in input_file_names:
        if not init(file):
            config.non_metadata_file.append(file)
    print(f"There are {len(input_file_names)} files in total.\n There are {len(config.non_metadata_file)} files which doesn't contains metadata.")
    print("Thay are: ")
    print(config.non_metadata_file)
    
    start = int(input(f"\nPlease enter a starting index(0, {len(input_file_names)}): "))
    output_file_names = get_file_names(config.output_path)
    for i in range(start,len(config.non_metadata_file)):
        file = config.non_metadata_file[i]
        print("="*50 + f" INDEX {i} " + "="*50)
        print(f"Begin to process file: {file}")
        
        config.SearchKEY = input("Please input your FOFA's query key: ")
        all_count, url_list = fofa.spider()
        print(f"File {file} 's target url gets.")
        get_fingerprint(file, all_count, url_list, output_file_names)
        
        print("="*110)
        print()

def main():
    print(menu)
    opt = input("Please input your option: ")
    fofa.checkSession()
    if opt == "3":
        Single()
    elif opt == "4":
        non_metadata_Batch()
    else:
        Batch(opt)
    
    
if __name__ == '__main__':
    logo()
    main()
