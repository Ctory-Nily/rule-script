import os
import requests
import logging
import json
from typing import List, Dict, Optional, Union
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

def write_md_file(urls: List[str], rule_name: str, content: List[str], cn_name: str, folder_path: str) -> None:
    """
    在每个文件夹下生成 .md 说明文件
    :param urls: 文件的 URL 列表
    :param rule_name: 规则名称
    :param content: 内容列表
    :param cn_name: 中文名称
    :param folder_path: 生成路径
    """
    os.makedirs(folder_path, exist_ok=True)

    md_file_path = os.path.join(folder_path, f"README.md")

    # 规则总数
    rule_count = len(content)   

    # 获取到单独统计的各个规则的数量
    rule_number_dict = calculate_rule_number(content)

    # 获取当前时间
    now_time = get_time()

    # 创建 Markdown 文件内容
    md_content = f"""# {cn_name if cn_name else rule_name}

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

    md_content += f"""## Clash

### 订阅链接 (每日更新)
```
https://raw.githubusercontent.com/Ctory-Nily/rule-script/main/rules/Clash/{rule_name}/{rule_name}.yaml
```

### 使用说明
{rule_name}.yaml, 请使用 behavior: 'classical'

## 规则来源
"""

    for url in urls:
        md_content += f"- {url} \n"

    try:
        with open(md_file_path, "w", encoding="utf-8") as md_file:
            md_file.write(md_content)
            logging.info(f".md 文件保存成功: {md_file_path}")
    except IOError as e:
        logging.error(f".md 文件保存失败 {md_file_path} - {e}")

def write_list_file(rule_name: str, content: List[str], folder_path: str) -> None:
    """
    将内容写进 .list 文件，并添加标题注释
    :param rule_name: 规则名称
    :param content: 内容列表
    :param folder_path: 生成路径
    """
    os.makedirs(folder_path, exist_ok=True)

    list_file_path = os.path.join(folder_path, f"{rule_name}.list")

    # 规则总数
    rule_count = len(content)
    
    rule_number_dict = calculate_rule_number(content)

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
    ]

    for prefix, count in rule_number_dict.items():
        formatted_content.append(f"# {prefix}: {count}")

    # 合并数组
    formatted_content.append("")
    formatted_content.extend(content)

    try:
        with open(list_file_path, 'w', encoding='utf-8') as list_file:
            list_file.write("\n".join(formatted_content))
        logging.info(f".list 文件保存成功: {list_file_path}")
    except IOError as e:
        logging.error(f".list 文件保存失败 {list_file_path} - {e}")

def write_yaml_file(rule_name: str, content: List[str], folder_path: str) -> None:
    """
    将内容写入 yaml 文件，并添加 payload 格式
    :param rule_name: 规则名称
    :param content: 内容列表
    :param folder_path: 生成路径
    """
    os.makedirs(folder_path, exist_ok=True)

    yaml_file_path = os.path.join(folder_path, f"{rule_name}.yaml")

    # 规则总数
    rule_count = len(content)
    
    rule_number_dict = calculate_rule_number(content)

    # 添加标题注释
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则总数量: {rule_count}",
    ]

    for prefix, count in rule_number_dict.items():
        formatted_content.append(f"# {prefix}: {count}")

    # 合并数组
    formatted_content.append("")
    formatted_content.append("payload:")
    for line in content:
        formatted_content.append(f"  - {line}")

    try:
        with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
            yaml_file.write("\n".join(formatted_content))
        logging.info(f".yaml 文件保存成功: {yaml_file_path}")
    except IOError as e:
        logging.error(f".yaml 文件保存失败 {yaml_file_path} - {e}")

def process_file(rule_name: str, urls: List[str], cn_name: str, folder_path: str) -> None:
    """
    下载文件、合并内容、排序规则并生成 .list 和 .yaml 文件。
    :param rule_name: 规则名称
    :param urls: 文件的 URL 列表
    :param cn_name: 中文名称
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

    # 在 rules/Clash 目录下创建同名文件夹
    rule_folder_path = os.path.join(folder_path, rule_name)

    # 写入 .list 和 .yaml文件
    write_list_file(rule_name, sorted_content, rule_folder_path)
    write_yaml_file(rule_name, sorted_content, rule_folder_path)    

    # 写入 .md文件
    write_md_file(urls, rule_name, sorted_content, cn_name, rule_folder_path)

def write_total_md_file(folder_path: str, rule_list_data: List[Dict[str, Union[List[str], str]]], width = 5) -> None:
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

    total_list_data_number = len(rule_list_data)

    # 创建 Markdown 文件内容
    md_content = f"""## 前言
本文件由脚本自动生成

## 规则列表
处理的规则总计: {total_list_data_number} 

最后同步时间: {now_time} \n
"""
    rule_names = [f"{item['rule_name']},{item['cn_name']}" for item in rule_list_data]

    rows = []
    for i in range(0, len(rule_names), width):
        row = rule_names[i:i + width]
        rows.append(row)

    # 生成表格
    markdown_table = []
    markdown_table.append("| 规则名称 |" + " | ".join(["   "] * (width - 1) ) + " |")  # 表头
    markdown_table.append("|" + "----------|" * width)  # 分隔线

    for row in rows:
        formatted_row = []
        for cell in row:
            # 解析 cell，格式为 "rule_name,cn_name"
            try:
                rule_name, cn_name = cell.split(",", 1)
            except ValueError:
                rule_name = cell.split(",", 1)[0]
                cn_name = False  # 或者其他默认值

            # 如果 cn_name 有值，则使用 cn_name；否则使用 rule_name
            display_name = cn_name if cn_name else rule_name
            # 格式化单元格内容
            formatted_cell = f"[{display_name}](https://github.com/Ctory-Nily/rule-script/tree/main/rules/Clash/{rule_name})"
            formatted_row.append(formatted_cell)
        markdown_table.append("| " + " | ".join(formatted_row) + " |")  # 使用字符串列表

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
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            rule_list_data = json.load(json_file)
    except FileNotFoundError:
        logging.error(f"文件未找到: {json_file_path}")
        exit(1)
    except json.JSONDecodeError:
        logging.error(f"JSON 文件格式错误: {json_file_path}")
        exit(1)

    # 批量处理
    for item in rule_list_data:
        process_file(item["rule_name"], item["rules_urls"], item["cn_name"], folder_path)
    
    # 生成总的 .md文件
    write_total_md_file(folder_path, rule_list_data)

