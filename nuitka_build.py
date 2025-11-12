#!/usr/bin/env python3
"""
Nuitka打包配置文件 - Kuro登录工具
基于项目分析结果优化的打包配置
"""

import os
import sys
from pathlib import Path

def create_nuitka_config():
    """创建Nuitka打包配置"""
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    # 主程序文件
    main_script = project_root / "kuro_login_gui.py"
    
    # 输出目录
    output_dir = project_root / "dist_nuitka"
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # Nuitka打包命令参数
    nuitka_args = [
        # 基本配置
        "--standalone",  # 创建独立可执行文件
        "--onefile",     # 打包为单个exe文件
        "--windows-disable-console",  # 禁用控制台窗口（GUI应用）
        
        # 输出配置
        f"--output-dir={output_dir}",
        f"--output-filename=KuroLogin",
        
        # 包含模块和包
        "--include-package=geetest_captcha",
        "--include-package=utils",
        "--include-module=PyQt5",
        "--include-module=PyQt5.QtCore",
        "--include-module=PyQt5.QtGui",
        "--include-module=PyQt5.QtWidgets",
        
        # 数据文件包含
        "--include-data-dir=geetest_captcha=geetest_captcha",
        "--include-data-dir=utils=utils",
        
        # # 隐藏导入（基于PyInstaller配置分析）
        # "--nofollow-import-to=tkinter",
        # "--nofollow-import-to=PyQt5.QtWebEngine",
        # "--nofollow-import-to=PyQt5.QtWebEngineCore",
        # "--nofollow-import-to=PyQt5.QtWebEngineWidgets",
        #
        # 优化选项
        "--remove-output",  # 清理临时文件
        "--assume-yes-for-downloads",  # 自动下载依赖
        
        # Windows特定配置
        "--windows-icon-from-ico=favicon.ico",  # 如果存在图标文件
        "--windows-company-name=KuroLogin",
        "--windows-product-name=Kuro登录工具",
        "--windows-file-version=1.0.0",
        "--windows-product-version=1.0.0",
        
        # 调试信息（可选，打包时移除）
        # "--show-progress",
        # "--show-memory",
    ]
    
    # 添加主程序文件
    nuitka_args.append(str(main_script))
    
    return nuitka_args

def check_dependencies():
    """检查项目依赖"""
    required_packages = [
        "PyQt5", "requests", "loguru", "ddddocr", 
        # "torch", "torchvision", "open_clip_torch",
        "pycryptodome", "numpy", "Pillow","urllib3",
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package}")
    
    return missing_packages

if __name__ == "__main__":
    print("=== Kuro登录工具 Nuitka打包配置检查 ===")
    print("\n1. 检查依赖包...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  缺少依赖包: {missing}")
        print("请运行: pip install " + " ".join(missing))
    else:
        print("\n✓ 所有依赖包已安装")
    
    print("\n2. 生成Nuitka配置...")
    config = create_nuitka_config()
    print("Nuitka打包命令:")
    print("python -m nuitka " + " ".join(config))
    
    print("\n3. 打包说明:")
    print("- 运行上述命令开始打包")
    print("- 打包过程可能需要10-30分钟")
    print("- 最终exe文件将生成在 dist_nuitka 目录")
    print("- 文件大小预计为100-200MB")
    
    # 生成批处理文件
    batch_content = "@echo off\n"
    batch_content += "echo 开始打包Kuro登录工具...\n"
    batch_content += f"python -m nuitka {' '.join(config)}\n"
    batch_content += "echo 打包完成！\n"
    batch_content += "pause"
    
    with open("build_kuro.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("\n✓ 已生成 build_kuro.bat 批处理文件")
    print("\n=== 配置完成 ===")