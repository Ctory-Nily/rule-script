# 前言
脚本处理文件夹

## 各文件说明
- **rule_file_list.json**:   
    规则列表, 在这个文件中存放网络上获取到的规则链接

- **fetch_and_convert.py**:   
    工作流脚本, 用来处理和生成 .list 文件和 .yaml 文件的脚本, 会调用 rule_file_list.json 中的数据, 并生成 .md 文件

- **process_rule.py**:   
    工作流脚本, 用来处理 user_rule 文件夹下 .list 文件的脚本

