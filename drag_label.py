import sys
import win32gui
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel


class DragLabel(QLabel):
    # 定义一个自定义信号，信号传递一个字符串参数（窗口名）
    windowNameChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.startPos = None
        self.setText("拖动鼠标到目标窗口，然后松开鼠标按钮")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos()  # 记录鼠标按下时在标签内的位置

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.startPos:
            endPos = event.pos()
            self.setText(f"拖动中: {endPos.x()}, {endPos.y()}")  # 实时显示拖动过程中的坐标
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取鼠标在屏幕上的全局位置，并转换为整数
            global_end_pos = event.globalPosition()
            found_windows = []

            # 定义回调函数，用于枚举所有顶层窗口
            def enum_windows_callback(hwnd, lParam):
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                except Exception:
                    return True  # 如果获取窗口矩形失败则继续枚举
                # 判断鼠标当前位置是否在窗口区域内
                if rect[0] <= int(global_end_pos.x()) <= rect[2] and rect[1] <= int(global_end_pos.y()) <= rect[3]:
                    found_windows.append(hwnd)
                    return False  # 找到第一个匹配窗口后停止枚举
                return True

            try:
                win32gui.EnumWindows(enum_windows_callback, None)
            except Exception as e:
                # 如果错误码为 0，则认为是正常提前终止枚举，忽略该错误
                if hasattr(e, 'winerror') and e.winerror == 0:
                    pass
                else:
                    raise

            if found_windows:
                window_handle = found_windows[0]
                window_title = win32gui.GetWindowText(window_handle)
                # 发射信号，传递窗口标题
                self.windowNameChanged.emit(window_title)
                self.setText(f"获取到窗口：{window_title}")
            else:
                self.setText("未找到目标窗口")

            self.startPos = None  # 重置鼠标拖动起始位置

def main():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("DragLabel 测试")
    main_window.resize(400, 300)

    # 将 DragLabel 作为主窗口的中央控件
    drag_label = DragLabel(main_window)
    main_window.setCentralWidget(drag_label)

    # 连接自定义信号到槽函数，这里简单打印窗口标题
    drag_label.windowNameChanged.connect(lambda title: print("获取到窗口标题:", title))

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
