from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import win32con, win32gui,win32api
import cv2
from numpy import uint8, frombuffer
import ctypes
from win32api import GetSystemMetrics
# ---------------------- 新版点击函数集成 ----------------------
def do_left_mouse_click( handle, x, y):
    """模拟鼠标点击"""
    win32gui.SetForegroundWindow(handle)
    
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

def do_left_mouse_move_to( handle, x, y):
    """执行动作函数 子函数"""
    x = int(x )
    y = int(y )
    windll.user32.PostMessageW(handle, 0x0200, 0, y << 16 | x)



# ---------------------- 坐标转换增强函数 ----------------------
def get_scaling_factor():
    """获取窗口缩放比例（处理高DPI）"""
    try:
        # 加载相关 DLL
        user32 = ctypes.windll.user32
        shcore = ctypes.windll.shcore

        # 启用当前进程的 DPI 感知能力
        user32.SetProcessDPIAware()

        # 获取主显示器的句柄
        hmonitor = user32.MonitorFromWindow(user32.GetDesktopWindow(), 1)  # 1 = MONITOR_DEFAULTTOPRIMARY

        # 定义变量存储 DPI
        dpi_x = ctypes.c_uint()
        dpi_y = ctypes.c_uint()

        # 获取主显示器的 DPI 值
        shcore.GetDpiForMonitor(hmonitor, 0, ctypes.byref(dpi_x), ctypes.byref(dpi_y))  # 0 = MDT_EFFECTIVE_DPI

        # 计算缩放比例
        scale_factor = dpi_x.value / 96 * 100  # 96 是标准 DPI

        return round(scale_factor/100, 2)

    except Exception as e:
        return f"错误: {e}"


# ---------------------- 窗口操作函数 ----------------------
def get_window_handle(name):
    """增强版窗口查找函数"""
    source_root_handle = win32gui.FindWindow(None, name)
    if source_root_handle == 0:
        # 尝试枚举窗口
        def callback(source_root_handle, extra):
            if win32gui.GetWindowText(source_root_handle) == name:
                extra.append(source_root_handle)
        handles = []
        win32gui.EnumWindows(callback, source_root_handle)
        if handles:
            return handles[0]
        raise Exception(f"未找到标题为 '{name}' 的窗口")
    # handle = win32gui.FindWindowEx(source_root_handle, None, "TabContentWnd", "")
    # handle = win32gui.FindWindowEx(handle, None, "CefBrowserWindow", "")      
    # handle = win32gui.FindWindowEx(handle, None, "Chrome_WidgetWin_0", "")  
    # handle = win32gui.FindWindowEx(handle, None, "WrapperNativeWindowClass", "")  
    # handle = win32gui.FindWindowEx(handle, None, "NativeWindowClass", "")  
    return source_root_handle

# ---------------------- 截图函数（保持原样）----------------------


from PIL import ImageGrab
def capture(handle):
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    # 发送还原最小化窗口的信息
    win32gui.SetForegroundWindow(handle)
    # 设为高亮
    x1, y1, x2, y2 = get_window_pos(handle)
    sleep(0.1)
    # 截图（PIL格式）
    img_pil = ImageGrab.grab((x1, y1, x2, y2))
    # 转换为OpenCV格式（PIL是RGB，OpenCV需要BGR）
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # 如果需要展示验证（调试时可取消注释）
    # cv2.imshow('Captured', img_cv)
    # cv2.waitKey(0)
    
    return img_cv  # 返回OpenCV格式图像
    
