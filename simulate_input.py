from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

def list_fonts():
    # 获取所有字体
    fonts = QFontDatabase.families()
    print("已安装字体：")
    for font in fonts:
        print(font)

if __name__ == "__main__":
    app = QApplication([])
    list_fonts()