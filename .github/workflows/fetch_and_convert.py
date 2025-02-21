import os
import requests
import logging
from rule_file_list import rule_list_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义规则类型的排序优先级
RULE_ORDER = [
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-CIDR6",
    "IP-SUFFIX"
]

def download_file(file_url):
    """
    Download the specified file.
    :param file_url: str, URL of the file
    :return: str, content of the downloaded file
    下载文件提取内容
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logging.info(f"File downloaded from: {file_url}")
        return response.text  # Return file content
    except requests.RequestException as e:
        logging.error(f"Failed to download {file_url}: {e}")
        return None

def merge_file_contents(file_contents):
    """
    Merge file contents, removing duplicates and preserving order.
    :param file_contents: list, content of each file
    :return: list, merged content
    去除带#的文本内容
    """
    merged_lines = []
    seen_lines = set()

    for content in file_contents:
        if content:
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line not in seen_lines:  # 去除重复项和注释
                    seen_lines.add(line)
                    merged_lines.append(line)
    
    return merged_lines

def sort_rules(rules):
    """
    Sort rules based on RULE_ORDER and alphabetically.
    :param rules: list, list of rule strings
    :return: list, sorted rules
    根据指定的规则进行排序
    """
    def rule_key(line):
        parts = line.split(",")
        if parts[0] in RULE_ORDER:
            return (RULE_ORDER.index(parts[0]), parts[1])  # Sort by rule type and alphabetically
        else:
            return (len(RULE_ORDER), line)  # Unknown types go to the end

    return sorted(rules, key=rule_key)

# 处理list文件
def write_list_file(file_name, content, folder_name, folder_path):
    """
    Write sorted content to a .list file with header comments.
    :param file_name: str, name of the .list file
    :param content: list, sorted content
    改写list文件
    """
    folder_name = folder_path + folder_name
    os.makedirs(folder_name, exist_ok=True)

    list_file_path = os.path.join(folder_name, file_name)

    # 规则总数
    rule_count = len(content)

    # 定义要统计的关键词列表
    keywords = ["DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6", "IP-SUFFIX"]

    # 初始化一个字典来存储统计结果
    count_dict = {keyword: 0 for keyword in keywords}

    # 遍历数据并统计
    for line in content:
        for keyword in keywords:
            if line.startswith(keyword):
                count_dict[keyword] += 1

    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    # Prepare content with header comments
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# DOMAIN: {count_dict['DOMAIN']}",
        f"# DOMAIN-SUFFIX: {count_dict['DOMAIN-SUFFIX']}"
        f"# DOMAIN-KEYWORD: {count_dict['DOMAIN-KEYWORD']}",
        f"# IP-CIDR: {count_dict['IP-CIDR']}",
        f"# IP-CIDR6: {count_dict['IP-CIDR6']}",
        f"# IP-SUFFIX: {count_dict['IP-SUFFIX']}\n"
    ] + content

    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f"List file saved: {list_file_path}")
    except IOError as e:
        logging.error(f"Failed to write list file {list_file_path}: {e}")

# 处理yaml文件
def write_yaml_file(file_name, content, folder_name, folder_path):
    """
    Write content to a YAML file in payload format.
    :param file_name: str, name of the .list file
    :param content: list, sorted content
    改写成yaml文件
    """
    folder_name = folder_path + folder_name
    os.makedirs(folder_name, exist_ok=True)

    yaml_file_path = os.path.join(folder_name, f"{os.path.splitext(file_name)[0]}.yaml")

    # 规则总数
    rule_count = len(content)

    # 定义要统计的关键词列表
    keywords = ["DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6", "IP-SUFFIX"]

    # 初始化一个字典来存储统计结果
    count_dict = {keyword: 0 for keyword in keywords}

    # 遍历数据并统计
    for line in content:
        for keyword in keywords:
            if line.startswith(keyword):
                count_dict[keyword] += 1

    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀

    console.log(count_dict)
    console.log(content)
    
    # Prepare content with payload format
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# DOMAIN: {count_dict['DOMAIN']}",
        f"# DOMAIN-SUFFIX: {count_dict['DOMAIN-SUFFIX']}"
        f"# DOMAIN-KEYWORD: {count_dict['DOMAIN-KEYWORD']}",
        f"# IP-CIDR: {count_dict['IP-CIDR']}",
        f"# IP-CIDR6: {count_dict['IP-CIDR6']}",
        f"# IP-SUFFIX: {count_dict['IP-SUFFIX']}\n"
        "payload:"
    ] + [f"  - {line}" for line in content]

    try:
        with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write("\n".join(formatted_content))
        logging.info(f"YAML file saved: {yaml_file_path}")
    except IOError as e:
        logging.error(f"Failed to write YAML file {yaml_file_path}: {e}")

# 批量处理多余的list文件
def process_file(file_name, urls, folder_name, write_yaml, folder_path):
    """
    获取list文件内的全部文本内容
    """
    file_contents = []
    for url in urls:
        content = download_file(url)
        if content is not None:
            file_contents.append(content)
    
    # Merge contents
    # 去除文本中带#的内容 并且 合并重复内容
    merged_content = merge_file_contents(file_contents)

    # Sort rules
    # 根据预定顺序 进行排序
    sorted_content = sort_rules(merged_content)

    # Write .list and .yaml files
    # 分别改写成 .list文件 和 .yaml文件
    write_list_file(file_name, sorted_content, folder_name ,folder_path)
    if write_yaml:
        write_yaml_file(file_name, sorted_content, folder_name, folder_path)

if __name__ == "__main__":

    # 设置rule文件夹路径
    folder_path = 'rules/Clash/'
    
    # 批量处理
    for item in rule_list_data:
        process_file(item["file_name"], item["file_urls"], item["folder_name"],item["write_yaml"], folder_path)


