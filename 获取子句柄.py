import win32gui
import win32api
import win32con

def find_child_window_by_position(parent_hwnd, target_x, target_y):
    """
    通过父窗口句柄和目标位置查找子窗口句柄
    :param parent_hwnd: 父窗口句柄
    :param target_x: 目标位置的 x 坐标
    :param target_y: 目标位置的 y 坐标
    :return: 子窗口句柄，如果未找到则返回 None
    """
    target_pos = (target_x, target_y)

    # 枚举所有子窗口
    def enum_child_windows_callback(hwnd, extra):
        # 获取子窗口的矩形区域
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect

        # 检查目标位置是否在子窗口的矩形区域内
        if (left <= target_pos[0] <= right) and (top <= target_pos[1] <= bottom):
            # 找到匹配的子窗口，保存句柄并停止枚举
            extra.append(hwnd)
            return False
        return True

    result = []
    win32gui.EnumChildWindows(parent_hwnd, enum_child_windows_callback, result)

    # 返回找到的子窗口句柄
    return result

from time import sleep
# 示例：查找父窗口句柄和目标位置的子窗口
if __name__ == "__main__":
    # 假设父窗口的标题是 "Parent Window"
    # parent_hwnd = win32gui.FindWindow(None, "Parent Window")
    # if not parent_hwnd:
    #     print("未找到父窗口")
    #     exit()
    parent_hwnd=266856
    # 目标位置（屏幕坐标）
    target_x, target_y = 760, 840
    sleep(2)
    # 查找子窗口
    child_hwnds = find_child_window_by_position(parent_hwnd, target_x, target_y)

    print(child_hwnds)