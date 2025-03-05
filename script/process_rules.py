import os
import logging
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
    "IP-SUFFIX",
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
    rule_number_dict = { keyword: 0 for keyword in RULE_ORDER }

    # 遍历数据并统计
    for line in content:
        for keyword in RULE_ORDER:
            if line.startswith(keyword):
                rule_number_dict[keyword] += 1
    
    return rule_number_dict

def is_list_file(file_path: str) -> bool:
    """
    检查文件是否为 list 格式（每行是一个条目）。
    :param file_path: 文件路径
    :return: 如果是 list 格式返回 True，否则返回 False
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return len(lines) > 0 and all(len(line.strip().split()) == 1 for line in lines if line.strip() and not line.startswith('#'))
    except Exception as e:
        logging.error(f"检查文件格式失败: {file_path} - {e}")
        return False

def count_rule_lines(file_path: str, rulename: str) -> None:
    """
    统计规则文件中每种规则类型的数量，并生成排序后的规则文件。
    :param file_path: 文件路径
    :param rulename: 规则名称
    """
    try:
        logging.info(f"正在处理文件: {file_path} - 规则名称: {rulename}")

        with open(file_path, "r", encoding="utf-8") as file:
            original_content = file.read().strip()

        # 移除注释行
        lines = [line.strip() for line in original_content.splitlines() if line.strip() and not line.startswith("#")]

        if not lines:
            logging.info(f"文件 {file_path} 中没有有效内容。")
            return

        # 使用集合去重
        unique_rules = set()
        sorted_rules = {prefix: [] for prefix in RULE_ORDER}

        for line in lines:
            parts = line.split(",")
            if len(parts) < 2:
                logging.warning(f"忽略格式错误的行: {line}")
                continue

            parts = [p.strip() for p in parts]
            rule_type, rule_value = parts[:2]
            rule_option = parts[2] if len(parts) > 2 else None

            if rule_type in RULE_ORDER:
                if line not in unique_rules:
                    unique_rules.add(line)
                    sorted_rules[rule_type].append(line)
                else:
                    logging.debug(f"重复规则被忽略: {line}")

        # 生成排序后的规则列表
        sorted_lines = []
        for prefix in RULE_ORDER:
            sorted_rules[prefix].sort()
            sorted_lines.extend(sorted_rules[prefix])

        rule_number_dict = calculate_rule_number(sorted_lines)
        total_rules = len(sorted_lines)

        # 获取当前时间
        now_time = get_time()

        # 生成注释信息
        comment = f"# 规则名称: {rulename} \n"
        comment += f"# 规则总数量: {total_rules} \n"
        comment += f"# 更新时间: {now_time} \n"

        for prefix, count in rule_number_dict.items():
            comment += f"# {prefix}: {count} \n"
        sorted_lines.insert(0, comment)

        # 写回文件
        new_content = "\n".join(sorted_lines)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

        # 检查文件内容是否更改
        if original_content == new_content:
            logging.info(f"文件内容未更改: {file_path}")
        else:
            logging.info(f"文件内容已更改: {file_path}")

    except Exception as e:
        logging.error(f"处理规则文件失败: {file_path} - {e}")

def process_rule_folder(folder_path: str) -> None:
    """
    处理指定文件夹中的所有规则文件。
    :param folder_path: 文件夹路径
    """
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith('.list'):  # 只处理以 .list 结尾的文件
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path) and is_list_file(file_path):  # 确保是文件
                    rulename = os.path.splitext(filename)[0]  # 去掉后缀获取规则名
                    count_rule_lines(file_path, rulename)
                    logging.info(f"处理文件成功: {file_path}，规则名称: {rulename}")
    except Exception as e:
        logging.error(f"处理文件夹失败: {folder_path} - {e}")

if __name__ == "__main__":

    # 自定义 user_rule 文件夹路径
    folder_path = 'user_rule'

    process_rule_folder(folder_path)