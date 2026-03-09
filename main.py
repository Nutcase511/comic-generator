#!/usr/bin/env python3
"""
四格漫画自动生成器 - 主程序（使用完整自动化流程）

🎨 样式标准: 基于 output/preview.html
🔧 自动化流程: GLM-4生成剧本 -> 即梦AI生成漫画 -> 微信公众号发布
"""
import sys
from pathlib import Path
from loguru import logger

from config import config
from api_clients import glm_client, jimeng_client, wechat_client
from utils import ImageCombiner


def setup_logger():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    logger.add(
        config.LOG_DIR / "comic_generator_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG"
    )


def validate_config():
    """验证配置"""
    errors = config.validate()
    if errors:
        logger.error("❌ 配置错误：")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("\n请在.env文件中配置必要的API密钥")
        return False
    return True


def generate_comic(user_input: str, style: str = "cute"):
    """
    生成四格漫画（完整自动化流程）

    Args:
        user_input: 用户输入的主题
        style: 漫画风格 (cute/anime/simple)

    Returns:
        生成结果字典
    """
    result = {
        "script": None,
        "separate_images": [],
        "combined_image": None,
        "wechat_media_id": None
    }

    try:
        # 步骤1: 使用GLM-4生成剧本
        logger.info("\n步骤1/5: 使用GLM-4生成剧本...")
        script = glm_client.generate_comic_script(user_input, style=style)
        result["script"] = script
        logger.info(f"✓ 剧本生成完成：{script.get('title')}")
        logger.info(f"✓ 包含{len(script.get('panels', []))}个场景，每个场景都有visual_prompt")

        # 步骤2: 提取画面描述
        logger.info("\n步骤2/5: 提取画面描述...")
        visual_prompts = [panel.get("visual_prompt", "") for panel in script.get("panels", [])]
        logger.info(f"✓ 已提取{len(visual_prompts)}个场景描述")

        # 步骤3: 使用即梦AI生成漫画
        logger.info("\n步骤3/5: 使用即梦AI生成漫画...")
        base_seed = hash(user_input) % 10000

        separate_images = jimeng_client.generate_four_panel_comic(
            prompts=visual_prompts,
            style=style,
            base_seed=base_seed
        )
        result["separate_images"] = separate_images
        logger.info("✓ 单独图片生成完成")

        # 步骤4: 生成拼接图
        logger.info("\n步骤4/5: 生成拼接四格漫画...")
        combined_path = config.OUTPUT_DIR / "four_panel_combined.png"
        ImageCombiner.create_four_panel_grid(separate_images, combined_path)
        result["combined_image"] = combined_path
        logger.info(f"✓ 拼接图已保存: {combined_path}")

        # 步骤5: 上传到微信公众号草稿箱
        logger.info("\n步骤5/5: 上传到微信公众号草稿箱...")

        # 上传图片到微信素材库
        logger.info("  正在上传图片到微信素材库...")
        image_urls = []
        for i, image_path in enumerate(separate_images, 1):
            logger.info(f"    上传第{i}张图片...", end='', flush=True)
            media_id, img_url = wechat_client.upload_image_with_url(str(image_path))
            image_urls.append(img_url)
            logger.info(f" ✓")

        # 生成HTML内容并上传
        media_id = wechat_client.create_comic_article(
            title=script.get("title", "AI生成的四格漫画"),
            script_data=script,
            image_paths=[str(combined_path)],
            author="AI"
        )
        result["wechat_media_id"] = media_id
        logger.info(f"✓ 已上传到草稿箱，Media ID: {media_id}")

        return result

    except Exception as e:
        logger.error(f"❌ 生成失败: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        raise


def main():
    """主函数"""
    # 打印欢迎信息
    print("""
╔════════════════════════════════════════╗
║  🎨 四格漫画自动生成器 v2.0           ║
║  AI-Powered Four-Panel Comic Generator ║
║  基于 preview.html 样式标准            ║
╚════════════════════════════════════════╝
    """)

    # 配置日志
    setup_logger()

    # 验证配置
    if not validate_config():
        sys.exit(1)

    # 获取用户输入
    user_input = input("\n✍️  请输入你想要转换成漫画的文字（例如：一个关于拖延症的搞笑故事）：\n> ").strip()

    if not user_input:
        logger.warning("⚠️  输入不能为空")
        sys.exit(1)

    # 选择风格
    print("\n🎨 请选择漫画风格：")
    styles = list(config.COMIC_STYLES.keys())
    style_names = {
        "cute": "可爱Q版",
        "anime": "日漫风格",
        "simple": "简笔画"
    }

    for i, style in enumerate(styles, 1):
        logger.info(f"  {i}. {style_names[style]} - {config.COMIC_STYLES[style]}")

    while True:
        try:
            choice = input("\n请输入选项 (1-3, 默认1): ").strip() or "1"
            index = int(choice) - 1
            if 0 <= index < len(styles):
                selected_style = styles[index]
                logger.info(f"✓ 已选择：{style_names[selected_style]}")
                break
            else:
                logger.warning("⚠️  无效选项，请重新输入")
        except ValueError:
            logger.warning("⚠️  请输入数字")

    # 生成漫画
    try:
        result = generate_comic(user_input, style=selected_style)

        # 显示结果
        logger.info("\n" + "="*70)
        logger.info("🎉 生成完成！")
        logger.info("="*70)
        logger.info(f"📖 剧本标题: {result['script'].get('title')}")
        logger.info(f"👥 角色数量: {len(result['script'].get('characters', []))}")
        logger.info(f"🎨 场景数量: {len(result['script'].get('panels', []))}")
        logger.info(f"📊 生成了 {len(result['separate_images'])} 张单独图片")

        if result['combined_image']:
            logger.info(f"🖼️  拼接图: {result['combined_image']}")

        logger.info(f"📱 已保存到公众号草稿箱")
        logger.info(f"\n💡 提示：登录微信公众号后台查看草稿箱")
        logger.info(f"   样式标准：完全基于 preview.html")
        logger.info(f"   包含内容：漫画、角色、剧情、AI创作揭秘、理念")

    except Exception as e:
        logger.error(f"\n❌ 程序异常退出: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

