import os
import requests
import logging
import json

# 配置日志记录
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
    :param file_url: 文件URL
    :return: 文件内容
    下载文件提取内容
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # 抛出 HTTP 错误
        logging.info(f"文件下载成功 from: {file_url}")
        return response.text  # 返回文件内容
    except requests.RequestException as e:
        logging.error(f"文件下载失败 {file_url}: {e}")
        return None

def merge_file_contents(file_contents):
    """
    合并文件内容，去除重复项和注释行
    :param file_contents: 文件内容列表
    :return: 合并后的文件内容列表
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
    规则排序
    :param rules: 规则列表
    :return: 排序后的规则列表
    """
    def rule_key(line):
        parts = line.split(",")
        if parts[0] in RULE_ORDER:
            return (RULE_ORDER.index(parts[0]), parts[1])  # 按规则类型和字母顺序排序
        else:
            return (len(RULE_ORDER), line)  # 异常类型

    return sorted(rules, key=rule_key)

# 单独统计各个规则的数量
def every_rule_number(content):
    # 定义要统计的关键词列表
    keywords = ["DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6", "IP-SUFFIX"]

    # 初始化一个字典来存储统计结果
    count_dict = {keyword: 0 for keyword in keywords}

    # 遍历数据并统计
    for line in content:
        for keyword in keywords:
            if line.startswith(keyword):
                count_dict[keyword] += 1
    
    return count_dict

# 生成md文件
def write_md_file(urls, content, folder_name, folder_path):

    # 规则总数
    rule_count = len(content)   

    # 获取到单独统计的各个规则的数量
    count_dict = every_rule_number(content)

    # 创建 Markdown 文件内容
    md_content = f"""# {folder_name}

## 前言
本文件由脚本自动生成

## 规则统计
| 类型 | 数量(条)  | 
| ---- | ----  |
| DOMAIN | {count_dict['DOMAIN']}  | 
| DOMAIN-SUFFIX | {count_dict['DOMAIN-SUFFIX']}  | 
| DOMAIN-KEYWORD | {count_dict['DOMAIN-KEYWORD']}  | 
| IP-CIDR | {count_dict['IP-CIDR']}  | 
| IP-CIDR6 | {count_dict['IP-CIDR6']}  | 
| IP-SUFFIX | {count_dict['IP-SUFFIX']}  | 
| TOTAL | {rule_count}  | 

## 获取连接
"""

    # 添加文件下载地址
    for url in urls:
        md_content += f"- {url} \n"

    # 创建输出目录（如果不存在）
    folder_name = folder_path + folder_name
    os.makedirs(folder_name, exist_ok=True)

    # 保存 Markdown 文件
    md_file_path = os.path.join(folder_name, f"README.md")
    try:
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            logging.info(f"MD 文件保存成功: {md_file_path}")
    except IOError as e:
        logging.error(f"MD 文件保存失败 {md_file_path}: {e}")

# 处理list文件
def write_list_file(file_name, content, folder_name, folder_path):
    """
    将内容写进 .list 文件，并添加标题注释
    :param file_name: 文件名称
    :param content: 内容列表
    改写list文件
    """
    folder_name = folder_path + folder_name
    os.makedirs(folder_name, exist_ok=True)

    list_file_path = os.path.join(folder_name, file_name)

    # 规则总数
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    count_dict = every_rule_number(content)

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# DOMAIN: {count_dict['DOMAIN']}",
        f"# DOMAIN-SUFFIX: {count_dict['DOMAIN-SUFFIX']}",
        f"# DOMAIN-KEYWORD: {count_dict['DOMAIN-KEYWORD']}",
        f"# IP-CIDR: {count_dict['IP-CIDR']}",
        f"# IP-CIDR6: {count_dict['IP-CIDR6']}",
        f"# IP-SUFFIX: {count_dict['IP-SUFFIX']}\n",
    ] + content

    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f".list 文件保存成功: {list_file_path}")
    except IOError as e:
        logging.error(f".list 文件保存失败 {list_file_path}: {e}")

