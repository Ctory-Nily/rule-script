import os
import requests
import logging

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
    下载文件
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
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    # Prepare content with header comments
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则数量: {rule_count}\n",
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
    rule_count = len(content)
    rule_name = os.path.splitext(file_name)[0]  # 去掉后缀
    
    # Prepare content with payload format
    formatted_content = [
        f"# 规则名称: {rule_name}",
        f"# 规则数量: {rule_count}\n",
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

    # Define the files to download and their respective URLs
    # 需要转换的文件链接 
    file_list_map = [
        {
            "file_name":"userDirect.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Ctory-Nily/rule-script/main/rules/Clash/userDirect/userDirect.list"
                ],
            "folder_name": "userDirect",
            "write_yaml": True
        },
        {
            "file_name":"userProxy.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Ctory-Nily/rule-script/main/rules/Clash/userProxy/userProxy.list"
                ],
            "folder_name": "userProxy",
            "write_yaml": True
        },
        {
            "file_name":"userReject.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Ctory-Nily/rule-script/main/rules/Clash/userReject/userReject.list"
                ],
            "folder_name": "userReject",
            "write_yaml": True
        },
        {
            "file_name":"Emby.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Emby.list",
                "https://raw.githubusercontent.com/kirito12827/kk_zawuku/clash/user_rule/emby.list"
                ],
            "folder_name": "Emby",
            "write_yaml": True
        },
        {
            "file_name":"Google.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Google/Google.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Google.list"
                ],
            "folder_name": "Google",
            "write_yaml": True
        },
        {
            "file_name":"GoogleDrive.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GoogleDrive/GoogleDrive.list"
                ],
            "folder_name": "GoogleDrive",
            "write_yaml": True
        },
        {
            "file_name":"GoogleSearch.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GoogleSearch/GoogleSearch.list"
                ],
            "folder_name": "GoogleSearch",
            "write_yaml": True
        },
        {
            "file_name":"Microsoft.list", 
            "file_urls": [
                "hhttps://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Microsoft.list",
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Microsoft/Microsoft.list"
                ],
            "folder_name": "Microsoft",
            "write_yaml": True
        },
        {
            "file_name":"YouTube.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/YouTube/YouTube.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/YouTube.list"
                ],
            "folder_name": "YouTube",
            "write_yaml": True
        },
        {
            "file_name":"YouTubeMusic.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/YouTubeMusic/YouTubeMusic.list"
                ],
            "folder_name": "YouTubeMusic",
            "write_yaml": True
        },
        {
            "file_name":"Telegram.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Telegram/Telegram.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Telegram.list"
                ],
            "folder_name": "Telegram",
            "write_yaml": True
        },
        {
            "file_name":"Netflix.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Netflix/Netflix.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Netflix.list"
                ],
            "folder_name": "Netflix",
            "write_yaml": True
        },
        {
            "file_name":"PayPal.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/PayPal/PayPal.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/PayPal.list"
                ],
            "folder_name": "PayPal",
            "write_yaml": True
        },
        {
            "file_name":"Bahamut.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Bahamut/Bahamut.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Bahamut.list"
                ],
            "folder_name": "Bahamut",
            "write_yaml": True
        },
        {
            "file_name":"Niconico.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Niconico/Niconico.list"
                ],
            "folder_name": "Niconico",
            "write_yaml": True
        },
        {
            "file_name":"BiliBili.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BiliBili/BiliBili.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Bilibili.list"
                ],
            "folder_name": "BiliBili",
            "write_yaml": True
        },
        {
            "file_name":"Instagram.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Instagram/Instagram.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Instagram.list"
                ],
            "folder_name": "Instagram",
            "write_yaml": True
        },
        {
            "file_name":"Pixiv.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Pixiv/Pixiv.list"
                ],
            "folder_name": "Pixiv",
            "write_yaml": True
        },
        {
            "file_name":"GoogleVoice.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/GoogleVoice/GoogleVoice.list"
                ],
            "folder_name": "GoogleVoice",
            "write_yaml": True
        },
        {
            "file_name":"Line.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Line/Line.list"
                ],
            "folder_name": "Line",
            "write_yaml": True
        },
        {
            "file_name":"TikTok.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/TikTok/TikTok.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/TikTok.list"
                ],
            "folder_name": "TikTok",
            "write_yaml": True
        },
        {
            "file_name":"Twitter.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Twitter/Twitter.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Twitter.list"
                ],
            "folder_name": "Twitter",
            "write_yaml": True
        },
        {
            "file_name":"OpenAI.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/OpenAI.list"
                ],
            "folder_name": "OpenAI",
            "write_yaml": True
        },
        {
            "file_name":"GitHub.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GitHub/GitHub.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Github.list"
                ],
            "folder_name": "GitHub",
            "write_yaml": True
        },
        {
            "file_name":"Claude.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Claude.list"
                ],
            "folder_name": "Claude",
            "write_yaml": True
        },
        {
            "file_name":"Discord.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Clash/Discord/Discord.list"
                ],
            "folder_name": "Discord",
            "write_yaml": True
        },
        {
            "file_name":"Epic.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Epic/Epic.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Epic.list"
                ],
            "folder_name": "Epic",
            "write_yaml": True
        },
        {
            "file_name":"Steam.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Steam/Steam.list",
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Steam.list"
                ],
            "folder_name": "Steam",
            "write_yaml": True
        },
        {
            "file_name":"Talkatone.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/Talkatone.list"
                ],
            "folder_name": "Talkatone",
            "write_yaml": True
        },
        {
            "file_name":"DownloadCDN_CN.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/Repcz/Tool/X/Clash/Rules/DownloadCDN_CN.list",
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Game/GameDownloadCN/GameDownloadCN.list"
                ],
            "folder_name": "DownloadCDN_CN",
            "write_yaml": True
        },
        {
            "file_name":"EHGallery.list", 
            "file_urls": [
                "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/EHGallery/EHGallery.list"
                ],
            "folder_name": "EHGallery",
            "write_yaml": True
        },
    ]
    
    # 批量处理
    for item in file_list_map:
        process_file(item["file_name"], item["file_urls"], item["folder_name"],item["write_yaml"], folder_path)


