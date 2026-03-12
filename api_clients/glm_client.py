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
        num_panels: int = 4
    ) -> Dict:
        """
        生成四格漫画剧本

        Args:
            user_input: 用户输入的文字
            style: 漫画风格
            num_panels: 格数（默认4格）

        Returns:
            包含剧本信息的字典
        """
        style_desc = config.get_style_prompt(style)

        prompt = f"""你是一位专业的四格漫画编剧。请根据用户输入的文字，创作一个爆笑四格漫画剧本。

用户输入：{user_input}

要求：
1. 创作一个{num_panels}格漫画的剧本
2. 风格：{style_desc}
3. 每格要有：画面描述、角色动作、对话/旁白
4. 剧情要搞笑、有梗、有反转
5. 对话要简洁，适合漫画呈现
6. 设定1-2个主要角色，描述他们的外貌特征

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
            "visual_prompt": "详细的画面描述，用于AI绘画生成"
        }}
    ],
    "script_generation_prompt": "总结你生成这个剧本时使用的提示词",
    "character_generation_prompt": "总结角色设计时使用的提示词"
}}

注意：visual_prompt要非常详细，包含场景、角色表情、动作、构图等，适合直接用于AI绘画生成。"""

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
