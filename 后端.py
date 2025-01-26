from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND, POINT
import win32con, win32gui
import cv2
from numpy import uint8, frombuffer
# ---------------------- 新版点击函数集成 ----------------------
def do_left_mouse_click( handle, x, y):
    """执行动作函数 子函数"""
    x = int(x )
    y = int(y )
    windll.user32.PostMessageW(handle, 0x0201, 0, y << 16 | x)
    windll.user32.PostMessageW(handle, 0x0202, 0, y << 16 | x)

def do_left_mouse_move_to( handle, x, y):
    """执行动作函数 子函数"""
    x = int(x )
    y = int(y )
    windll.user32.PostMessageW(handle, 0x0200, 0, y << 16 | x)



# ---------------------- 坐标转换增强函数 ----------------------
def get_scaling_factor(handle):
    """获取窗口缩放比例（处理高DPI）"""
    
    try:
        # Windows 10+ 方法
        dpi = windll.user32.GetDpiForWindow(handle)
        return dpi / 96.0
    except:
        # 兼容旧版Windows
        dc = windll.user32.GetDC(0)
        scale = windll.gdi32.GetDeviceCaps(dc, 88) / 96.0  # 88=LOGPIXELSX
        windll.user32.ReleaseDC(0, dc)
        return scale

# ---------------------- 窗口操作函数 ----------------------
def get_window_handle(name):
    """增强版窗口查找函数"""
    handle = win32gui.FindWindow('DUIWindow', name)
    if handle == 0:
        # 尝试枚举窗口
        def callback(handle, extra):
            if win32gui.GetWindowText(handle) == name:
                extra.append(handle)
        handles = []
        win32gui.EnumWindows(callback, handles)
        if handles:
            return handles[0]
        raise Exception(f"未找到标题为 '{name}' 的窗口")
    return handle

# ---------------------- 截图函数（保持原样）----------------------
def capture_image_png_once(handle: HWND):
    # 获取窗口客户区的大小
    r = RECT()
    windll.user32.GetClientRect(handle, byref(r))  # 获取指定窗口句柄的客户区大小
    width, height = r.right, r.bottom  # 客户区宽度和高度

    # 创建设备上下文
    dc = windll.user32.GetDC(handle)  # 获取窗口的设备上下文
    cdc = windll.gdi32.CreateCompatibleDC(dc)  # 创建一个与给定设备兼容的内存设备上下文
    bitmap = windll.gdi32.CreateCompatibleBitmap(dc, width, height)  # 创建兼容位图
    windll.gdi32.SelectObject(cdc, bitmap)  # 将位图选入到内存设备上下文中，准备绘图

    # 执行位块传输，将窗口客户区的内容复制到内存设备上下文中的位图
    windll.gdi32.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, 0x00CC0020)

    # 准备缓冲区，用于接收位图的像素数据
    total_bytes = width * height * 4  # 计算总字节数，每个像素4字节（RGBA）
    buffer = bytearray(total_bytes)  # 创建字节数组作为缓冲区
    byte_array = c_ubyte * total_bytes  # 定义C类型数组类型

    # 从位图中获取像素数据到缓冲区
    windll.gdi32.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

    # 清理资源
    windll.gdi32.DeleteObject(bitmap)  # 删除位图对象
    windll.gdi32.DeleteObject(cdc)  # 删除内存设备上下文
    windll.user32.ReleaseDC(handle, dc)  # 释放窗口的设备上下文

    # 将缓冲区数据转换为numpy数组，并重塑为图像的形状 (高度,宽度,[B G R A四通道])
    image = frombuffer(buffer, dtype=uint8).reshape(height, width, 4)
    return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB) # 这里比起FAA原版有一点修改，在返回前先做了图像处理

# ---------------------- 图像匹配函数（增加可视化）----------------------
def match_template(source_img, template_path, match_threshold=0.8):
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
    
    # 增强可视化标记
    marked_img = source_img.copy()
    cv2.rectangle(marked_img, top_left, (top_left[0]+w, top_left[1]+h), (0,255,0), 2)
    cv2.circle(marked_img, center, 5, (0,0,255), -1)
    cv2.putText(marked_img, f"Confidence: {max_val:.2f}", (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
    
    return center, marked_img

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



def test():
    # 获取窗口信息
    handle1 = get_window_handle('美食大战老鼠')
    handle = win32gui.FindWindowEx(handle1, None, "TabContentWnd", "")
    handle = win32gui.FindWindowEx(handle, None, "CefBrowserWindow", "")      
    handle = win32gui.FindWindowEx(handle, None, "Chrome_WidgetWin_0", "")  
    handle = win32gui.FindWindowEx(handle, None, "WrapperNativeWindowClass", "")  
    handle = win32gui.FindWindowEx(handle, None, "NativeWindowClass", "")  
    
    restore_window_if_minimized(handle1)
    scale_factor = get_scaling_factor(handle1)
    print(f"检测到缩放比例: {scale_factor:.1f}x")
    
    # 截图
    img = capture_image_png_once(handle)
    
    # 图像匹配
    target_pos, result_img = match_template(img, "1.png", 0.8)
    
    # 应用缩放
    scaled_x,scaled_y=apply_dpi_scaling(target_pos[0],target_pos[1])
    
    # 执行点击操作
    do_left_mouse_click(handle, scaled_x, scaled_y)
    
# # ---------------------- 主程序 ----------------------
if __name__ == "__main__":
    test()