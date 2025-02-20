# 前言
工作流处理文件夹

### 各文件说明
- clear-commit.yml: 手动工作流, 用来清理工作流, 会把项目文件移到一个新的分支上
- fetch-and-convert.yml: 自动工作流, 根据规则列表自动生成新的 list 文件和 yaml 文件存放到指定文件夹下
- fetch_and_convert.py: 用来生成 list 文件和 yaml 文件的脚本, 会调用 rule_file_list.py 中的数据
- rule_file_list.py: 规则列表, 在这个文件中存放网络上获取到的规则列表, 并进行整合