# 处理yaml文件
def write_yaml_file(file_name, content, folder_name, folder_path):
    """
    将内容写入 yaml 文件，并添加 payload 格式
    :param file_name: 文件名称
    :param content: 内容列表
    改写成yaml文件
    """
    folder_name = folder_path + folder_name
    os.makedirs(folder_name, exist_ok=True)

    yaml_file_path = os.path.join(folder_name, f"{os.path.splitext(file_name)[0]}.yaml")

    # 规则总数
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    count_dict = every_rule_number(content)

    # 添加 payload 格式
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# DOMAIN: {count_dict['DOMAIN']}",
        f"# DOMAIN-SUFFIX: {count_dict['DOMAIN-SUFFIX']}",
        f"# DOMAIN-KEYWORD: {count_dict['DOMAIN-KEYWORD']}",
        f"# IP-CIDR: {count_dict['IP-CIDR']}",
        f"# IP-CIDR6: {count_dict['IP-CIDR6']}",
        f"# IP-SUFFIX: {count_dict['IP-SUFFIX']}\n",
        "payload:"
    ] + [f"  - {line}" for line in content]

    try:
        with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write("\n".join(formatted_content))
        logging.info(f".yaml 文件保存成功: {yaml_file_path}")
    except IOError as e:
        logging.error(f".yaml 文件保存失败 {yaml_file_path}: {e}")

# 批量处理每一行数据
def process_file(file_name, urls, folder_name, folder_path):
    """
    获取list文件内的全部文本内容
    """
    file_contents = []
    for url in urls:
        content = download_file(url)
        if content is not None:
            file_contents.append(content)
    
    # 合并内容
    merged_content = merge_file_contents(file_contents)

    # 排序规则
    sorted_content = sort_rules(merged_content)

    # 写入 .list 和 .yaml文件
    write_list_file(file_name, sorted_content, folder_name ,folder_path)
    write_yaml_file(file_name, sorted_content, folder_name, folder_path)    

    # 生成MD说明文件
    write_md_file(urls, sorted_content, folder_name, folder_path)

# 生成一个总的MD说明文件
def total_md_file(folder_path, rule_list_data ,width=5):

    # 创建 Markdown 文件内容
    md_content = f"""## 前言
本文件由脚本自动生成

## 规则列表
"""

    # 提取所有 file_name
    folder_names = [item.get("folder_name", "") for item in rule_list_data]

    # 表头
    table = "| 规则名称 |" + "  |" * (width-1) + "\n"
    table += "|" + "---|" * width + "\n"

    # 分组数据
    for i in range(0, len(folder_names), width):
        row = folder_names[i:i + width]  # 获取当前行的数据
        # 如果数据不足，用空格填充
        row += [""] * (width - len(row))
        row_str = "|" + "|".join(f"[{row}](https://github.com/Ctory-Nily/rule-script/tree/main/rules/Clash/{row})") + "|"  # 将数据拼接为表格行
        table += row_str + "\n"

    # 合并
    md_content += table

    # 创建输出目录（如果不存在）
    os.makedirs(folder_path, exist_ok=True)

    # 保存 Markdown 文件
    md_file_path = os.path.join(folder_path, f"README.md")
    try:
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            logging.info(f"MD 文件保存成功: {md_file_path}")
    except IOError as e:
        logging.error(f"MD 文件保存失败 {md_file_path}: {e}")

if __name__ == "__main__":

    # 设置rule文件夹路径
    folder_path = 'rules/Clash/'


    # 获取 rule_file_list.json 的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "rule_file_list.json")

    # 读取 rule_file_list.json 文件
    with open(data_path, "r", encoding="utf-8") as f:
        rule_list_data = json.load(f)

    # 批量处理
    for item in rule_list_data:
        process_file(item["file_name"], item["file_urls"], item["folder_name"], folder_path)
    
    # 生成总的MD文件
    total_md_file(folder_path, rule_list_data)

