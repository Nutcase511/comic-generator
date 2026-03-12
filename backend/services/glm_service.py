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
            character_name = character_info.get('name', '自定义角色')
            character_description = character_info.get('description', '')
            character_source = character_info.get('source', '')
            prompt_keywords = character_info.get('prompt_keywords', '')

            parts.append("=" * 60)
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【重要：角色替换指令 - 必须严格遵守】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("=" * 60)
            parts.append("")
            parts.append("【目标角色】")
            parts.append(f"角色名称：{character_name}")
            parts.append(f"角色来源：{character_source}")
            parts.append(f"角色描述：{character_description}")
            if prompt_keywords:
                parts.append(f"角色特征：{prompt_keywords}")
            parts.append("")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【强制要求 - 违反即视为任务失败】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("")
            parts.append("1. 【必须】将原始文案中的所有角色（如李小白、小明等）替换为【" + character_name + "】")
            parts.append("2. 【必须】在生成的JSON剧本中，characters字段只能包含【" + character_name + "】")
            parts.append("3. 【必须】在dialogue（对话）中，也必须使用【" + character_name + "】作为说话者")
            parts.append("4. 【必须】每个visual_prompt都必须以【" + character_name + "】开头，详细描述其外貌")
            parts.append("5. 【禁止】保留原始文案中的任何其他角色名称")
            parts.append("6. 【禁止】创造新的角色名称")
            parts.append("")
            parts.append("=" * 60)
            parts.append("")

        # 添加原始文案
        parts.append("【原始四格漫画文案（需要替换角色）】")
        parts.append(paste_text)
        parts.append("")
        parts.append("【注意】以上文案中的角色名只是示例，必须替换为【" + (character_info.get('name', '指定角色') if character_info else '目标角色') + "】")
        parts.append("")

        # 添加指令
        parts.append("")
        parts.append("=" * 60)
        parts.append("【创作要求】")
        parts.append("=" * 60)
        parts.append("1. 基于原始文案的情节结构，生成一个完整的四格漫画剧本JSON")
        parts.append("2. 保持原始文案的对话内容，但【必须】将所有角色替换为指定角色")
        parts.append("3. scene_description和character_actions中也【必须】使用指定角色")
        parts.append("4. 确保输出格式符合四格漫画的标准JSON格式")
        if character_info:
            parts.append("")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【最关键检查点】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append(f"- 所有dialogue中是否只有【{character_name}】在说话？")
            parts.append(f"- 所有visual_prompt是否都以【{character_name}】开头？")
            parts.append(f"- characters数组是否只包含【{character_name}】？")
            parts.append("=" * 60)

        return "\n".join(parts)

    def _build_prompt_for_copywriting(self, copywriting_text: str, character_info: dict) -> str:
        """为文案生成模式构建提示词"""
        parts = []

        # 添加角色信息（如果有）
        if character_info:
            character_name = character_info.get('name', '自定义角色')
            character_description = character_info.get('description', '')
            character_source = character_info.get('source', '')
            prompt_keywords = character_info.get('prompt_keywords', '')

            parts.append("=" * 60)
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【重要：指定角色信息 - 必须使用此角色】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("=" * 60)
            parts.append("")
            parts.append("【目标角色】")
            parts.append(f"角色名称：{character_name}")
            parts.append(f"角色来源：{character_source}")
            parts.append(f"角色描述：{character_description}")
            if prompt_keywords:
                parts.append(f"角色特征：{prompt_keywords}")
            parts.append("")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【强制要求 - 违反即视为任务失败】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("")
            parts.append(f"1. 【必须】使用【{character_name}】作为剧本的唯一主角")
            parts.append(f"2. 【必须】在生成的JSON剧本中，characters字段必须包含【{character_name}】")
            parts.append(f"3. 【必须】所有dialogue（对话）必须由【{character_name}】说出")
            parts.append(f"4. 【必须】每个visual_prompt都必须以【{character_name}】开头")
            parts.append("5. 【禁止】创造或使用其他角色名称")
            parts.append("")
            parts.append("=" * 60)
            parts.append("")

        # 添加文案内容
        parts.append("【文案内容】")
        parts.append(copywriting_text)
        parts.append("")

        # 添加指令
        parts.append("")
        parts.append("=" * 60)
        parts.append("【创作要求】")
        parts.append("=" * 60)
        parts.append("1. 基于以上文案内容，生成一个完整的四格漫画剧本JSON")
        parts.append("2. 将文案内容转换为标准的四格漫画剧本格式")
        parts.append("3. 包含场景描述、角色动作、对话和visual_prompt")
        parts.append("4. 保持文案的核心思想和幽默感")
        if character_info:
            parts.append("")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append("【最关键检查点】")
            parts.append("【【【【【【【【【【【【【【【【【【【【【【【【【【【【")
            parts.append(f"- 对话中是否只有【{character_name}】在说话？")
            parts.append(f"- visual_prompt是否都以【{character_name}】开头？")
            parts.append(f"- 画面中是否清晰展现了【{character_name}】的特征？")
            parts.append("=" * 60)

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
