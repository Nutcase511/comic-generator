"""
智谱AI API客户端
"""
import json
from typing import Dict, List, Optional
from zhipuai import ZhipuAI
from config import config


class GLMClient:
    """智谱GLM-4客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.ZHIPU_API_KEY
        self.client = ZhipuAI(api_key=self.api_key)

    def generate_comic_script(
        self,
        user_input: str,
        style: str = "cute",
        num_panels: int = 4,
        character_info: dict = None,
        series_characters: list = None
    ) -> Dict:
        """
        生成四格漫画剧本

        Args:
            user_input: 用户输入的文字
            style: 漫画风格
            num_panels: 格数（默认4格）
            character_info: 角色信息（可选）
            series_characters: 同系列的其他角色（可作为配角）

        Returns:
            包含剧本信息的字典
        """
        style_desc = config.get_style_prompt(style)

        # 构建角色描述部分
        character_desc = ""
        character_series = ""
        supporting_characters_desc = ""

        if character_info:
            character_name = character_info.get('name', '自定义角色')
            character_description = character_info.get('description', '')
            character_source = character_info.get('source', '')
            character_series = character_info.get('series', '')
            prompt_keywords = character_info.get('prompt_keywords', '')

            character_desc = f"""

【必须严格遵守的角色要求】
======================================================
角色：{character_name}（来自：{character_series}）
角色外貌：{character_description}
{f'关键词：{prompt_keywords}' if prompt_keywords else ''}
======================================================

【最关键的要求】
1. 每一格的画面中心必须是 {character_name}
2. {character_name} 必须占据画面的主要位置（至少50%）
3. 必须清晰展现 {character_name} 的面部特征和表情
4. {character_name} 的服装、发型、标志性物品必须准确呈现
5. 画面风格不能改变角色的基本特征
6. 如果是孙悟空：必须有金箍棒、金色的毛发、虎皮裙
7. 如果是钢铁侠：必须有红金色的战甲、反应堆
8. 如果是路飞：必须有草帽、红色坎肩、短裤

在下面的每个visual_prompt中，都要以"{character_name}在做什么动作、什么表情"作为开头！"""

            # 如果有同系列的其他角色，添加配角说明
            if series_characters and len(series_characters) > 0:
                supporting_characters_desc = f"""

【配角选择规则 - 必须遵守】
======================================================
如果剧本中需要其他角色作为配角（如路人、朋友、对手等）：
- 【必须】从【{character_series}】系列中选择
- 【禁止】使用其他系列的角色
- 【禁止】创造不存在的角色名称

【{character_series}】系列可选配角（最多3个）：
{chr(10).join([f"- {idx+1}. {c.get('name')}: {c.get('description', '')[:50]}" for idx, c in enumerate(series_characters[:6])])}
======================================================

【重要】：
- 配角的作用是辅助主角，不应抢戏
- 如果不需要配角，可以只使用主角一个人
- 选择配角时，优先选择该系列中最知名的角色"""

        prompt = f"""你是一位专业的四格漫画编剧。请根据用户输入的文字，创作一个爆笑四格漫画剧本。

用户输入：{user_input}{character_desc}{supporting_characters_desc}

要求：
1. 创作一个{num_panels}格漫画的剧本
2. 风格：{style_desc}
3. 每格要有：画面描述、角色动作、对话/旁白
4. 剧情要搞笑、有梗、有反转
5. 对话要简洁，适合漫画呈现
6. {'使用指定的角色及其特征' if character_info else '设定1-2个主要角色，描述他们的外貌特征'}
7. **所有格的画面描述（visual_prompt）中都必须包含指定的角色，并详细描述角色的外貌、表情、动作和服装**{'''
8. 如果需要配角，必须从【{character_series}】系列中选择（见上方的配角列表）''' if series_characters and character_series else ''}
9. {"禁止创造随机角色名称，必须使用指定系列的角色" if series_characters else "设定合理的角色名称"}

