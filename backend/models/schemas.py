"""
Pydantic模型（API请求和响应）
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ==================== 请求模型 ====================

class GenerateScriptRequest(BaseModel):
    """生成剧本请求"""
    input_type: Literal["topic", "paste", "copywriting"] = Field(..., description="输入类型：topic(主题模式), paste(粘贴文案), copywriting(文案生成)")
    input_text: str = Field(..., description="输入内容：主题或文案")
    character_id: Optional[str] = Field(None, description="预制角色ID")
    custom_character: Optional[str] = Field(None, description="自定义角色名称和描述")
    style: str = Field("cute", description="风格：cute(可爱Q版), funny(搞笑), 等")


class GenerateImagesRequest(BaseModel):
    """生成图片请求"""
    script_data: dict = Field(..., description="剧本数据")


class PublishToWechatRequest(BaseModel):
    """发布到微信请求"""
    script_data: dict = Field(..., description="剧本数据")
    image_urls: List[str] = Field(..., description="图片URL列表")


# ==================== 响应模型 ====================

class ScriptData(BaseModel):
    """剧本数据"""
    title: str
    panels: List[dict]
    characters: List[dict]
    script_generation_prompt: str
    character_generation_prompt: str


class GenerateScriptResponse(BaseModel):
    """生成剧本响应"""
    success: bool
    message: str
    data: Optional[ScriptData] = None


class Character(BaseModel):
    """预制角色"""
    id: str
    name: str
    source: str
    source_type: str
    description: str
    prompt_keywords: str


class CharactersResponse(BaseModel):
    """角色列表响应"""
    success: bool
    data: List[Character]


class ImageGenerationProgress(BaseModel):
    """图片生成进度"""
    panel_number: int
    status: str  # generating, completed, error
    progress: int
    image_url: Optional[str] = None
    error: Optional[str] = None


class GenerateImagesResponse(BaseModel):
    """生成图片响应"""
    success: bool
    message: str
    data: Optional[List[str]] = None  # 图片URL列表


class PublishToWechatResponse(BaseModel):
    """发布到微信响应"""
    success: bool
    message: str
    media_id: Optional[str] = None
    draft_url: Optional[str] = None


class HistoryItem(BaseModel):
    """历史记录项"""
    id: int
    created_at: str
    title: str
    input_type: str
    character_name: Optional[str] = None
    wechat_media_id: Optional[str] = None
    published_at: Optional[str] = None


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    success: bool
    total: int
    data: List[HistoryItem]


class HistoryDetailResponse(BaseModel):
    """历史记录详情响应"""
    success: bool
    data: Optional[dict] = None


# ==================== 文案生成相关模型 ====================

class GenerateCopywritingRequest(BaseModel):
    """生成文案选项请求"""
    topic: str = Field(..., description="主题：预设主题ID或自定义主题文本")


class CopywritingOption(BaseModel):
    """文案选项"""
    id: str
    title: str
    content: str
    tags: List[str] = []


class GenerateCopywritingResponse(BaseModel):
    """生成文案选项响应"""
    success: bool
    message: str
    data: Optional[List[CopywritingOption]] = None


class CopywritingTopic(BaseModel):
    """文案主题"""
    id: str
    name: str
    description: str


class CopywritingTopicsResponse(BaseModel):
    """文案主题列表响应"""
    success: bool
    data: List[CopywritingTopic]
