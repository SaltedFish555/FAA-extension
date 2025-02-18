import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel
import io

class LogWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("日志输出窗口")
        main_layout = QVBoxLayout()

        # 日志标签
        self.log_label = QLabel("日志输出:")
        self.log_label.setStyleSheet("color: #333; font-weight: bold;")
        main_layout.addWidget(self.log_label)

        # 创建 QTextEdit 用于显示日志
        self.log_output = QTextEdit()
        self.log_output.setWordWrapMode(1)  # 启用自动换行
        self.log_output.setMinimumHeight(100)  # 设置最小高度
        self.log_output.setReadOnly(True)  # 设置为只读，防止编辑
        main_layout.addWidget(self.log_output)

        # 设置主布局
        self.setLayout(main_layout)

        # 创建一个输出重定向器
        self.stdout_redirector = TextEditRedirector(self.log_output)
        sys.stdout = self.stdout_redirector  # 重定向标准输出

    def show_log(self, message):
        self.log_output.append(message)  # 向 QTextEdit 添加日志消息


class TextEditRedirector:
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self.original_stdout = sys.stdout  # 保留原始的标准输出

    def write(self, message):
        # 同时将输出传递给 QTextEdit 和 终端
        self.text_edit.append(message)  # 显示到 QTextEdit
        self.original_stdout.write(message)  # 显示到终端

    def flush(self):
        # 需要实现一个空的 flush 方法，因为 sys.stdout 需要它
        pass


if __name__ == "__main__":
    app = QApplication([])

    window = LogWindow()
    window.show()

    # 测试 print 输出
    print("这是一条日志信息")
    print("这是另一条日志信息，显示在 QTextEdit 中，同时也输出到终端")

    app.exec_()