请以JSON格式返回，格式如下：
{{
    "title": "漫画标题",
    "characters": [
        {{
            "name": "角色名",
            "description": "角色外观描述"
        }}
    ],
    "panels": [
        {{
            "panel_number": 1,
            "scene_description": "场景描述",
            "character_actions": "角色动作",
            "dialogue": "对话/旁白",
            "visual_prompt": "{'孙悟空，金色的毛发，头戴金箍，手持金箍棒，穿着虎皮裙，[表情]在[场景][做动作]，高清细节' if character_info and character_info.get('name') == '孙悟空' else '钢铁侠，红金色的战甲，胸口的反应堆发光，[表情]在[场景][做动作]，科技感' if character_info and character_info.get('name') == '钢铁侠' else character_info.get('name', '角色') + '，' + character_info.get('description', '具体外貌描述') + '，[表情]在[场景][做动作]' if character_info else '主要角色的详细外貌描述，表情、动作、服装，场景细节'}"
        }}
    ],
    "script_generation_prompt": "总结你生成这个剧本时使用的提示词",
    "character_generation_prompt": "总结角色设计时使用的提示词"
}}

【关键提醒】：
- visual_prompt的每一个字都至关重要，决定了图片生成的效果
- 每个visual_prompt都必须以角色名称开头
- 描述要具体：不要说"一个人"，而要说"{character_info.get('name', '角色名称') if character_info else '角色名称'}，穿着[什么服装]，[什么表情]，在[做什么动作]"
- 如果角色有标志性物品（金箍棒、战甲、草帽等），必须在每个visual_prompt中提及
- {"visual_prompt长度要超过100字，包含角色、服装、表情、动作、场景、光线、构图等所有细节" if character_info else "visual_prompt要详细，包含所有必要信息"}
- {"如果需要配角，必须从【"+character_series+"】系列中选择，禁止使用其他系列的角色" if series_characters and character_series else ""}"""

        try:
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的四格漫画编剧，擅长创作搞笑、有反转的剧情。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # 尝试解析JSON
            # 如果内容被markdown代码块包裹，需要提取
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            script_data = json.loads(content)
            return script_data

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始内容: {content}")
            raise
        except Exception as e:
            print(f"调用GLM-4失败: {e}")
            raise

    def refine_script(
        self,
        script: Dict,
        feedback: str
    ) -> Dict:
        """
        根据反馈优化剧本

        Args:
            script: 原始剧本
            feedback: 用户反馈

        Returns:
            优化后的剧本
        """
        prompt = f"""请根据以下反馈优化四格漫画剧本：

原始剧本：
{json.dumps(script, ensure_ascii=False, indent=2)}

用户反馈：
{feedback}

请返回优化后的完整JSON剧本，保持相同的格式。"""

        try:
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位专业的四格漫画编剧。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            refined_script = json.loads(content)
            return refined_script

        except Exception as e:
            print(f"优化剧本失败: {e}")
            raise

    def generate_copywriting(
        self,
        prompt: str
    ) -> List[Dict]:
        """
        生成文案选项

        Args:
            prompt: 文案生成提示词

        Returns:
            文案选项列表
        """
        try:
            response = self.client.chat.completions.create(
                model=config.ZHIPU_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的四格漫画编剧，擅长创作深度思考风格的社会观察文案。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2500
            )

            content = response.choices[0].message.content

            # 尝试解析JSON
            # 如果内容被markdown代码块包裹，需要提取
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # 清理可能的数组标记
            content = content.strip()
            if content.startswith('[') and content.endswith(']'):
                copywriting_options = json.loads(content)
            else:
                # 尝试提取JSON数组
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    copywriting_options = json.loads(json_match.group())
                else:
                    raise ValueError("无法从响应中提取JSON数组")

            return copywriting_options

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始内容: {content}")
            raise
        except Exception as e:
            print(f"生成文案失败: {e}")
            raise


# 创建全局实例
glm_client = GLMClient()
