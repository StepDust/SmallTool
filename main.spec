# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller打包配置文件
功能说明：
1. 资源文件管理
   - 自动扫描并收集项目中的静态资源文件
   - 支持html/css/js/图片/字体等多种文件类型
   - 保持原始目录结构打包
2. 依赖项控制
   - 智能分析并管理Python模块依赖
   - 可配置隐式导入模块列表
   - 支持排除不需要的模块减小体积
3. 性能优化
   - 集成UPX压缩以减小生成文件体积
   - 使用LZMA算法实现高效压缩
   - 优化运行时临时文件处理
4. 安全性
   - 提供代码加密选项
   - 可配置hook禁用策略
   - 运行时模块访问控制
5. 跨平台兼容
   - 自动适配目标系统架构
   - Windows平台特定优化
   - 支持多平台打包配置
6. 打包定制
   - 支持读取package.json进行配置
   - 可自定义应用图标和名称
   - 灵活的打包模式选择
"""
import os
import sys
import glob
import json
import argparse
# 加密设置，用于保护打包后的代码
block_cipher = None
# 检查是否通过PyInstaller传入spec文件
if hasattr(sys, "argv") and sys.argv[0].endswith(".spec"):
    # 如果是通过PyInstaller调用,获取spec文件的绝对路径
    spec_path = os.path.abspath(sys.argv[0]) # pyinstaller 传入的 spec 文件路径
else:
    # 如果不是通过PyInstaller调用,使用当前目录作为默认路径
    spec_path = os.path.abspath(".") # fallback：当前目录
# 获取spec文件所在的目录作为基准目录
base_dir = os.path.dirname(spec_path)
main_path = os.environ.get("MAIN_PATH", os.path.join(base_dir, "main.py"))
code_dir = os.environ.get("CODE_DIR", base_dir)
# 动态获取icon.ico的路径
icon_path = os.path.join(code_dir, "icon.ico")
icon_exists = os.path.isfile(icon_path)

def get_data_files():
    data_files = []
    dist_dir = os.path.join(code_dir, "dist")
    if not os.path.isdir(dist_dir):
        return data_files  # 如果dist不存在，返回空
    
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            src_path = os.path.join(root, file)
            # 计算相对于dist的相对路径
            rel_path = os.path.relpath(root, dist_dir)
            if rel_path == '.':
                dest_path = 'dist'  # 根目录文件放到 dist/ 下（保持完整dist文件夹）
            else:
                dest_path = os.path.join('dist', rel_path).replace(os.sep, '/')
            data_files.append((src_path, dest_path))
    
    return data_files

# Analysis 中主脚本及参数以元组形式传递
a = Analysis(
    [
        main_path,
    ],
    pathex=[],
    binaries=[],
    datas=get_data_files(),
    hiddenimports=[
        # 补充缺失的运行时依赖
        "webview.platforms.win32",
        #"webview.platforms.edgechromium",
        "webview.js",
        "http.client",
        "urllib.request",
    ],
    hookspath=[],
    hooksconfig={
        "hook-distutils.py": {"disabled": True},
        "hook-setuptools.py": {"disabled": True}, # 新增禁用setuptools hook
    },
    runtime_hooks=[
        # 添加运行时hook避免自动导入
        #'hook-runtime.py'
    ],
    excludes=[
        "tkinter",
        "test",
        "unittest",
        "pydoc",
        # 注释掉distutils排除项
        # 'distutils',
        "setuptools",
        "lib2to3",
        # 'distutils.*',
        "_distutils_hack",
        "setuptools._distutils",
        "setuptools.extern",
        "pkg_resources",
        # 排除所有 Qt 相关模块
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "qtpy",
        "Qt",
    ],
    win_no_prefer_redirects=False, # Windows重定向设置
    win_private_assemblies=False, # Windows私有程序集设置
    cipher=block_cipher, # 加密设置
    noarchive=True, # 不打包成归档文件，这样可以减小体积
)
# 创建PYZ归档文件，包含所有纯Python模块
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
# 读取package.json配置
def get_app_title():
    try:
        package_path = os.path.join(code_dir, "package.json")
        with open(package_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("window", {}).get("title", "SmallTool")
    except Exception as e:
        print(f"读取package.json失败: {e}")
        return "SmallTool"
# 创建可执行文件（使用动态名称）
exe = EXE(
    pyz, # PYZ归档文件
    a.scripts, # 脚本文件
    a.binaries, # 二进制文件
    a.zipfiles, # ZIP文件
    a.datas, # 数据文件
    [], # 运行时文件
    name=get_app_title(), # 动态获取应用名称
    debug=True, # 是否包含调试信息
    bootloader_ignore_signals=False, # 是否忽略信号
    strip=False, # 禁用strip功能
    upx=True, # 使用UPX压缩
    upx_args=["--best", "--lzma"], # 使用最高压缩级别和LZMA算法
    upx_exclude=[], # UPX排除列表
    runtime_tmpdir=None, # 运行时临时目录
    console=False, # 是否显示控制台窗口
    disable_windowed_traceback=False, # 是否禁用窗口化程序的回溯
    argv_emulation=False, # 是否模拟命令行参数
    target_arch=None, # 目标架构
    codesign_identity=None, # 代码签名标识
    entitlements_file=None, # 授权文件
    icon=os.path.abspath(icon_path) if icon_exists else None, # 自动设置图标
    onefile=True, # 打包为单文件模式
)