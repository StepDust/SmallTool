import webview
import time
import screeninfo


def with_application(func):
    def wrapper(self, *args, **kwargs):
        self.get_application()  # 自动调用 get_application
        return func(self, *args, **kwargs)

    return wrapper


class WindowsAPI:
    def __init__(self):
        self.last_move_time = 0
        self.move_threshold = 0.016  # 约 60fps，单位：秒
        self.application = None

    def get_application(self):
        if self.application is None:
            self.application = webview.windows[0]
        return self.application

    @with_application
    def drag_move(self, delta_x, delta_y):

        # 节流处理，避免频繁调用导致抖动
        current_time = time.time()
        if current_time - self.last_move_time < self.move_threshold:
            return

        self.last_move_time = current_time

        # 忽略过小的移动量，避免微小抖动
        if abs(delta_x) < 1 and abs(delta_y) < 1:
            return

        x, y = self.application.x, self.application.y
        # 使用整数坐标，避免浮点数导致的抖动
        self.application.move(int(x + delta_x), int(y + delta_y))

    @with_application
    def center_window(self):
        """将窗口居中到屏幕"""
        # 获取主屏幕尺寸
        screen = screeninfo.get_monitors()[0]
        screen_width = screen.width
        screen_height = screen.height

        window_width = self.application.width
        window_height = self.application.height
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.application.move(x, y)

    @with_application
    def resize_window(self, width, height):
        """调整窗口大小"""
        self.application.resize(width, height)

    @with_application
    def minimize(self):
        """最小化窗口"""
        self.application.minimize()

    @with_application
    def maximize(self):
        """最大化窗口"""
        self.application.maximize()

    @with_application
    def restore(self):
        """恢复窗口大小"""
        self.application.restore()

    @with_application
    def close(self):
        """关闭窗口"""
        self.application.destroy()

    @with_application
    def set_on_top(self, on_top):
        """设置窗口是否置顶"""
        self.application.on_top = on_top