# ---------------------- 图像匹配函数（增加可视化）----------------------
import numpy as np
def match_template(source_img, template_path, match_threshold=0.9):
    template = cv2.imdecode(buf=np.fromfile(file=template_path, dtype=np.uint8), flags=-1)
    if template is None:
        raise Exception(f"无法读取模板图像: {template_path}")
    
    h, w = template.shape[:2]
    result = cv2.matchTemplate(source_img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val < match_threshold:
        return None, source_img
    
    top_left = max_loc
    center = (top_left[0] + w//2, top_left[1] + h//2)
    
    # 增强可视化标记
    marked_img = source_img.copy()
    cv2.rectangle(marked_img, top_left, (top_left[0]+w, top_left[1]+h), (0,255,0), 2)
    cv2.circle(marked_img, center, 5, (0,0,255), -1)
    cv2.putText(marked_img, f"Confidence: {max_val:.2f}", (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
    
    return center, marked_img



def get_window_pos(handle):
    # 获取窗口句柄
    if handle == 0:
        return None
    else:
        # 返回坐标值和handle
        return win32gui.GetWindowRect(handle)
    

def restore_window_if_minimized(handle) -> bool:
    """
    :param handle: 句柄
    :return: 如果是最小化, 并恢复至激活窗口的底层, 则返回True, 否则返回False.
    """

    # 检查窗口是否最小化
    if win32gui.IsIconic(handle):
        # 恢复窗口（但不会将其置于最前面）
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)

        # 将窗口置于Z序的底部，但不改变活动状态
        win32gui.SetWindowPos(handle, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
        return True
    return False


def apply_dpi_scaling(x,y,scale_factor=1.0):
    """
    对坐标应用 DPI 缩放，并返回缩放后的坐标。

    参数:
        x (int): x 坐标
        y (int): y 坐标
        scale_factor (float): 缩放比，默认为1.0

    返回:
        scaled_x,scaled_y 
    """

    scaled_x = int(x * scale_factor)
    scaled_y = int(y * scale_factor)
    return scaled_x,scaled_y



def match_and_click(handle,source_root_handle,img_path:str,tolerance=0.95,test:bool=False):
    '''
    匹配图片并进行点击
    
    成功返回True，失败返回False
    '''
    
    # 激活窗口
    restore_window_if_minimized(source_root_handle)
    
    # 获取缩放比
    scale_factor = get_scaling_factor()
    print(f"检测到缩放比例: {scale_factor:.2f}x")
    
    # 截图
    img = capture(handle)
    
    # 图像匹配
    target_pos, result_img = match_template(img, img_path, tolerance)
    if test:
        cv2.imshow('result',result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # 添加匹配失败处理
    if target_pos is None:
        print(f"⚠️ 未匹配到图片 {img_path}，跳过点击")
        return False
    # 应用缩放
    scaled_x,scaled_y=apply_dpi_scaling(target_pos[0],target_pos[1],scale_factor)
    x1, y1, x2, y2 = get_window_pos(handle)
    # 加上偏移后再进行 DPI 缩放（或先缩放后加偏移，根据实际情况调整）
    final_x = x1 + scaled_x
    final_y = y1 + scaled_y
    do_left_mouse_click(handle, final_x, final_y)
    return True


def loop_match_and_click(handle,img_path:str,tolerance=0.95,interval=0.2,timeout=10.0,after_sleep=0.5,check_enabled=False,source_range=[0,0,2000,2000],test:bool=False):
    spend_time=0.0
    match_succeeded=False
    while spend_time<=timeout and not match_succeeded:
        match_succeeded=match_and_click(handle,handle,img_path,tolerance,test)
        sleep(interval)
        spend_time+=interval
        
        
    sleep(after_sleep)
    
    # 检查点击后是否跳转（可以检查点击后是否还能识别到原来的图片，但这样写容易出bug，因此暂时不写）
    # 未跳转成功则重新进行匹配，递归即可
    if check_enabled:
        pass
    
    return match_succeeded



import json
from time import sleep

def load_config(config_path):
    """读取JSON配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
    
def execute(window_name, configs_path):
    """执行自动化脚本流程"""
    source_root_handle=get_window_handle(window_name)
    configs=load_config(configs_path)
    for step_config in configs:
        # 获取当前步骤配置参数
        # 执行匹配点击操作
        loop_match_and_click(
            handle=source_root_handle, 
            img_path=step_config["template_path"],
            interval=step_config["interval"],
            timeout=step_config["timeout"],
            after_sleep = step_config["after_sleep"],
            check_enabled=step_config["check_enabled"],
            source_range=step_config["source_range"],
            test=True
        )
        



def input_str(handle, text):
    """
    后台模拟键盘输入，向指定窗口句柄发送文本。

    参数：
        handle: 窗口句柄（HWND）
        text: 要输入的文本（字符串）
    """
    # # 确保窗口置于前台（其实这个不应该由输入函数来管理）
    # try:
    #     win32gui.SetForegroundWindow(handle)
    # except Exception as e:
    #     print("设置窗口为前台失败:", e)
    # sleep(1)
    
    # 遍历每个字符，发送 WM_CHAR 消息
    # 可以后台输入
    for ch in text:
        # 发送单个字符消息
        # 以下两种方法都可以，但暂时不清楚二者的区别
        # win32api.PostMessage(handle, win32con.WM_CHAR, ord(ch), 0)
        win32gui.PostMessage(handle, win32con.WM_CHAR, ord(ch), 0)
        # 根据需要可以增加适当延时，以模拟自然的输入节奏
        sleep(0.05)



# 测试代码

def test():
    # 获取窗口信息
    # source_root_handle = get_window_handle('美食大战老鼠')
    
    # match_and_click(source_root_handle,source_root_handle,'Snipaste_2025-02-01_00-35-29.png',True)
    
    # print(get_scaling_factor())
    # execute('洛克童心智能辅助公测版Ver2.5.1',r'C:\Users\cy\Desktop\洛克挂机脚本\脚本.json')
    input_str(1509162,"1784224018")
    # img=capture_image_png_once(handle)
    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    pass
    
# # ---------------------- 主程序 ----------------------
if __name__ == "__main__":
    test()