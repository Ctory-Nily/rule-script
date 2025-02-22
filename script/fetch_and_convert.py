import os
import requests
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 定义规则类型的排序优先级
RULE_ORDER = [
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-CIDR6",
    "IP-SUFFIX"
]

def get_time() -> Optional[str]:
    """
    获取工作流执行时的时间段
    :return: 当前时间
    """
    Beijing_Time = ZoneInfo('Asia/Shanghai')
    now_time = datetime.now(Beijing_Time)

    # 将时间格式化为 "年月日时分" 的格式
    format_time = now_time.strftime("%Y年%m月%d日 %H:%M")

    return format_time

def calculate_rule_number(content: List[str]) -> Dict[str, int]:
    """
    单独统计各个规则的数量
    :param content: 内容列表
    :return: 统计后的数据字典
    """
    rule_number_dict = { prefix: 0 for prefix in RULE_ORDER }

    # 遍历数据并统计
    for line in content:
        for prefix in RULE_ORDER:
            if line.startswith(prefix):
                rule_number_dict[prefix] += 1
    
    return rule_number_dict

def download_file(file_url: str) -> Optional[str]:
    """
    下载指定的文件
    :param file_url: 文件的 URL
    :return: 文件内容（字符串），失败时返回 None
    """
    try:
        response = requests.get(file_url, timeout=10)
        response.raise_for_status()  # 抛出 HTTP 错误
        logging.info(f"文件下载成功 from: {file_url}")
        return response.text  # 返回文件内容
    except requests.RequestException as e:
        logging.error(f"文件下载失败 {file_url} - {e}")
        return None

def merge_file_contents(file_contents: List[str]) -> List[str]:
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

def sort_rules(rules: List[str]) -> List[str]:
    """
    根据规则类型和字母顺序对规则进行排序
    :param rules: 规则列表
    :return: 排序后的规则列表
    """
    def rule_key(line: str) -> tuple:
        parts = line.split(",")
        if parts[0] in RULE_ORDER:
            return (RULE_ORDER.index(parts[0]), parts[1])  # 按规则类型和字母顺序排序
        else:
            return (len(RULE_ORDER), line)  # 异常类型

    return sorted(rules, key=rule_key)

def write_md_file(urls: List[str], content: List[str], folder_name: str, folder_path: str) -> None:
    """
    在每个文件夹下生成 .md 说明文件
    :param urls: 文件的 URL 列表
    :param content: 内容列表
    :param folder_name: 文件夹名称
    :param folder_path: 生成路径
    """
    # 规则总数
    rule_count = len(content)   

    # 获取到单独统计的各个规则的数量
    rule_number_dict = calculate_rule_number(content)

    # 获取当前时间
    now_time = get_time()

    # 创建 Markdown 文件内容
    md_content = f"""# {folder_name}

## 前言
本文件由脚本自动生成

## 规则统计
最后同步时间: {now_time}

各类型规则统计:
| 类型 | 数量(条)  | 
| ---- | ----  |
"""

    for prefix, count in rule_number_dict.items():
        md_content += f"| {prefix} | {count} | \n"

    md_content += f"| TOTAL | {rule_count} | \n"

    md_content += f"## Clash"
    md_content += f"### 使用说明"
    md_content += f"{folder_name}.yaml, 请使用 behavior: 'classical' \n"

    md_content += f"### 规则链接"
    for url in urls:
        md_content += f"- {url} \n"

    folder_path = folder_path + folder_name
    os.makedirs(folder_path, exist_ok=True)

    md_file_path = os.path.join(folder_path, f"README.md")
    try:
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            logging.info(f".md 文件保存成功: {md_file_path}")
    except IOError as e:
        logging.error(f".md 文件保存失败 {md_file_path} - {e}")

def write_list_file(file_name: str, content: List[str], folder_name: str, folder_path: str) -> None:
    """
    将内容写进 .list 文件，并添加标题注释
    :param file_name: 文件名称
    :param content: 内容列表
    :param folder_name: 文件夹名称
    :param folder_path: 生成路径
    """
    folder_path = folder_path + folder_name
    os.makedirs(folder_path, exist_ok=True)

    list_file_path = os.path.join(folder_path, file_name)

    # 规则总数
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    rule_number_dict = calculate_rule_number(content)

    # 获取当前时间
    now_time = get_time()

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# 同步时间: {now_time}",
    ]

    for prefix, count in rule_number_dict.items():
        formatted_content.append(f"# {prefix}: {count}")

    # 合并数组
    formatted_content.append("\n")
    formatted_content.extend(content)

    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f".list 文件保存成功: {list_file_path}")
    except IOError as e:
        logging.error(f".list 文件保存失败 {list_file_path} - {e}")

