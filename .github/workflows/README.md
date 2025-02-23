# 前言
工作流处理文件夹

## 各文件说明
- **clear-commit.yml**:     
    手动工作流, 用来清理工作流, 将整个项目移到一个新的分支上
    
- **fetch-and-convert.yml**:     
    自动工作流, 当检测到 process-rule 工作流完成后就会触发, 每天0点也会自动触发, 当检测到 script 文件夹下的 json 文件有变动后也会自动触发, 执行 fetch_and_convert.py 脚本

- **process-rule.yml**:     
    自动工作流, 当检测到 user_rule 文件夹下有变动后就会触发, 执行 process_rule.py 脚本