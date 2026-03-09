#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端启动脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from loguru import logger

# 检查环境变量
env_file = Path("backend/.env")
if not env_file.exists():
    print("⚠️  警告：未找到.env文件")
    print("请复制 backend/.env.example 为 backend/.env 并填入你的API密钥")
    print("")
    print("命令：")
    print("  cd backend")
    print("  cp .env.example .env")
    print("  然后编辑.env文件填入密钥")
    print("")
    response = input("是否现在创建.env文件？(y/n): ")
    if response.lower() == 'y':
        import shutil
        shutil.copy("backend/.env.example", "backend/.env")
        print("✓ .env文件已创建")
        print("⚠️  请编辑 backend/.env 文件，填入你的API密钥后重新运行")
        sys.exit(1)

# 切换到backend目录并启动
os.chdir("backend")
print("启动后端服务器...")
print("="*50)

import subprocess
subprocess.run([sys.executable, "main.py"])
