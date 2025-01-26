from function import match_and_click,get_window_handle
import json
from time import sleep
def load_config(config_path):
    """读取JSON配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
    
def execute(window_name, configs_path):
    """执行自动化脚本流程"""
    handle=get_window_handle(window_name)
    configs=load_config(configs_path)
    for step_config in configs:
        # 获取当前步骤配置参数
        template_path = step_config["template_path"]
        after_sleep = step_config["after_sleep"]
        
        # 执行匹配点击操作
        match_and_click(handle, template_path)
        
        # 执行后等待
        sleep(after_sleep)


# 测试代码
# execute('美食大战老鼠','1111.json')