# 忽略警告: libpng warning: iCCP: known incorrect sRGB profile
import os
os.environ["PYTHONWARNINGS"] = "ignore::libpng warning"
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QDoubleSpinBox, QScrollArea, QFileDialog, 
    QMessageBox, QCheckBox, QLabel, QSpinBox, QTextEdit
)
from PyQt5.QtCore import Qt, QSize, QTimer, QEvent, QObject, QTime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# 初始化全局调度器
scheduler = BackgroundScheduler()
scheduler.start()

from function_faa import ExecuteThread


def create_param_group(label_text, default, decimals, suffix, \
    is_float=True,
    minimum=0,
    maximum=9999,
    label_fixed_width=60,
    spin_fixed_width=100):
    """创建 标签+SpinBox 组件。

    参数:
        label (str): 标签的文本内容，显示在 QLabel 中。
        default (int 或 float): 数值输入框的默认值。根据 is_float 决定是整数还是浮点数。
        decimals (int): 小数位数（仅对 QDoubleSpinBox 有效）。
        suffix (str): 数值输入框的后缀文本（例如单位 "px" 或 "%"）。
        is_float (bool): 是否使用浮点数输入框（QDoubleSpinBox）。
                        True 为浮点数，False 为整数。
        minimum(int or float): 最小值
        maximum(int or float): 最大值
        label_fixed_width=60: 标签组件的固定宽度
        spin_fixed_width=100: 数字框组件的固定宽度
    """
    group = QHBoxLayout()
    group.setContentsMargins(0, 0, 0, 0)
    group.setSpacing(5)
    
    label = QLabel(label_text)
    label.setFixedWidth(label_fixed_width)
    # 下面这行带阿米是设置文本向左对齐，但设置了之后文本好像会向上偏一点，不美观，而且不设置好像也自动向左对齐了
    # label.setAlignment(Qt.AlignmentFlag.AlignLeft) 
    group.addWidget(label)

    # 根据 is_float 决定使用 QSpinBox 或 QDoubleSpinBox
    if is_float:
        spin = QDoubleSpinBox()
        spin.setDecimals(decimals)
    else:
        spin = QSpinBox()
    spin.setMinimum(minimum)
    spin.setMaximum(maximum)
    # 禁用滚轮事件的核心部分
    class WheelFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Wheel:
                return True  # 禁用滚轮事件
            return super().eventFilter(obj, event)
    
    wheel_filter = WheelFilter(spin)
    spin.installEventFilter(wheel_filter)  # 安装事件过滤器

    spin.setValue(default)
    spin.setFixedWidth(spin_fixed_width)
    if suffix:
        spin.setSuffix(f" {suffix}")
    group.addWidget(spin)

    return group


class ImageSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(8)

        # === 第一行：图片路径 ===
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_layout.setSpacing(5)
        
        self.template_label = QLabel("图片路径:")
        self.template_label.setFixedWidth(60)
        path_layout.addWidget(self.template_label)
        
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("图片路径")
        path_layout.addWidget(self.image_path_edit)
        
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setFixedWidth(80)
        path_layout.addWidget(self.browse_btn)
        
        main_layout.addLayout(path_layout)

        # === 第二行：数值参数 ===
        param_layout = QHBoxLayout()
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.setSpacing(15)

        self.tolerance_group = create_param_group("精度:", 0.95, 2, "")
        param_layout.addLayout(self.tolerance_group)

        self.interval_group = create_param_group("间隔:", 0.10, 2, "秒")
        param_layout.addLayout(self.interval_group)

        self.timeout_group = create_param_group("超时:", 10.0, 2, "秒", maximum=9999)
        param_layout.addLayout(self.timeout_group)

        sleep_container = QHBoxLayout()
        sleep_container.addStretch()
        self.sleep_group = create_param_group("休眠:", 0.50, 2, "秒", maximum=9999)
        sleep_container.addLayout(self.sleep_group)
        param_layout.addLayout(sleep_container, stretch=1)
        
        main_layout.addLayout(param_layout)

        # === 第三行：功能区域（校验和截图区域） ===
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        self.check_template_check = QCheckBox("点击后校验")
        action_layout.addWidget(self.check_template_check)

        # 在点击后校验后增加一个选择框“点击后输入”
        self.check_click_input = QCheckBox("点击后输入")
        action_layout.addWidget(self.check_click_input)
        self.check_click_input.toggled.connect(self.on_click_input_toggled)

        # 截图区域配置
        action_layout.addWidget(QLabel("截图区域:"))
        self.x1_group = create_param_group("X1:", 0, 0, "",is_float=False, label_fixed_width=20,spin_fixed_width=60)
        self.y1_group = create_param_group("Y1:", 0, 0, "",is_float=False, label_fixed_width=20,spin_fixed_width=60)
        self.x2_group = create_param_group("X2:", 2000, 0, "",is_float=False, label_fixed_width=20,spin_fixed_width=60)
        self.y2_group = create_param_group("Y2:", 2000, 0, "",is_float=False, label_fixed_width=20,spin_fixed_width=60)
        action_layout.addLayout(self.x1_group)
        action_layout.addLayout(self.y1_group)
        action_layout.addLayout(self.x2_group)
        action_layout.addLayout(self.y2_group)
        
        
        
        
        main_layout.addLayout(action_layout)

        # === 第四行：点击后输入的编辑框（只有当勾选“点击后输入”时显示） ===
        click_input_layout = QHBoxLayout()
        click_input_layout.setContentsMargins(0, 0, 0, 0)
        click_input_layout.setSpacing(5)
        # 添加一个空白标签作为占位，与前面行对齐
        spacer = QLabel()
        spacer.setFixedWidth(60)
        click_input_layout.addWidget(spacer)
        
        self.click_input_edit = QLineEdit()
        self.click_input_edit.setPlaceholderText("请输入内容")
        click_input_layout.addWidget(self.click_input_edit)
        main_layout.addLayout(click_input_layout)
        self.click_input_edit.setVisible(False)  # 初始状态下隐藏

        # === 第五行：操作按钮 ===
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.insert_after_btn = QPushButton("向后插入")
        self.insert_after_btn.setFixedWidth(100)
        btn_layout.addWidget(self.insert_after_btn)
        
        self.delete_btn = QPushButton("删除配置项")
        self.delete_btn.setFixedWidth(100)
        btn_layout.addWidget(self.delete_btn)
        
        main_layout.addLayout(btn_layout)

        self.browse_btn.clicked.connect(self.browse_image)
        
        # === 第六行：分割线 ==
        # 创建一个自定义的分割线
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: gray;")
        main_layout.addWidget(line)

    def on_click_input_toggled(self, checked):
        """当“点击后输入”复选框状态改变时，显示或隐藏输入框"""
        self.click_input_edit.setVisible(checked)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择模板图片", "", "PNG Files (*.png)")
        if path:
            self.image_path_edit.setText(path)

    def get_data(self):
        return {
            "template_path": self.image_path_edit.text(),
            "tolerance": self.tolerance_group.itemAt(1).widget().value(),
            "interval": self.interval_group.itemAt(1).widget().value(),
            "timeout": self.timeout_group.itemAt(1).widget().value(),
            "after_sleep": self.sleep_group.itemAt(1).widget().value(),
            "check_enabled": self.check_template_check.isChecked(),
            "click_input_enabled": self.check_click_input.isChecked(),
            "click_input": self.click_input_edit.text() if self.check_click_input.isChecked() else "",
            "source_range": [
                self.x1_group.itemAt(1).widget().value(),
                self.y1_group.itemAt(1).widget().value(),
                self.x2_group.itemAt(1).widget().value(),
                self.y2_group.itemAt(1).widget().value()
            ]
        }

from PyQt5.QtCore import pyqtSignal

class TextEditRedirector(QObject):
    """用于将 print 的内容写入到自定义的 text_edit 编辑框，采用信号跨线程发送"""
    append_text_signal = pyqtSignal(str)

    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit
        # 保存原始的标准输出，这里最好用 sys.__stdout__ 避免重定向后的影响
        self.original_stdout = sys.__stdout__
        # 将信号连接到 QTextEdit 的 append 方法上（保证在主线程调用）
        self.append_text_signal.connect(self.text_edit.append)

    def write(self, message: str):
        """
        将消息输出到 QTextEdit 和终端
        注意：使用信号保证在主线程中更新 QTextEdit
        """
        # 删除尾部的换行符，避免 QTextEdit 显示多余的空行
        message = message.rstrip('\n')
        # 通过信号发射消息，确保在主线程中调用 text_edit.append(message)
        self.append_text_signal.emit(message)
        
        # 检查是否有终端输出流，有的话就同时将消息输出到原始的 stdout（终端）（不检查的话在打包后运行exe时会报错）
        if self.original_stdout:
            self.original_stdout.write(message + "\n")

    def flush(self):
        """实现 flush 方法，因为 sys.stdout 需要它"""
        pass





