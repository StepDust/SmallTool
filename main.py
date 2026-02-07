import webview
import subprocess
import os
import sys
import signal
from api import API
from dust_utils import setup_logger
from dust_utils.file_utils import PipUtils

# 初始化日志
logger = setup_logger()

npm_process = None  # 确保全局变量在函数外定义


def get_npm_cmd_path():
    import subprocess

    let_result = subprocess.run(["where.exe", "npm"], capture_output=True, text=True)

    if let_result.returncode != 0:
        return None

    let_paths = let_result.stdout.splitlines()

    for let_path in let_paths:
        if let_path.lower().endswith(".cmd"):
            return let_path

    return None


def create_window():
    global npm_process
    try:
        # 返回当前应用的根目录，开发环境和打包环境不同
        base_path = PipUtils.get_base_path()
        url = os.path.join(base_path, "index.html")
        logger.info(f"{os.path.exists(url) and '存在' or '不存在'}{url}")

        # 如果是打包后的应用，使用打包后的路径
        if PipUtils.is_development_mode():
            npm_path = os.path.join(base_path, "npm.cmd")
            npm_path = get_npm_cmd_path() or npm_path  # 这里使用 npm 的完整路径

            npm_process = subprocess.Popen(
                [npm_path, "run", "dev"],
                cwd=os.path.join(os.getcwd()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            url = "http://localhost:1420"

        webview.create_window(
            "MyCustomAppWindow",  # 窗口标题
            url,  # Vue.js 构建后的 HTML 文件路径
            width=1200,  # 窗口宽度
            height=800,  # 窗口高度
            resizable=True,  # 可调整大小
            shadow=True,
            frameless=True,  # 无边框窗口
            easy_drag=False,  # 禁用默认的拖动功能
            js_api=API(),
        )
    except FileNotFoundError as e:
        print(
            "找不到 npm 命令，请确保 Node.js 和 npm 已正确安装，并且 npm 在环境变量中。"
        )
        raise e  # 重新抛出异常，确保程序不继续运行


def stop_npm_process():
    # 终止 npm 进程
    global npm_process
    if npm_process:
        try:
            os.kill(npm_process.pid, signal.SIGTERM)
        except Exception as e:
            print(f"停止 npm 进程时发生错误: {e}")
    else:
        print("npm 进程未启动")


if __name__ == "__main__":
    try:
        icon_path = os.path.abspath("./src/assets/logo.ico")
        create_window()
        webview.start(
            private_mode=False,
            storage_path=os.path.join(os.getcwd(), "cache"),
            debug=PipUtils.is_development_mode(),
            http_server=True,
            gui="gtk",
            icon=icon_path,  # 新增：你的图标路径（支持 .ico 或 .png）
        )
    finally:
        if PipUtils.is_development_mode():
            stop_npm_process()
