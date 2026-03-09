#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文件清理脚本
删除临时、测试、调试文件，保留核心功能文件
"""
import sys
import os
from pathlib import Path
from loguru import logger


def clean_project():
    """清理项目文件"""
    print("""
========================================
  🧹 项目文件清理
========================================
    """)

    project_dir = Path("D:/自动化生产动漫工具/comic-generator")

    if not project_dir.exists():
        print("❌ 项目目录不存在")
        return

    os.chdir(project_dir)

    # 文件分类
    keep_files = {
        # 核心系统文件
        "config.py",
        "main.py",

        # 完整自动化流程
        "full_auto_workflow.py",

        # API客户端
        "api_clients/__init__.py",
        "api_clients/glm_client.py",
        "api_clients/jimeng_client.py",
        "api_clients/wechat_client.py",

        # 工具模块
        "utils/__init__.py",
        "utils/image_utils.py",

        # 生成器模块
        "generators/__init__.py",

        # 文档
        "README.md",
        "STYLE_STANDARD.md",
        ".env",
        ".env.example",
        ".gitignore",
        "requirements.txt",
    }

    # 需要删除的文件列表
    files_to_delete = [
        # 调试文件
        "debug_api_response.py",
        "debug_html_content.py",
        "debug_jimeng.py",
        "debug_json_payload.py",
        "diagnose_ark.py",
        "diagnose_wechat.py",

        # 修复脚本
        "fix_combined_image.py",
        "fix_jimeng_size.py",
        "regenerate_combined.py",
        "regenerate_panel4.py",

        # 测试文件
        "test_encoding_upload.py",
        "test_fixed_encoding.py",
        "test_full.py",
        "test_jimeng_api.py",
        "test_models.py",
        "test_script.py",
        "test_simple.py",
        "test_single_image.py",
        "test_unified_size.py",
        "polling_test.py",

        # 临时上传脚本
        "run_goku_comic.py",
        "upload_adjusted_layout.py",
        "upload_correct_goku.py",
        "upload_exact_match.py",
        "upload_final_match.py",
        "upload_final_version.py",
        "upload_fresh_goku.py",
        "upload_goku_comic.py",
        "upload_html_fragment.py",
        "upload_preview_style.py",
        "upload_simple_html.py",
        "upload_styled_version.py",
        "upload_with_template.py",

        # 其他临时文件
        "compare_html.py",
        "list_drafts.py",
        "generate_html_preview.py",
    ]

    # 首先创建backup目录
    backup_dir = project_dir / "_backup"
    if not backup_dir.exists():
        backup_dir.mkdir()
        logger.info(f"✓ 创建备份目录: {backup_dir}")

    # 移动文件到backup而不是删除
    moved_count = 0
    for filename in files_to_delete:
        file_path = project_dir / filename
        if file_path.exists():
            import shutil
            try:
                shutil.move(str(file_path), str(backup_dir / filename))
                logger.info(f"  → {filename} (已移到_backup)")
                moved_count += 1
            except Exception as e:
                logger.error(f"  ✗ {filename} 移动失败: {e}")

    print(f"\n✅ 清理完成！已移动 {moved_count} 个文件到 _backup 目录")

    # 显示保留的文件
    print("\n📂 保留的核心文件：")
    print("="*70)

    core_files = [
        ("系统核心", ["config.py", "main.py"]),
        ("自动化流程", ["full_auto_workflow.py"]),
        ("API客户端", ["api_clients/glm_client.py", "api_clients/jimeng_client.py", "api_clients/wechat_client.py"]),
        ("工具模块", ["utils/image_utils.py"]),
        ("文档", ["README.md", "STYLE_STANDARD.md"]),
    ]

    for category, files in core_files:
        print(f"\n{category}:")
        for f in files:
            if (project_dir / f).exists():
                print(f"  ✓ {f}")

    # 显示backup目录的内容
    backup_files = list(backup_dir.glob("*"))
    if backup_files:
        print(f"\n📦 _backup 目录中的文件（可随时删除）：")
        for f in backup_files:
            print(f"  - {f.name}")

    print("\n💡 提示：")
    print("1. 核心文件已保留")
    print("2. 临时文件已移到 _backup 目录")
    print("3. 如果确认不需要，可以手动删除 _backup 目录")
    print(f"4. 运行命令: cd \"{project_dir}\" && rm -rf _backup")

    # 清理output目录中的临时文件
    print("\n🧹 清理output目录...")
    output_dir = project_dir / "output"

    # 保留的文件
    keep_output_files = [
        "final_article.html",  # 最新的预览
        "wuko_script.json",   # 最新剧本
        "four_panel_combined.png",  # 拼接图
    ]

    # 移动其他文件到backup
    for item in output_dir.iterdir():
        if item.is_file() and item.name not in keep_output_files:
            try:
                import shutil
                shutil.move(str(item), str(backup_dir / item.name))
                logger.info(f"  → {item.name} (已移到_backup)")
            except:
                pass

    print("✓ output目录清理完成")


if __name__ == "__main__":
    clean_project()