from typing import Optional
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自定义识图插件")
        self.setMinimumWidth(800)
        self.initial_height = 200
        self.config_widgets = []
        self.current_config_path = None
        self.temp_config_path = "temp_config.json"

        self.execute_thread:Optional[ExecuteThread]=None
        
        self.init_ui()
        self.update_max_height()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        # === 当前配置路径显示 ===
        path_display_layout = QHBoxLayout()
        path_display_layout.addWidget(QLabel("当前配置路径:"))
        
        self.current_config_label = QLabel("无")
        self.current_config_label.setStyleSheet("color: #666;")
        self.current_config_label.setWordWrap(True)
        path_display_layout.addWidget(self.current_config_label, stretch=1)
        
        clear_btn = QPushButton("×")
        clear_btn.setFixedSize(20, 20)
        clear_btn.clicked.connect(lambda: self.update_config_path(None))
        path_display_layout.addWidget(clear_btn)
        
        main_layout.addLayout(path_display_layout)

        config_btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("打开配置")
        self.open_btn.clicked.connect(self.load_config)
        config_btn_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_config)
        config_btn_layout.addWidget(self.save_btn)

        self.save_as_btn = QPushButton("将配置另存为")
        self.save_as_btn.clicked.connect(self.save_as_config)
        config_btn_layout.addWidget(self.save_as_btn)
        main_layout.addLayout(config_btn_layout)

        self.add_btn = QPushButton("添加配置项")
        self.add_btn.clicked.connect(lambda: self.add_config())
        main_layout.addWidget(self.add_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(250)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(5)
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

        # === 底部按钮布局 ===
        bottom_btn_layout = QHBoxLayout()
        


        # 循环执行次数
        self.loop_group = create_param_group("循环执行次数", 1, 0, "次", is_float=False, maximum=9999,label_fixed_width=100,spin_fixed_width=60)
        bottom_btn_layout.addLayout(self.loop_group)
        # 在循环执行次数的右边增加一个选择框“显示识图效果”
        self.show_detection_effect_checkbox = QCheckBox("显示识图效果")
        bottom_btn_layout.addWidget(self.show_detection_effect_checkbox)

        bottom_btn_layout.addStretch()

        hwnd_label = QLabel("窗口名")
        bottom_btn_layout.addWidget(hwnd_label)

        self.window_name_edit = QLineEdit()
        self.window_name_edit.setFixedWidth(150)
        self.window_name_edit.setPlaceholderText("输入窗口名（如：美食大战老鼠）")
        self.window_name_edit.setText("789 | 美食大战老鼠")
        bottom_btn_layout.addWidget(self.window_name_edit)

        self.execute_btn = QPushButton("执行脚本")
        self.execute_btn.setFixedWidth(100)
        self.execute_btn.clicked.connect(self.execute_script)
        bottom_btn_layout.addWidget(self.execute_btn)

        main_layout.addLayout(bottom_btn_layout)
        self.resize(QSize(800, self.initial_height))
        
        # === 定时任务区域 ===
        timer_layout = QHBoxLayout()
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(5)

        # 标签“定时运行时间：”
        timer_label = QLabel("定时运行时间：")
        timer_label.setFixedWidth(100)
        timer_layout.addWidget(timer_label)

        # 编辑框
        self.timer_edit = QLineEdit()
        self.timer_edit.setPlaceholderText("输入时间点（如 08:00:00）")
        timer_layout.addWidget(self.timer_edit)

        # 按钮“启动定时任务”
        self.start_timer_btn = QPushButton("启动定时任务")
        self.start_timer_btn.setFixedWidth(120)
        self.start_timer_btn.clicked.connect(self.start_timer_task)
        timer_layout.addWidget(self.start_timer_btn)

        # 将定时任务区域添加到主布局
        main_layout.addLayout(timer_layout)
        
        # === 底部日志区域 ===
        # “日志输出”标签
        self.log_label = QLabel("日志输出:")
        self.log_label.setStyleSheet("color: #333; font-weight: bold;")
        main_layout.addWidget(self.log_label)

        # 创建 QTextEdit 用于显示长文本
        self.log_output = QTextEdit()
        self.log_output.setText("欢迎使用自定义识图插件。\n你可以在网站：https://stareabyss.github.io/FAA-WebSite/guide/start/自定义识图脚本教程.html 中查看使用教程。\n\n注意：当你使用别人发给你的配置文件时，记得修改配置中的图片路径，保证其与你的电脑一致")
        self.log_output.setWordWrapMode(1)  # 启用自动换行
        self.log_output.setMinimumHeight(100)  # 设置最小高度
        self.log_output.setReadOnly(True)  # 设置为只读，防止编辑
        # 使用新的 TextEditRedirector 重定向标准输出到 QTextEdit
        # 注意：保存实例到 self.stdout_redirector 以防被垃圾回收
        self.stdout_redirector = TextEditRedirector(self.log_output)
        sys.stdout = self.stdout_redirector
        
        # 将底部日志区域添加到主布局
        main_layout.addWidget(self.log_output)
        

    
    

    
    
    def start_timer_task(self):
        """启动定时任务"""
        try:
            # 获取用户输入的时间
            time_input = self.timer_edit.text().strip()
            task_time = QTime.fromString(time_input, "hh:mm:ss")

            if not task_time.isValid():
                QMessageBox.warning(None, "警告", "请输入有效的时间点（格式如 08:00:00）")
                return

            # 提取小时、分钟、秒
            hour = task_time.hour()
            minute = task_time.minute()
            second = task_time.second()

            # 添加定时任务到调度器
            scheduler.add_job(
                self.execute_script,  # 定时执行的函数
                CronTrigger(hour=hour, minute=minute, second=second),
                id="daily_task",  # 任务 ID
                replace_existing=True  # 如果有同名任务则替换
            )

            print(f"定时任务已启动，将在每天 {time_input} 执行一次\n注意：请确保配置完成，建议先使用“执行脚本”进行测试，确保无误后再使用定时功能")

        except Exception as e:
            QMessageBox.warning(None, "错误", f"启动定时任务时出错：{str(e)}")

    def update_config_path(self, path):
        """ 更新当前配置路径显示 """
        self.current_config_path = path
        display_text = path if path else "无"
        self.current_config_label.setText(display_text)
        self.current_config_label.setToolTip(display_text)

    def execute_script(self):
        """ 执行脚本的核心方法，用来连接按钮 """
        
        # 结束执行
        if self.execute_btn.text() == "结束脚本":
            self.execute_btn.setText("结束中……")
            self.execute_btn.setEnabled(False)  # 禁用按钮
            QApplication.processEvents() # 刷新ui
            
            self.execute_thread.stop()  # 调用自己写的方法，让线程自己安全退出
            self.execute_thread.join()  # 等待线程退出
            self.execute_thread = None
            self.execute_btn.setText("执行脚本")
            self.execute_btn.setEnabled(True)  # 启动按钮
            
            
            return 
        
        # 启动执行
        if not self.current_config_path:
            QMessageBox.warning(self, "警告", "请先保存配置或加载现有配置")
            return

        window_name = self.window_name_edit.text().strip()
        if not window_name:
            QMessageBox.warning(self, "警告", "请输入窗口名")
            return

        loop_times = self.loop_group.itemAt(1).widget().value()
        
        # 获取“显示识图效果”复选框的状态
        need_test = self.show_detection_effect_checkbox.isChecked()
        
        self.execute_btn.setText("结束脚本")
        QApplication.processEvents()
        # 创建执行线程，并将是否显示识图效果的状态赋值给线程的一个属性
        self.execute_thread = ExecuteThread(window_name, self.current_config_path, loop_times, need_test)
        self.execute_thread.start()
        
        def show_message(title, text):
            # 在主线程中显示消息框
            QMessageBox.information(self, title, text)
            self.execute_btn.setText("执行脚本")
        # 连接信号到槽函数
        self.execute_thread.message_signal.connect(show_message)

    def update_max_height(self):
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.max_window_height = int(screen_geo.height() * 0.6)

    def calculate_required_height(self):
        header_height = self.add_btn.sizeHint().height()
        footer_height = self.save_btn.sizeHint().height()
        margins = self.centralWidget().layout().contentsMargins()
        scroll_content_height = self.scroll_content.sizeHint().height()
        return (
            header_height +
            footer_height +
            scroll_content_height +
            margins.top() + margins.bottom() +
            20
        )

    def add_config(self, index=None, scroll=True):
        new_config = ImageSettingsWidget()
        
        if index is None:
            self.scroll_layout.addWidget(new_config)
            self.config_widgets.append(new_config)
        else:
            self.scroll_layout.insertWidget(index, new_config)
            self.config_widgets.insert(index, new_config)
        
        new_config.delete_btn.clicked.connect(
            lambda: self.remove_config(new_config)
        )
        new_config.insert_after_btn.clicked.connect(
            lambda: self.insert_config_after(new_config)
        )

        QApplication.processEvents()
        required_height = self.calculate_required_height()
        new_height = min(required_height, self.max_window_height)
        if new_height > self.height():
            self.resize(self.width(), new_height)
        
        if scroll:
            QTimer.singleShot(10, self.force_scroll_to_bottom)

    def insert_config_after(self, current_widget):
        try:
            index = self.config_widgets.index(current_widget)
            self.add_config(index + 1, scroll=False)
        except ValueError:
            self.add_config()

    def remove_config(self, widget):
        if widget in self.config_widgets:
            self.scroll_layout.removeWidget(widget)
            self.config_widgets.remove(widget)
            widget.deleteLater()
            
            QApplication.processEvents()
            required_height = self.calculate_required_height()
            new_height = min(required_height, self.max_window_height)
            if self.height() > new_height:
                self.resize(self.width(), new_height)
            
            self.update_scrollbar_policy(required_height)

    def force_scroll_to_bottom(self):
        scroll_bar = self.scroll.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        QTimer.singleShot(10, lambda: scroll_bar.setValue(scroll_bar.maximum()))

    def update_scrollbar_policy(self, required_height):
        if required_height > self.max_window_height:
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    
    def save_config(self):
        if not self.current_config_path:
            self.save_as_config()
        else:
            config_data = [w.get_data() for w in self.config_widgets]
            
            try:
                with open(self.current_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                print("保存配置成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件时出错：{str(e)}")

    def save_as_config(self):
        config_data = [w.get_data() for w in self.config_widgets]
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "", "JSON Files (*.json)"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            self.update_config_path(file_path)
            print("保存配置成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件时出错：{str(e)}")

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开配置文件", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            while self.config_widgets:
                widget = self.config_widgets.pop()
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()
            
            for item in config_data:
                new_config = ImageSettingsWidget()
                self._apply_config_data(new_config, item)
                self.scroll_layout.addWidget(new_config)
                self.config_widgets.append(new_config)
                
                new_config.delete_btn.clicked.connect(
                    lambda _, w=new_config: self.remove_config(w)
                )
                new_config.insert_after_btn.clicked.connect(
                    lambda _, w=new_config: self.insert_config_after(w)
                )

            self.update_config_path(file_path)
            QApplication.processEvents()
            self.resize(self.width(), min(
                self.calculate_required_height(),
                self.max_window_height
            ))
            self.force_scroll_to_bottom()
            print("打开配置成功")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败：{str(e)}")

    def _apply_config_data(self, widget, data):
        widget.image_path_edit.setText(data.get("template_path", ""))
        widget.check_template_check.setChecked(data.get("check_enabled", False))
        
        widget.tolerance_group.itemAt(1).widget().setValue(data.get("tolerance", 0.95))
        widget.interval_group.itemAt(1).widget().setValue(data.get("interval", 0.1))
        widget.timeout_group.itemAt(1).widget().setValue(data.get("timeout", 10.0))
        widget.sleep_group.itemAt(1).widget().setValue(data.get("after_sleep", 0.5))
        
        source_range = data.get("source_range", [0, 0, 0, 0])
        widget.x1_group.itemAt(1).widget().setValue(source_range[0])
        widget.y1_group.itemAt(1).widget().setValue(source_range[1])
        widget.x2_group.itemAt(1).widget().setValue(source_range[2])
        widget.y2_group.itemAt(1).widget().setValue(source_range[3])
        
        # 恢复“点击后输入”部分的配置
        widget.check_click_input.setChecked(data.get("click_input_enabled", False))
        widget.click_input_edit.setText(data.get("click_input", ""))
        widget.click_input_edit.setVisible(widget.check_click_input.isChecked())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
