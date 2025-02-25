# 前言
工作流处理文件夹

## 各文件说明
- **clear-commit.yml**:     
    手动工作流, 用来清理工作流, 将整个项目移到一个新的分支上
    
- **process_json_list_fetch_and_convert.yml**:     
    自动工作流, 每天4点自动触发, 当检测到 script 文件夹下的 json 文件 或 user_rule 文件夹下的文件 有变动后也会触发, 按顺序执行 process_json、process_list 和 fetch_and_convert 工作流, 分别: 处理 Json 文件中的 urls、执行 process_rules.py 脚本 和 执行 fetch_and_convert.py 脚本
