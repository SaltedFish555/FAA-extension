from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND, POINT
import win32api, win32con, win32gui
import cv2
import numpy as np
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
    r = RECT()
    windll.user32.GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom

    dc = windll.user32.GetDC(handle)
    cdc = windll.gdi32.CreateCompatibleDC(dc)
    bitmap = windll.gdi32.CreateCompatibleBitmap(dc, width, height)
    windll.gdi32.SelectObject(cdc, bitmap)

    windll.gdi32.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, 0x00CC0020)

    total_bytes = width * height * 4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte * total_bytes
    windll.gdi32.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

    windll.gdi32.DeleteObject(bitmap)
    windll.gdi32.DeleteObject(cdc)
    windll.user32.ReleaseDC(handle, dc)

    image = frombuffer(buffer, dtype=uint8).reshape(height, width, 4)
    return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

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


    
    
    
    



# # ---------------------- 主程序 ----------------------
# if __name__ == "__main__":
#     try:
#         # 获取窗口信息
#         # handle = get_window_handle('美食大战老鼠')
#         # handle = win32gui.FindWindowEx(handle, None, "TabContentWnd", "")
#         # handle = win32gui.FindWindowEx(handle, None, "CefBrowserWindow", "")      
#         # handle = win32gui.FindWindowEx(handle, None, "Chrome_WidgetWin_0", "")  
#         # handle = win32gui.FindWindowEx(handle, None, "WrapperNativeWindowClass", "")  
#         # handle = win32gui.FindWindowEx(handle, None, "NativeWindowClass", "")  
        
#         handle=get_window_handle("新建文本文档.txt - 记事本")
#         handle = win32gui.FindWindowEx(handle, None, "Edit", "")
        
#         scale_factor = get_scaling_factor(handle)
#         print(f"检测到缩放比例: {scale_factor:.1f}x")

#         # 获取窗口位置（用于调试）
#         win_rect = win32gui.GetWindowRect(handle)
#         print(f"窗口位置: {win_rect}")

#         # 截图
#         img = capture_image_png_once(handle)
        
#         # 图像匹配
#         target_pos, result_img = match_template(img, "1.png", 0.8)
#         cv2.imshow("匹配结果", result_img)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
        
#         if target_pos:
#             # 应用DPI缩放
#             scaled_x = int(target_pos[0] * scale_factor)
#             scaled_y = int(target_pos[1] * scale_factor)
#             print(f"原始坐标: {target_pos} → 缩放后坐标: ({scaled_x}, {scaled_y})")

#             # 执行点击操作（增加移动动作）
#             do_left_mouse_move_to(handle, scaled_x, scaled_y)
#             do_left_mouse_click(handle, scaled_x, scaled_y)
            
#             # 验证点击位置
#             cv2.circle(result_img, (target_pos[0], target_pos[1]), 10, (255,0,0), 2)
#             cv2.imwrite('click_verify.png', result_img)
#             print("点击位置已保存为 click_verify.png")
#         else:
#             print("未找到目标")
            
#     except Exception as e:
#         print(f"错误：{str(e)}")
#         # 保存错误截图用于调试
#         if 'img' in locals():
#             cv2.imwrite('error_screenshot.png', img)





# 测试点击
handle=get_window_handle("美食大战老鼠")
handle = win32gui.FindWindowEx(handle, None, "TabContentWnd", "")
handle = win32gui.FindWindowEx(handle, None, "CefBrowserWindow", "")  
handle = win32gui.FindWindowEx(handle, None, "Chrome_WidgetWin_0", "")  
handle = win32gui.FindWindowEx(handle, None, "WrapperNativeWindowClass", "")  
handle = win32gui.FindWindowEx(handle, None, "NativeWindowClass", "")  
# handle=get_window_handle("新建文本文档.txt - 记事本")
# handle = win32gui.FindWindowEx(handle, None, "Edit", "")

print(handle)

do_left_mouse_click(handle,500, 300)






