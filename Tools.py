import os
import yaml

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