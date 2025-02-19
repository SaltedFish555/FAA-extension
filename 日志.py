import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt 打开另一个 EXE")
        
        # 创建按钮
        self.button = QPushButton("打开另一个 EXE", self)
        self.button.clicked.connect(self.open_exe)
        
        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        
    def open_exe(self):
        # 这里是你想要打开的 .exe 文件路径
        exe_path = r"I:\MyCode\FAA-extension\dist\ui.exe"
        
        try:
            # 使用 subprocess 打开 .exe 文件
            subprocess.Popen([exe_path])
        except Exception as e:
            print(f"打开 EXE 时发生错误: {e}")

# 创建应用程序
app = QApplication(sys.argv)

# 创建主窗口并显示
window = MainWindow()
window.show()

# 启动事件循环
sys.exit(app.exec_())
