from function_faa import execute
from PyQt5.QtCore import QObject, pyqtSignal
import threading
from time import sleep
class ExecuteThread(threading.Thread,QObject):
    """
    用于执行脚本的线程类，执行完成后会弹出提示框，使用多线程是为了保证ui窗口不被阻塞。
    
    继承QObject是为了使用 PyQt 的信号槽机制，从而实现线程间通信（尤其是子线程与主线程的 GUI 交互），
    因为Qt限制了只能在主线程使用消息框，因此要用信号槽机制来实现消息框提示
    """
    # 定义一个信号，用于传递消息，注意不能写在__init__函数里
    # 因为：
    # PyQt 的信号是通过 元类（MetaClass） 和 类属性声明 实现的。
    # 当你在类作用域中声明 pyqtSignal 时，PyQt 的元类会在类定义阶段自动处理这些信号，将它们转换为合法的信号对象，并赋予它们 emit() 和 connect() 等方法。
    # 而如果信号定义在 __init__ 中：
    # 它们会成为 实例属性，而非类属性。
    # PyQt 的元类无法在类定义阶段捕获和处理这些信号。
    # 最终生成的信号对象只是一个普通的 pyqtSignal 包装器，不具备 connect 或 emit 功能。
    message_signal = pyqtSignal(str, str)
    def __init__(self,window_name, configs_path,loop_times):
        # 显式调用所有父类构造函数
        QObject.__init__(self)
        threading.Thread.__init__(self)
        self.window_name=window_name
        self.configs_path=configs_path
        self.loop_times=loop_times
        
    def run(self):
        for _ in range(self.loop_times):
            execute(self.window_name, self.configs_path)
            sleep(1)
        self.message_signal.emit("成功", "脚本执行已完成")
        
        