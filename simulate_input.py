import pyautogui
import time

time.sleep(2)  # 给你 2 秒钟时间切换到目标窗口
pyautogui.write("user123", interval=0.1)  # 模拟输入账号
pyautogui.press("tab")                    # 按下 Tab 键
pyautogui.write("Pass@123", interval=0.1)   # 模拟输入密码
