# 前言
脚本处理文件夹

## 各文件说明
- **rule_file_list.json**:   
    规则列表, 在这个文件中存放网络上获取到的规则列表, 并进行整合生成 MD 文件

- **fetch_and_convert.py**:   
    用来生成 list 文件和 yaml 文件的脚本, 会调用 rule_file_list.json 中的数据
