import ctypes
from ctypes import wintypes

def get_display_scaling():
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

        return round(scale_factor, 2)

    except Exception as e:
        return f"错误: {e}"

if __name__ == "__main__":
    scaling = get_display_scaling()
    print(f"当前屏幕缩放比例: {scaling}%")