def write_yaml_file(file_name: str, content: List[str], folder_name: str, folder_path: str) -> None:
    """
    将内容写入 yaml 文件，并添加 payload 格式
    :param file_name: 文件名称
    :param content: 内容列表
    :param folder_name: 文件夹名称
    :param folder_path: 生成路径
    """
    folder_path = folder_path + folder_name
    os.makedirs(folder_path, exist_ok=True)

    yaml_file_path = os.path.join(folder_path, f"{os.path.splitext(file_name)[0]}.yaml")

    # 规则总数
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    rule_number_dict = calculate_rule_number(content)

    # 获取当前时间
    now_time = get_time()

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
        f"# 同步时间: {now_time}",
    ]

    for prefix, count in rule_number_dict.items():
        formatted_content.append(f"# {prefix}: {count}")

    # 合并数组
    formatted_content.append("\n")
    formatted_content.append("payload:")
    for line in content:
        formatted_content.append(f"  - {line}")

    try:
        with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write("\n".join(formatted_content))
        logging.info(f".yaml 文件保存成功: {yaml_file_path}")
    except IOError as e:
        logging.error(f".yaml 文件保存失败 {yaml_file_path} - {e}")

def process_file(file_name: str, urls: List[str], folder_name: str, folder_path: str) -> None:
    """
    下载文件、合并内容、排序规则并生成 .list 和 .yaml 文件。
    :param file_name: 文件名
    :param urls: 文件的 URL 列表
    :param folder_name: 文件夹名称
    :param folder_path: 生成路径
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

    # 生成 .md文件
    write_md_file(urls, sorted_content, folder_name, folder_path)

def write_total_md_file(folder_path: str, rule_list_data ,width = 5) -> None:
    """
    生成一个总的 .md文件
    :param folder_path: 生成路径
    :param rule_list_data: 列表数据
    :param width: 表格宽度
    """
    os.makedirs(folder_path, exist_ok=True)

    md_file_path = os.path.join(folder_path, f"README.md")

    # 获取当前时间
    now_time = get_time()

    # 创建 Markdown 文件内容
    md_content = f"""## 前言
本文件由脚本自动生成

## 规则列表
最后同步时间: {now_time}

各规则统计:
"""
    folder_names = [item["folder_name"] for item in rule_list_data]

    rows = []
    for i in range(0, len(folder_names), width):
        row = folder_names[i:i + width]
        rows.append(row)

    # 填充空的单元格
    for row in rows:
        while len(row) < width:
            row.append(" " * 10)  # 用空格填充空单元格

    # 生成表格
    table = []
    for row in rows:
        # 确保每个单元格是字符串
        formatted_row = [f"{cell:<10}" for cell in row]
        table.append("|".join(formatted_row))  # 使用字符串列表

    # 添加 Markdown 表格语法
    markdown_table = []
    markdown_table.append("| 规则 |" + " | ".join(["   "] * (width-1) ) + " |")  # 表头
    markdown_table.append("|" + "----------|" * width)  # 分隔线

    for line in table:
        markdown_table.append("| " + f"[{line}]" + f"(https://github.com/Ctory-Nily/rule-script/tree/main/rules/Clash/{line})" + " |")  # 表格内容
        logging.info("| " + f"[{line}]" + f"(https://github.com/Ctory-Nily/rule-script/tree/main/rules/Clash/{line})" + " |")

    logging.info(markdown_table)
    md_content += "\n".join(markdown_table)

    try:
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            logging.info(f".md 文件保存成功: {md_file_path}")
    except IOError as e:
        logging.error(f".md 文件保存失败 {md_file_path} - {e}")

if __name__ == "__main__":

    # 自定义 rule 文件夹总路径
    folder_path = 'rules/Clash/'

    # 获取 rule_file_list.json 的路径
    json_file_path = os.path.join(os.path.dirname(__file__), 'rule_file_list.json')

    # 读取 rule_file_list.json 文件
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        rule_list_data = json.load(json_file)

    # 批量处理
    for item in rule_list_data:
        process_file(item["file_name"], item["file_urls"], item["folder_name"], folder_path)
    
    # 生成总的MD文件
    write_total_md_file(folder_path, rule_list_data)

