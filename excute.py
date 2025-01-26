import sys
import json
import logging
from typing import List, Dict

import sys
print(sys.path)



# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

class AutomationEngine:
    def __init__(self, config_path: str, window_handle: int):
        """
        初始化自动化引擎
        :param config_path: JSON配置文件路径
        :param window_handle: 目标窗口句柄
        """
        self.config_path = config_path
        self.window_handle = window_handle
        self.tasks = []
        self.current_task = 0
        


    def load_config(self) -> bool:
        """加载JSON配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_tasks = json.load(f)
                self._validate_config(raw_tasks)
                self.tasks = raw_tasks
            logging.info(f"成功加载 {len(self.tasks)} 个任务")
            return True
        except Exception as e:
            logging.error(f"配置文件加载失败: {str(e)}")
            return False

    def _validate_config(self, tasks: List[Dict]) -> None:
        """验证配置有效性"""
        required_fields = {
            'template_path', 'tolerance', 'interval',
            'timeout', 'after_sleep', 'source_range'
        }
        
        for idx, task in enumerate(tasks):
            missing = required_fields - task.keys()
            if missing:
                raise ValueError(
                    f"任务 {idx+1} 缺少必要字段: {', '.join(missing)}"
                )
            
            if len(task['source_range']) != 4:
                raise ValueError(
                    f"任务 {idx+1} 截图区域格式错误，应为4个整数值"
                )

    def execute_pipeline(self) -> None:
        """执行任务流水线"""
        if not self.tasks:
            logging.warning("没有可执行的任务")
            return

        for task_idx, task in enumerate(self.tasks, 1):
            logging.info(f"正在执行任务 {task_idx}/{len(self.tasks)}")
            self._execute_single_task(task)

    def _execute_single_task(self, task: Dict) -> None:
        """执行单个任务"""
        
        success = False

        try:
            result = loop_match_p_in_w(
                source_handle=self.window_handle,
                source_range=task['source_range'],
                template=task['template_path'],
                match_tolerance=task['tolerance'],
                match_interval=task['interval'],
                after_sleep=task['after_sleep'],
                match_failed_check=task['timeout'],
                click=True
            )

            if result:
                logging.info(f"任务执行成功: {task['template_path']}")
                success = True

            if not success:
                logging.warning(f"任务超时: {task['template_path']}")

        except Exception as e:
            logging.error(f"任务执行异常: {str(e)}")
            # 可根据需要添加重试逻辑

        finally:
            if task.get('check_enabled', False):
                self._post_check(task)

    def _post_check(self, task: Dict) -> None:
        """执行后置校验（示例逻辑）"""
        logging.info("执行点击后校验...")
        # 这里可以添加二次验证逻辑，比如截图比对点击后的效果

def execute(config_path,window_handle):
    '''执行json脚本'''
    # 使用示例
    T_ACTION_QUEUE_TIMER.start()
    ENGINE = AutomationEngine(
        window_handle=window_handle,
        config_path=config_path
        
    )
    
    if ENGINE.load_config():
        ENGINE.execute_pipeline()



if __name__ == "__main__":
    # 使用示例
    T_ACTION_QUEUE_TIMER.start()
    ENGINE = AutomationEngine(
        config_path=r"I:\MyCode\FoodsVsMiceAutoAssistant-main\extension\1111.json",  # 替换为实际配置文件路径
        window_handle=263920  # 替换为实际窗口句柄
    )
    
    if ENGINE.load_config():
        ENGINE.execute_pipeline()