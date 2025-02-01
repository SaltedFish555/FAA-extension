from ctypes import windll, byref, c_ubyte, POINTER, WINFUNCTYPE
from ctypes.wintypes import RECT, HWND, POINT, BOOL
import win32api, win32con, win32gui
import cv2
import numpy as np
from numpy import uint8, frombuffer

# ---------------------- 坐标转换函数 ----------------------
def client_to_screen(handle, x, y):
    """将窗口客户区坐标转换为屏幕坐标"""
    point = POINT(x, y)
    windll.user32.ClientToScreen(handle, byref(point))
    return (point.x, point.y)

# ---------------------- 窗口操作函数 ----------------------
def get_window_handle(name):
    """根据窗口标题获取窗口句柄"""
    handle = win32gui.FindWindow(0, name)
    if handle == 0:
        raise Exception(f"未找到标题为 '{name}' 的窗口")
    return handle

def get_window_pos(name):
    """获取窗口位置和句柄"""
    handle = get_window_handle(name)
    return win32gui.GetWindowRect(handle), handle

# ---------------------- 截图函数 ----------------------
def capture_image_png_once(handle: HWND):
    # 获取客户区大小
    r = RECT()
    windll.user32.GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom

    # 创建设备上下文
    dc = windll.user32.GetDC(handle)
    cdc = windll.gdi32.CreateCompatibleDC(dc)
    bitmap = windll.gdi32.CreateCompatibleBitmap(dc, width, height)
    windll.gdi32.SelectObject(cdc, bitmap)

    # 复制像素数据
    windll.gdi32.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, 0x00CC0020)

    # 读取像素数据
    total_bytes = width * height * 4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte * total_bytes
    windll.gdi32.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

    # 清理资源
    windll.gdi32.DeleteObject(bitmap)
    windll.gdi32.DeleteObject(cdc)
    windll.user32.ReleaseDC(handle, dc)

    # 转换图像格式
    image = frombuffer(buffer, dtype=uint8).reshape(height, width, 4)
    return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

# ---------------------- 图像匹配函数 ----------------------
def match_template(source_img, template_path, match_threshold=0.8):
    """模板匹配"""
    template = cv2.imread(template_path)
    if template is None:
        raise Exception(f"无法读取模板图像: {template_path}")
    
    h, w = template.shape[:2]
    result = cv2.matchTemplate(source_img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val < match_threshold:
        return None, source_img
    
    top_left = max_loc
    center = (top_left[0] + w//2, top_left[1] + h//2)
    cv2.rectangle(source_img, top_left, (top_left[0]+w, top_left[1]+h), (0,255,0), 2)
    return center, source_img

# ---------------------- 点击函数 ----------------------
def click_at_position(x, y):
    """模拟鼠标点击"""
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

# ---------------------- 主程序 ----------------------
if __name__ == "__main__":
    try:
        # 获取窗口信息
        (win_left, win_top, win_right, win_bottom), hwnd = get_window_pos('Rōcō悟空神辅II Ver 2.4.3.7 ┆悟空在手 游戏无忧┆')
        
        # 恢复窗口并置顶
        # win32gui.SendMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
        win32gui.SetForegroundWindow(hwnd)
        
        # 截图
        img = capture_image_png_once(hwnd)
        
        # 图像匹配
        target_pos, result_img = match_template(img, "2.png", 0.8)
        cv2.imshow("匹配结果", result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        from time import sleep
        sleep(1)
        if target_pos:
            # 关键修正：使用客户区坐标转换
            screen_x, screen_y = client_to_screen(hwnd, target_pos[0], target_pos[1])
            click_at_position(screen_x, screen_y)
            print(f"精确点击位置：({screen_x}, {screen_y})")
        else:
            print("未找到目标")
            
    except Exception as e:
        print(f"错误：{str(e)}")