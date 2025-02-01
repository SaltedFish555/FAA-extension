import win32gui
import win32con

def get_window_tree(parent_handle=0, indent=0):
    window_tree = []
    
    def enum_child_windows(hwnd, results):
        results.append(hwnd)
        return True

    # 获取所有子窗口
    child_windows = []
    win32gui.EnumChildWindows(parent_handle, enum_child_windows, child_windows)
    
    for hwnd in child_windows:
        # 获取窗口信息
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        if not title:
            title = "无标题"
        
        # 递归获取子窗口
        children = get_window_tree(hwnd, indent + 1)
        
        window_info = {
            'handle': hwnd,
            'title': title,
            'class': cls,
            'children': children
        }
        window_tree.append(window_info)
    
    return window_tree

def print_window_tree(window_tree, indent=0):
    for window in window_tree:
        print(' ' * indent * 4 + 
              f"句柄: {window['handle']}, 标题: {window['title']}, 类名: {window['class']}")
        print_window_tree(window['children'], indent + 1)

def main():
    # 获取所有顶级窗口
    top_windows = []
    def enum_top_windows(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            top_windows.append(hwnd)
        return True
    
    win32gui.EnumWindows(enum_top_windows, None)
    
    # 构建完整窗口树
    full_tree = []
    for hwnd in top_windows:
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        children = get_window_tree(hwnd)
        
        full_tree.append({
            'handle': hwnd,
            'title': title if title else "无标题",
            'class': cls,
            'children': children
        })
    
    # 打印窗口树
    print("系统窗口树结构：")
    print_window_tree(full_tree)

if __name__ == "__main__":
    main()