"""
GLM-4服务层
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loguru import logger


class GLMService:
    """GLM-4服务"""

    def __init__(self):
        # 延迟导入避免初始化问题
        self.client = None

    def _get_client(self):
        """获取客户端实例"""
        if self.client is None:
            from api_clients import glm_client
            self.client = glm_client
        return self.client

    async def generate_comic_script(
        self,
        user_input: str,
        style: str = "cute",
        character_info: dict = None,
        input_type: str = "topic"
    ) -> dict:
        """
        生成四格漫画剧本

        Args:
            user_input: 用户输入
            style: 风格
            character_info: 角色信息
            input_type: 输入类型

        Returns:
            剧本数据字典
        """
        try:
            if input_type == "paste":
                # 粘贴文案模式：需要解析文案并指定角色
                prompt = self._build_prompt_for_paste(user_input, character_info)
            elif input_type == "copywriting":
                # 文案生成模式：需要将文案转换为剧本格式
                prompt = self._build_prompt_for_copywriting(user_input, character_info)
            else:
                # 主题模式：正常生成
                prompt = user_input

            # 在线程池中运行同步代码
            loop = asyncio.get_event_loop()
            client = self._get_client()

            # 调用GLM-4生成，传递character_info参数
            script_data = await loop.run_in_executor(
                None,
                lambda: client.generate_comic_script(
                    user_input=prompt,
                    style=style,
                    character_info=character_info
                )
            )

            return script_data

        except Exception as e:
            logger.error(f"生成剧本失败: {e}")
            raise

    def _build_prompt_for_paste(self, paste_text: str, character_info: dict) -> str:
        """为粘贴模式构建提示词"""
        parts = []

        # 添加角色信息（如果有）
        if character_info:
            parts.append("=" * 50)
            parts.append("【重要：指定角色信息】")
            parts.append("=" * 50)
            parts.append(f"角色名称：{character_info.get('name', '自定义角色')}")
            parts.append(f"角色描述：{character_info.get('description', '')}")
            parts.append(f"角色来源：{character_info.get('source', '')}")
            if 'prompt_keywords' in character_info:
                parts.append(f"角色特征关键词：{character_info.get('prompt_keywords', '')}")
            parts.append("=" * 50)
            parts.append("")
            parts.append("【要求】")
            parts.append("- 将原始文案中的角色替换为上述指定的角色")
            parts.append("- 在每个画面的visual_prompt中详细描述角色的外貌、表情和动作")
            parts.append("- 如果角色有标志性物品（如金箍棒、战甲等），必须在画面中体现")
            parts.append("=" * 50)
            parts.append("")

        # 添加原始文案
        parts.append("【原始四格漫画文案】")
        parts.append(paste_text)
        parts.append("")

        # 添加指令
        parts.append("")
        parts.append("【创作要求】")
        parts.append("1. 基于原始文案生成一个完整的四格漫画剧本")
        parts.append("2. 保持原始文案的对话内容和情节结构")
        parts.append("3. 确保输出格式符合四格漫画的标准JSON格式")
        if character_info:
            parts.append("4. 【最关键】所有格的画面都必须包含指定角色，替换原角色")
            parts.append("5. visual_prompt中必须详细描述指定角色的外貌、表情、动作和服装特征")

        return "\n".join(parts)

    def _build_prompt_for_copywriting(self, copywriting_text: str, character_info: dict) -> str:
        """为文案生成模式构建提示词"""
        parts = []

        # 添加角色信息（如果有）
        if character_info:
            parts.append("=" * 50)
            parts.append("【重要：指定角色信息】")
            parts.append("=" * 50)
            parts.append(f"角色名称：{character_info.get('name', '自定义角色')}")
            parts.append(f"角色描述：{character_info.get('description', '')}")
            parts.append(f"角色来源：{character_info.get('source', '')}")
            if 'prompt_keywords' in character_info:
                parts.append(f"角色特征关键词：{character_info.get('prompt_keywords', '')}")
            parts.append("=" * 50)
            parts.append("")
            parts.append("【要求】")
            parts.append("- 必须使用上述指定的角色作为主角")
            parts.append("- 在每个画面的visual_prompt中详细描述角色的外貌、表情和动作")
            parts.append("- 如果角色有标志性物品（如金箍棒、战甲等），必须在画面中体现")
            parts.append("=" * 50)
            parts.append("")

        # 添加文案内容
        parts.append("【文案内容】")
        parts.append(copywriting_text)
        parts.append("")

        # 添加指令
        parts.append("")
        parts.append("【创作要求】")
        parts.append("1. 基于以上文案内容，生成一个完整的四格漫画剧本")
        parts.append("2. 将文案内容转换为标准的四格漫画剧本格式，包含场景描述、角色动作和对话")
        parts.append("3. 保持文案的核心思想和幽默感，让剧本适合漫画呈现")
        parts.append("4. 确保输出格式符合四格漫画的标准JSON格式")
        if character_info:
            parts.append("5. 【最关键】所有格的画面都必须包含指定角色，并详细描述其特征")

        return "\n".join(parts)

    async def generate_copywriting_options(self, topic: str) -> list:
        """
        生成文案选项

        Args:
            topic: 主题

        Returns:
            文案选项列表
        """
        try:
            # 在线程池中运行同步代码
            loop = asyncio.get_event_loop()
            client = self._get_client()

            # 构建提示词
            prompt = self._build_copywriting_prompt(topic)

            # 调用GLM-4生成
            copywriting_options = await loop.run_in_executor(
                None,
                lambda: client.generate_copywriting(prompt=prompt)
            )

            return copywriting_options

        except Exception as e:
            logger.error(f"生成文案选项失败: {e}")
            raise

    def _build_copywriting_prompt(self, topic: str) -> str:
        """构建文案生成提示词"""
        prompt = f"""请基于主题"{topic}"，生成3-5个不同角度的四格漫画文案。

【风格要求】
- 社会观察：关注日常现象背后的深层逻辑
- 深度思考：引发读者反思，带有哲学意味
- 讽刺幽默：用幽默揭示问题本质
- 点睛之笔：每篇结尾有一句升华主题的旁白

【格式要求】
每个文案包含：标题 + 四格内容 + 文案旁白

【参考示例】
示例一：信息茧房
第一格：用户手指快速滑动屏幕，面无表情
第二格：屏幕上出现各种相似内容的推荐
第三格：用户试图搜索不同观点，却被算法引导回原有观点
第四格：学生的脑袋变成了一个只有单一颜色的方块
文案旁白："算法在探索你的边界，也在固化你的边界；你以为在开阔视野，其实是在重复昨天。"

【输出格式】
JSON数组：
[
  {{
    "id": "1",
    "title": "文案标题",
    "content": "第一格：...\\n第二格：...\\n第三格：...\\n第四格：...\\n文案旁白：...",
    "tags": ["标签1", "标签2"]
  }}
]"""
        return prompt
