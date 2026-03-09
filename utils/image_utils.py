"""
图片处理工具
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Tuple
import os


class ImageCombiner:
    """图片拼接工具"""

    @staticmethod
    def create_four_panel_grid(
        image_paths: List[Path],
        output_path: Path,
        panel_size: Tuple[int, int] = (512, 512),
        gap: int = 10,
        background_color: str = "white"
    ) -> Path:
        """
        创建2x2四格漫画拼接图

        Args:
            image_paths: 4张图片路径
            output_path: 输出路径
            panel_size: 每格的尺寸
            gap: 格子之间的间距
            background_color: 背景颜色

        Returns:
            拼接后的图片路径
        """
        if len(image_paths) != 4:
            raise ValueError("必须提供4张图片")

        # 计算总尺寸
        total_width = panel_size[0] * 2 + gap * 3
        total_height = panel_size[1] * 2 + gap * 3

        # 创建新图片
        combined = Image.new("RGB", (total_width, total_height), background_color)

        # 定义4个格子的位置
        positions = [
            (gap, gap),  # 左上
            (panel_size[0] + gap * 2, gap),  # 右上
            (gap, panel_size[1] + gap * 2),  # 左下
            (panel_size[0] + gap * 2, panel_size[1] + gap * 2)  # 右下
        ]

        # 粘贴每张图片
        for i, (img_path, pos) in enumerate(zip(image_paths, positions)):
            img = Image.open(img_path)
            img = img.resize(panel_size, Image.Resampling.LANCZOS)
            combined.paste(img, pos)

            # 添加格数编号
            draw = ImageDraw.Draw(combined)
            number = str(i + 1)

            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            # 在左上角绘制编号
            text_x = pos[0] + 20
            text_y = pos[1] + 20
            draw.text((text_x, text_y), number, fill="white", font=font)

        # 保存拼接图
        output_path.parent.mkdir(parents=True, exist_ok=True)
        combined.save(output_path, "PNG", quality=95)

        return output_path

    @staticmethod
    def add_text_to_image(
        image_path: Path,
        text: str,
        output_path: Path,
        position: str = "bottom",
        font_size: int = 30,
        text_color: str = "black",
        background_color: str = "white"
    ) -> Path:
        """
        在图片上添加文字

        Args:
            image_path: 图片路径
            text: 要添加的文字
            output_path: 输出路径
            position: 文字位置 (top, bottom)
            font_size: 字体大小
            text_color: 文字颜色
            background_color: 背景颜色

        Returns:
            输出路径
        """
        img = Image.open(image_path)
        width, height = img.size

        # 创建新图片，增加高度用于显示文字
        new_height = height + font_size + 40
        new_img = Image.new("RGB", (width, new_height), background_color)

        # 粘贴原图
        if position == "top":
            new_img.paste(img, (0, font_size + 20))
            text_y = 10
        else:  # bottom
            new_img.paste(img, (0, 0))
            text_y = height + 20

        # 添加文字
        draw = ImageDraw.Draw(new_img)

        try:
            font = ImageFont.truetype("simsun.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2

        draw.text((text_x, text_y), text, fill=text_color, font=font)

        # 保存图片
        output_path.parent.mkdir(parents=True, exist_ok=True)
        new_img.save(output_path, "PNG", quality=95)

        return output_path

    @staticmethod
    def resize_image(
        image_path: Path,
        output_path: Path,
        max_size: Tuple[int, int] = (1024, 1024)
    ) -> Path:
        """
        调整图片大小（保持宽高比）

        Args:
            image_path: 图片路径
            output_path: 输出路径
            max_size: 最大尺寸

        Returns:
            输出路径
        """
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG", quality=95)

        return output_path
